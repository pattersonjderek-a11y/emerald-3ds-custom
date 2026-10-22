#!/usr/bin/env python3
"""Audit and package a verified embedded build for PRIVATE console testing.

Run tools/stage_a.sh test first. This never publishes or installs anything.
Generated content stays in ignored work/; never attach this ZIP to public CI.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/port_common'))
import staging


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stage', choices=('A', 'B', 'C'), default='A')
    ap.add_argument('--tree', type=Path)
    args = ap.parse_args()
    tree = (args.tree or ROOT / {'A':'build/expansion','B':'build/stage-b','C':'build/stage-c'}[args.stage]).resolve()
    namespace = 'emerald3ds-custom' + (f'-stage-{args.stage.lower()}' if args.stage != 'A' else '')
    port = tree / '3ds_port'
    from bootstrap import patch_digest
    expected = patch_digest(sorted((ROOT / 'patches/pokeemerald-expansion').glob('*.patch')))
    assert (tree / '.emerald3ds-patches').read_text().strip() == expected, 'Tree/patch mismatch; use the matching source branch or bootstrap'
    # Re-run the gating audits. No package is written if any check fails.
    subprocess.run(['make', '-C', str(port), 'verify', 'PYTHON=python3'], check=True)
    subprocess.run([sys.executable, '-m', 'unittest',
                    'builder.tests.test_expansion_enhancements', '-v'], cwd=ROOT,
                   env={**os.environ, 'EMERALD3DS_EXPANSION_TREE': str(tree)}, check=True)
    subprocess.run([sys.executable, 'tools/release_audit.py', '--repo', '.', '--strict'],
                   cwd=ROOT, check=True)
    romfs = port / 'romfs'
    abi, items = staging.compute_abi(romfs)
    assert struct.unpack('<I', (romfs / 'engine/abi.bin').read_bytes())[0] == abi
    assert (romfs / 'data.embedded').is_file()
    asset_map = romfs / 'assets/asset_map.txt'
    rows = asset_map.read_text().splitlines()
    assert len(rows) > 1000, 'empty/truncated expansion asset index'
    app = port / 'emerald3ds.3dsx'
    blob = app.read_bytes()
    assert blob[:4] == b'3DSX'
    assert f'sdmc:/3ds/{namespace}/'.encode() in blob
    if args.stage != 'A':
        assert b'sdmc:/3ds/emerald3ds-custom/' not in blob
    if args.stage == 'C':
        assert b'sdmc:/3ds/emerald3ds-custom-stage-b/' not in blob
    assert b'sdmc:/3ds/emerald3ds/' not in blob
    assert b'sdmc:/3ds/pokeemerald/' not in blob
    assert struct.pack('<I', abi) in blob, 'ABI missing from embedded application'
    # Verify every pack payload, not just its header; compare against this tree.
    pack = port / 'build/emerald3ds.pak'
    pack_info = None
    if pack.is_file():
        from emerald3ds_builder.pak import PakReader
        with PakReader(pack) as reader:
            assert reader.abi == abi
            count = reader.verify()
            assert count == len(items)
        pack_info = {'bytes': pack.stat().st_size, 'sha256': sha(pack), 'entries': count}
    files = {f'3ds/{namespace}/Emerald3DS.3dsx': app,
             f'3ds/{namespace}/Emerald3DS.smdh': port / 'emerald3ds.smdh'}
    report = {
        'private_content_bearing': True, 'stage': args.stage, 'namespace': namespace,
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'source_diff_sha256': hashlib.sha256(subprocess.check_output(['git', 'diff', 'HEAD'], cwd=ROOT)).hexdigest(),
        'engine_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=tree, text=True).strip(),
        'upstream_lock_sha256': sha(ROOT / 'upstream.lock'),
        'expansion_patch_sha256': sha(ROOT / 'patches/pokeemerald-expansion/0001-port.patch'),
        'toolchain_manifest_sha256': sha(ROOT / 'docs/TOOLCHAIN_PACKAGES.txt'),
        'build_config_sha256': sha(port / 'build/config'),
        'engine_build_info_sha256': sha(port / 'build/buildinfo.c'),
        'engine_abi': f'{abi:08x}', 'game_data_files': len(items),
        'game_data_bytes': sum(size for _, size, _ in items),
        'asset_map_rows': len(rows), 'asset_map_sha256': sha(asset_map),
        'asset_index_entries': (romfs / 'assets/asset_index.bin').stat().st_size // 12,
        'asset_pointer_entries': (romfs / 'assets/asset_ptr_index.bin').stat().st_size // 12,
        'pack': pack_info,
        'files': {name: {'bytes': p.stat().st_size, 'sha256': sha(p)} for name, p in files.items()},
        'native_verified': True, 'emulator_tested': False, 'hardware_tested': False,
        'limitations': 'Generated asset inventory is not a complete Gen 1-9/follower coverage audit.',
    }
    out = ROOT / (f'work/stage-{args.stage.lower()}-private' if args.stage != 'A' else 'work/private-smoke')
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.dumps(report, indent=2) + '\n'
    (out / 'manifest.json').write_text(manifest)
    zip_path = out / f'Emerald3DS-Custom-Stage{args.stage}-private.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, path in files.items():
            archive.write(path, name)
        archive.writestr(f'3ds/{namespace}/debug.txt', '')
        archive.writestr(f'STAGE_{args.stage}_MANIFEST.json', manifest)
        archive.write(ROOT / 'docs/TOOLCHAIN_PACKAGES.txt', 'TOOLCHAIN_PACKAGES.txt')
        archive.write(ROOT / 'docs/DEVICE_TESTS.md', 'READ_ME_FIRST.md')
    print(manifest)
    print(f'PRIVATE package: {zip_path} ({zip_path.stat().st_size} bytes); SHA-256 {sha(zip_path)}')


if __name__ == '__main__':
    main()
