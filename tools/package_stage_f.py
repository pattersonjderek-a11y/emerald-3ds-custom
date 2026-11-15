#!/usr/bin/env python3
"""Freeze an audited PRIVATE F bundle plus portable laptop installer."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'builder'))
from emerald3ds_builder.custom_package import APP, FILES, MANIFEST, sha, validate_bundle


def main():
    bundle = ROOT / 'work/stage-f-bundle'
    meta = validate_bundle(bundle)
    # Do not freeze unreviewable source or bypass the verification checkpoint.
    if subprocess.check_output(['git','status','--porcelain'], cwd=ROOT).strip():
        raise SystemExit('Checkpoint source before freezing the test package')
    commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    if meta['source_commit'] != commit or meta['source_diff_sha256'] != hashlib.sha256(b'').hexdigest():
        raise SystemExit('Bundle source receipt differs from the clean checkpoint')
    out = ROOT / 'work/stage-f-private'
    out.mkdir(exist_ok=True)
    target = out / 'Emerald3DS-Custom-StageF-private.zip'
    if target.exists():
        raise SystemExit('Frozen ZIP exists; do not overwrite it')
    files = {f'3ds/{APP}/{n}': bundle/n for n in (*FILES, MANIFEST)}
    files['installer/install_custom.py'] = ROOT/'tools/install_custom.py'
    for name in ('__init__.py','custom_package.py','pak.py'):
        files['installer/emerald3ds_builder/'+name] = ROOT/'builder/emerald3ds_builder'/name
    for src, dst in (('docs/STAGE_F_INSTALL.md','READ_ME_FIRST.md'),
                     ('docs/DEVICE_TESTS.md','DEVICE_TESTS.md'),
                     ('LICENSE-PORT.md','LICENSES/LICENSE-PORT.md'),
                     ('NOTICE.md','LICENSES/NOTICE.md'),
                     ('3ds_port/src/voxel/NOTICE.md','LICENSES/VOXEL-NOTICE.md'),
                     ('docs/SOURCES.md','SOURCES.md'),
                     ('docs/STAGE_E_TOOLCHAIN_PACKAGES.txt','TOOLCHAIN_PACKAGES.txt')):
        files[dst] = ROOT/src
    with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED) as z:
        for rel,path in files.items():z.write(path, rel)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for rel,path in files.items():
            assert hashlib.sha256(z.read(rel)).hexdigest() == sha(path), rel
    report = {'path':str(target.relative_to(ROOT)), 'bytes':target.stat().st_size,
              'sha256':sha(target), 'source_commit':commit, 'engine_abi':meta['engine_abi'],
              'files':meta['files'], 'hardware_tested':False, 'emulator_tested':False,
              'data_recipe_sha256':meta['recipe_sha256']}
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
