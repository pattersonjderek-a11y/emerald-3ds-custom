"""Private source-build bundles and recoverable SD updates for the custom fork.

The public ROM recipe is a different pipeline. This format contains a locally
built pack and must stay private. It never imports another namespace's saves.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import uuid

from .pak import PakReader

APP = 'emerald3ds-custom-stage-f-v050'
RULES = 0x00050050
MANIFEST = 'CUSTOM_INSTALL.json'
FILES = ('Emerald3DS.3dsx', 'Emerald3DS.smdh', 'emerald3ds.pak')
JOURNAL = '.' + APP + '.transaction.json'


class PackageError(ValueError):
    pass


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def engine_romfs(path):
    """Read the raw level-3 RomFS produced by 3dsxtool, with bounded tables."""
    blob = Path(path).read_bytes()
    if len(blob) < 44 or blob[:4] != b'3DSX' or struct.unpack_from('<H', blob, 4)[0] < 44:
        raise PackageError('invalid extended 3DSX header')
    off = struct.unpack_from('<I', blob, 40)[0]
    rom = blob[off:]
    if off < 44 or len(rom) < 40:
        raise PackageError('missing 3DSX RomFS')
    head, dh, dhn, dm, dmn, fh, fhn, fm, fmn, data = struct.unpack_from('<10I', rom)
    if head != 40 or data > len(rom):
        raise PackageError('unsupported RomFS header')
    for start, size in ((dh, dhn), (dm, dmn), (fh, fhn), (fm, fmn)):
        if start < 40 or start + size > data:
            raise PackageError('RomFS table outside metadata')
    files, dirs, visited_files = {}, set(), set()

    def name(start, length, end):
        if length % 2 or start + length > end:
            raise PackageError('invalid RomFS name')
        text = rom[start:start + length].decode('utf-16le')
        if text in ('.', '..') or any(c in text for c in '/\\:\0'):
            raise PackageError('unsafe RomFS name')
        return text

    def directory(index, parent):
        if index in dirs or index + 24 > dmn:
            raise PackageError('cyclic or truncated RomFS directory')
        dirs.add(index)
        _, sibling, child, file_index, _, length = struct.unpack_from('<6I', rom, dm + index)
        leaf = name(dm + index + 24, length, dm + dmn)
        prefix = parent + leaf + '/' if leaf else parent
        while file_index != 0xffffffff:
            if file_index in visited_files or file_index + 32 > fmn:
                raise PackageError('cyclic or truncated RomFS file table')
            visited_files.add(file_index)
            _, next_file, rel, size, _, n = struct.unpack_from('<IIQQII', rom, fm + file_index)
            path = prefix + name(fm + file_index + 32, n, fm + fmn)
            if data + rel + size > len(rom) or path in files:
                raise PackageError('RomFS payload out of bounds or duplicated')
            files[path] = rom[data + rel:data + rel + size]
            file_index = next_file
        while child != 0xffffffff:
            child = directory(child, prefix)
        return sibling

    directory(0, '')
    return files


def validate_bundle(folder):
    folder = Path(folder)
    if folder.is_symlink():
        raise PackageError('bundle must not be a symlink')
    try:
        meta = json.loads((folder / MANIFEST).read_text())
        if not isinstance(meta, dict):
            raise PackageError('install receipt must be an object')
        for key in ('schema', 'save_schema', 'rules', 'engine_abi', 'data_files'):
            if type(meta.get(key)) is not int:
                raise PackageError('invalid integer in install receipt: ' + key)
        if not 0 < meta['engine_abi'] <= 0xffffffff or not 0 < meta['data_files'] <= (1 << 20):
            raise PackageError('invalid ABI or data count')
        if (meta['schema'] != 1 or meta['namespace'] != APP or meta['rules'] != RULES
                or meta['save_schema'] != 1 or meta['private_content_bearing'] is not True):
            raise PackageError('unsupported package, namespace or save rules')
        if not isinstance(meta['files'], dict) or set(meta['files']) != set(FILES):
            raise PackageError('unexpected package file list')
        if {p.name for p in folder.iterdir()} != {*FILES, MANIFEST}:
            raise PackageError('bundle contains unexpected files; state cannot be installed')
        for name in (*FILES, MANIFEST):
            p = folder / name
            if p.is_symlink() or not p.is_file():
                raise PackageError('nonregular bundle file')
        for name in FILES:
            p = folder / name
            if p.stat().st_size != meta['files'][name]['bytes'] or sha(p) != meta['files'][name]['sha256']:
                raise PackageError('file size/hash mismatch: ' + name)
        smdh = (folder / FILES[1]).read_bytes()
        if len(smdh) != 14016 or smdh[:4] != b'SMDH':
            raise PackageError('invalid Homebrew Launcher metadata')
        engine = engine_romfs(folder / FILES[0])
        # An embedded development app or loose-data pack could mask a mismatch.
        if 'data.embedded' in engine or 'gamedata/gamedata.bin' in engine:
            raise PackageError('expected engine-only executable')
        if engine.get('engine/abi.bin') != struct.pack('<I', meta['engine_abi']):
            raise PackageError('executable ABI does not match the manifest')
        executable = (folder / FILES[0]).read_bytes()
        if ('sdmc:/3ds/' + APP + '/').encode() not in executable:
            raise PackageError('executable uses a different namespace')
        for prefix in (b'emerald3ds/', b'pokeemerald/', b'emerald3ds-custom/',
                       b'emerald3ds-custom-stage-b/', b'emerald3ds-custom-stage-c/',
                       b'emerald3ds-custom-stage-d/', b'emerald3ds-custom-stage-e-v050/'):
            if b'sdmc:/3ds/' + prefix in executable:
                raise PackageError('legacy storage path in executable')
        with PakReader(folder / FILES[2]) as reader:
            if reader.abi != meta['engine_abi'] or reader.rom_sha1.hex() != meta['rom_profile_sha1']:
                raise PackageError('pack ABI/profile mismatch')
            if reader.verify() != meta['data_files']:
                raise PackageError('pack entry count mismatch')
        return meta
    except (OSError, KeyError, TypeError, struct.error, UnicodeError, json.JSONDecodeError) as exc:
        raise PackageError('invalid bundle: ' + str(exc)) from exc


def _sync_dir(path):
    # Directory fsync is unavailable on Windows and some mounted SD drivers.
    # File fsync and the persistent recovery journal remain mandatory.
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def _regular_tree(path):
    if path.is_symlink() or not path.is_dir():
        raise PackageError('destination must be a real directory')
    for item in path.rglob('*'):
        if item.is_symlink() or not (item.is_file() or item.is_dir()):
            raise PackageError('refusing nonregular destination entry: ' + str(item))


def _paths(sd):
    sd = Path(sd).absolute()
    for p in (*sd.parents, sd, sd / '3ds'):
        if p.is_symlink() or (p.exists() and not p.is_dir()):
            raise PackageError('unsafe SD root or 3ds directory')
    return sd / '3ds', sd / '3ds' / APP


def _state_snapshot(folder):
    return {p.relative_to(folder).as_posix(): sha(p) for p in folder.rglob('*')
            if p.is_file() and p.relative_to(folder).as_posix() not in
            (*FILES, MANIFEST, '.install-token')}


def recover(sd):
    """Roll back a journaled interrupted install. Never resume a mixed pair."""
    parent, dest = _paths(sd)
    journal = parent / JOURNAL
    if not journal.exists() and not journal.is_symlink():
        return False
    if journal.is_symlink():
        raise PackageError('unsafe recovery journal')
    tx = json.loads(journal.read_text())
    if not isinstance(tx, dict):
        raise PackageError('invalid recovery journal; files preserved')
    token = tx.get('token', '')
    if (type(tx.get('schema')) is not int or tx['schema'] != 1
            or not isinstance(token, str) or not re.fullmatch('[0-9a-f]{32}', token)
            or type(tx.get('had_previous')) is not bool):
        raise PackageError('invalid recovery journal; inspect without changing files')
    stage = parent / ('.' + APP + '.' + token + '.staging')
    backup = parent / ('.' + APP + '.backup-' + token)
    rejected = parent / ('.' + APP + '.rejected-' + token)
    for p in (dest, stage, backup, rejected):
        if p.exists() or p.is_symlink():
            _regular_tree(p)
    current = (dest.exists() and (dest / '.install-token').is_file()
               and (dest / '.install-token').read_text() == token)
    if not tx['had_previous'] and backup.exists():
        raise PackageError('unexpected backup for a first install; files preserved')
    if current:
        if tx['had_previous'] and not backup.exists():
            raise PackageError('recovery backup missing; destination preserved')
        if rejected.exists() or stage.exists():
            raise PackageError('ambiguous pending folders; files preserved')
        # Never recursively delete the live destination while a recovery is
        # pending: interruption could erase its identity marker halfway through.
        # A rename keeps the failed copy inspectable and can be retried safely.
        os.replace(dest, rejected)
        _sync_dir(parent)
    if backup.exists():
        if dest.exists():
            raise PackageError('both previous destination and backup exist; inspect manually')
        os.replace(backup, dest)
        _sync_dir(parent)
    elif tx['had_previous'] and not dest.exists():
        raise PackageError('previous install and backup missing')
    if stage.exists():
        if rejected.exists():
            raise PackageError('both staging and rejected folders exist; files preserved')
        os.replace(stage, rejected)
        _sync_dir(parent)
    journal.unlink()
    _sync_dir(parent)
    return True


def install_bundle(sd, bundle):
    """Validate before writes; stage a full copy; preserve a complete rollback.

    Source state is never loaded from B/C/D/E. For subsequent F updates schema
    and rules must match. Run recover after a disconnect/crash before launching.
    """
    meta = validate_bundle(bundle)
    parent, dest = _paths(sd)
    if (parent / JOURNAL).exists() or (parent / JOURNAL).is_symlink():
        raise PackageError('interrupted update: run recover before installing')
    previous = dest.exists() or dest.is_symlink()
    if previous:
        _regular_tree(dest)
        # Loose-data overrides have higher priority than the pack in the game.
        if any((dest / n).exists() for n in ('devdata', '.emerald3ds-dev')):
            raise PackageError('remove loose development-data overrides before updating')
        try:
            old = json.loads((dest / MANIFEST).read_text())
        except (OSError, ValueError) as exc:
            raise PackageError('existing folder has no valid F install receipt; refusing import') from exc
        if (not isinstance(old, dict)
                or any(type(old.get(k)) is not int for k in ('schema', 'save_schema', 'rules'))
                or any(old.get(k) != meta[k] for k in ('schema', 'namespace', 'save_schema', 'rules'))):
            raise PackageError('save rules changed; use a separate namespace')
    # Snapshot every user file, not just the executable/pack. A same-length
    # damaged copy of settings or a save must abort before the old folder moves.
    state = _state_snapshot(dest) if previous else {}
    receipt_sha = sha(Path(bundle) / MANIFEST)
    parent.mkdir(parents=True, exist_ok=True)
    need = sum(p.stat().st_size for p in Path(bundle).iterdir())
    if previous:
        need += sum(p.stat().st_size for p in dest.rglob('*') if p.is_file())
    if shutil.disk_usage(parent).free < need + (4 << 20):
        raise PackageError('insufficient free space to stage a complete install')
    token = uuid.uuid4().hex
    stage = parent / ('.' + APP + '.' + token + '.staging')
    backup = parent / ('.' + APP + '.backup-' + token)
    journal = parent / JOURNAL
    # Reserve the journal exclusively to serialize installers and recovery.
    fd = os.open(journal, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump({'schema': 1, 'token': token, 'had_previous': previous}, f)
            f.flush()
            os.fsync(f.fileno())
        _sync_dir(parent)
        if previous:
            shutil.copytree(dest, stage)
        else:
            stage.mkdir()
        for name in (*FILES, MANIFEST):
            shutil.copyfile(Path(bundle) / name, stage / name)
        (stage / '.install-token').write_text(token)
        for p in stage.rglob('*'):
            if p.is_file():
                with p.open('rb') as f:
                    os.fsync(f.fileno())
        # Read back the staged managed files before renaming either directory.
        for name in FILES:
            if sha(stage / name) != meta['files'][name]['sha256']:
                raise PackageError('staged file changed: ' + name)
        if sha(stage / MANIFEST) != receipt_sha:
            raise PackageError('staged install receipt changed')
        if _state_snapshot(stage) != state or (previous and _state_snapshot(dest) != state):
            raise PackageError('user state changed or was corrupted while staging')
        _sync_dir(stage)
        if previous:
            os.replace(dest, backup)
            _sync_dir(parent)
        os.replace(stage, dest)
        _sync_dir(parent)
        journal.unlink()
        _sync_dir(parent)
    except Exception:
        # If recovery itself fails, keep the journal and report the original
        # error. A later explicit recovery can retry with the card reinserted.
        try:
            recover(sd)
        except Exception:
            pass
        raise
    return {'destination': str(dest), 'backup': str(backup) if previous else None,
            'engine_abi': meta['engine_abi'], 'hardware_tested': False}
