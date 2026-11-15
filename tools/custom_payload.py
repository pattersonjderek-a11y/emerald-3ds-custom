#!/usr/bin/env python3
"""Build/verify a PRIVATE custom source-data bundle, or install/recover it.

No ROM is downloaded or read. The hash-only recipe consumes local outputs of
the pinned expansion source build. It is not the upstream retail-ROM recipe.
"""
import argparse
import configparser
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'builder'), str(ROOT / 'tools/port_common')]
from emerald3ds_builder import pak
from emerald3ds_builder.custom_package import (APP, FILES, MANIFEST, RULES,
    PackageError, engine_romfs, install_bundle, recover, sha, validate_bundle)
import staging


def recipe(tree, out):
    tree = tree.resolve()
    romfs = tree / '3ds_port/romfs'
    abi, items = staging.compute_abi(romfs)
    engine = tree / '3ds_port/dist' / FILES[0]
    if engine_romfs(engine).get('engine/abi.bin') != struct.pack('<I', abi):
        raise PackageError('engine-only output does not match staged data')
    lock = configparser.ConfigParser()
    lock.read(ROOT / 'upstream.lock')
    pin = lock['pokeemerald-expansion']['commit'].strip('"')
    if subprocess.check_output(['git', '-C', str(tree), 'rev-parse', 'HEAD'], text=True).strip() != pin:
        raise PackageError('unexpected source pin')
    from bootstrap import patch_digest
    digest = patch_digest(sorted((ROOT / 'patches/pokeemerald-expansion').glob('*.patch')))
    if (tree / '.emerald3ds-patches').read_text().strip() != digest:
        raise PackageError('source tree does not match canonical patch')
    paths = staging.data_files(romfs)
    if staging.optional_files(romfs):
        raise PackageError('unversioned optional data is not part of this recipe')
    result = {'schema': 1, 'kind': 'custom-pinned-source-data', 'namespace': APP,
        'rules': RULES, 'save_schema': 1, 'engine_abi': abi,
        'private_content_bearing': True, 'rom_profile_sha1': lock['rom']['sha1'].strip('"'),
        'source_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        'source_diff_sha256': hashlib.sha256(subprocess.check_output(['git','diff','HEAD'], cwd=ROOT)).hexdigest(),
        'expansion_pin': pin, 'graphics_pin': lock['graphics']['commit'].strip('"'),
        'patch_sha256': sha(ROOT / 'patches/pokeemerald-expansion/0001-port.patch'),
        'campaign_sha256': sha(ROOT / 'tools/campaign_f.json'),
        'engine': {n: {'bytes': (tree/'3ds_port/dist'/n).stat().st_size,
                       'sha256': sha(tree/'3ds_port/dist'/n)} for n in FILES[:2]},
        'entries': [{'path': n, 'bytes': p.stat().st_size, 'sha256': sha(p)} for n,p in paths]}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(f'Hash-only local source recipe: {out}; ABI {abi:08x}, {len(items)} data files')
    return result


def build(recipe_file, romfs, engine_dir, out):
    spec = json.loads(recipe_file.read_text())
    if (spec.get('schema') != 1 or spec.get('kind') != 'custom-pinned-source-data'
            or spec.get('namespace') != APP or spec.get('rules') != RULES):
        raise PackageError('unsupported source-data recipe')
    expected = {e['path']: e for e in spec['entries']}
    if len(expected) != len(spec['entries']):
        raise PackageError('duplicate recipe entry')
    actual = dict(staging.data_files(romfs))
    if set(actual) != set(expected) or staging.optional_files(romfs):
        raise PackageError('source data file set does not match recipe')
    for name, p in actual.items():
        if p.is_symlink() or p.stat().st_size != expected[name]['bytes'] or sha(p) != expected[name]['sha256']:
            raise PackageError('source data differs from recipe: ' + name)
    abi, _ = staging.compute_abi(romfs)
    if abi != spec['engine_abi']:
        raise PackageError('source data ABI mismatch')
    for name, entry in spec['engine'].items():
        if name not in FILES[:2] or sha(engine_dir/name) != entry['sha256']:
            raise PackageError('compiled engine differs from recipe')
    if set(spec['engine']) != set(FILES[:2]):
        raise PackageError('incomplete engine receipt')
    # Refuse an existing output, including partial bundles; no silent overwrite.
    out.mkdir(parents=True, exist_ok=False)
    try:
        for name in FILES[:2]:
            shutil.copyfile(engine_dir/name, out/name)
            if sha(out/name) != spec['engine'][name]['sha256']:
                raise PackageError('engine changed during copy')
        def payloads():
            for n,p in sorted(actual.items()):
                data = p.read_bytes()
                if hashlib.sha256(data).hexdigest() != expected[n]['sha256']:
                    raise PackageError('source changed during packing: ' + n)
                yield n,data
        pak.write_pak(out/FILES[2], payloads(),
                      abi, bytes.fromhex(spec['rom_profile_sha1']))
        meta = {k: v for k,v in spec.items() if k not in ('entries','engine','kind')}
        meta.update(data_files=len(actual), recipe_sha256=sha(recipe_file),
            files={n: {'bytes': (out/n).stat().st_size, 'sha256': sha(out/n)} for n in FILES},
            emulator_tested=False, hardware_tested=False)
        (out/MANIFEST).write_text(json.dumps(meta, indent=2)+'\n')
        validate_bundle(out)
    except Exception:
        shutil.rmtree(out)
        raise
    print(f'PRIVATE bundle verified: {out}; {len(actual)} data files, ABI {abi:08x}')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    subs = ap.add_subparsers(dest='command', required=True)
    p = subs.add_parser('recipe'); p.add_argument('--tree', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
    p = subs.add_parser('build'); p.add_argument('--recipe', type=Path, required=True); p.add_argument('--romfs', type=Path, required=True); p.add_argument('--engine-dir', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
    p = subs.add_parser('verify'); p.add_argument('--bundle', type=Path, required=True)
    p = subs.add_parser('install'); p.add_argument('--bundle', type=Path, required=True); p.add_argument('--sd', type=Path, required=True)
    p = subs.add_parser('recover'); p.add_argument('--sd', type=Path, required=True)
    a = ap.parse_args()
    if a.command == 'recipe': recipe(a.tree, a.out)
    elif a.command == 'build': build(a.recipe, a.romfs, a.engine_dir, a.out)
    elif a.command == 'verify':
        m = validate_bundle(a.bundle); print(f'PASS bundle, ABI {m["engine_abi"]:08x}; no hardware result implied')
    elif a.command == 'install': print(json.dumps(install_bundle(a.sd, a.bundle), indent=2))
    elif a.command == 'recover': print('Rolled back interrupted install' if recover(a.sd) else 'No interrupted install')


if __name__ == '__main__':
    main()
