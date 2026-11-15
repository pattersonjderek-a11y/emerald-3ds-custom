#!/usr/bin/env python3
"""Freeze an audited PRIVATE F bundle plus portable laptop installer."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'builder'))
from emerald3ds_builder.custom_package import APP, FILES, MANIFEST, sha, validate_bundle


def verify_campaign_report(tree, path):
    evidence = json.loads(path.read_text())
    if (evidence.get('source_audit') != 'passed' or evidence.get('native_data_audit') != 'passed'
            or evidence.get('image_sha256') != sha(tree/'3ds_port/build/gamedata_image.elf')):
        raise ValueError('campaign audit is missing, failed or stale; rerun campaign_audit.py after linking')
    return evidence['image_sha256']


def verify_native_baseline(root, path):
    baseline = json.loads(path.read_text())
    prefix = 'build/stage-f/3ds_port/'
    for name in ('emerald3ds.3dsx', 'emerald3ds.smdh', 'emerald3ds.elf',
                 'build/gamedata_image.elf', 'dist/Emerald3DS.3dsx',
                 'dist/Emerald3DS.smdh', 'build/emerald3ds.pak'):
        entry = baseline['files'][prefix+name]
        file = root/prefix/name
        if file.stat().st_size != entry['bytes'] or sha(file) != entry['sha256']:
            raise ValueError('native output changed from the verified baseline: '+name)
    return baseline['source_commit']


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bundle', type=Path, default=ROOT/'work/stage-f-bundle')
    ap.add_argument('--tree', type=Path, default=ROOT/'build/stage-f')
    ap.add_argument('--campaign-report', type=Path, default=ROOT/'docs/STAGE_F_CAMPAIGN.json')
    ap.add_argument('--native-baseline', type=Path, help='require byte-identical native outputs from a verified earlier build')
    ap.add_argument('--rehearsal-report', type=Path, help='require a matching successful installer/update/recovery rehearsal')
    ap.add_argument('--output', type=Path, default=ROOT/'work/stage-f-private/Emerald3DS-Custom-StageF-private.zip')
    args = ap.parse_args()
    bundle = args.bundle
    meta = validate_bundle(bundle)
    image_sha = verify_campaign_report(args.tree, args.campaign_report)
    native_source = verify_native_baseline(ROOT, args.native_baseline) if args.native_baseline else None
    for name in FILES:
        file = (args.tree/'3ds_port/build'/name if name.endswith('.pak')
                else args.tree/'3ds_port/dist'/name)
        if sha(file) != meta['files'][name]['sha256']:
            raise ValueError('bundle does not match the compiled output: '+name)
    # Do not freeze unreviewable source or bypass the verification checkpoint.
    if subprocess.check_output(['git','status','--porcelain'], cwd=ROOT).strip():
        raise SystemExit('Checkpoint source before freezing the test package')
    commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    if meta['source_commit'] != commit or meta['source_diff_sha256'] != hashlib.sha256(b'').hexdigest():
        raise SystemExit('Bundle source receipt differs from the clean checkpoint')
    if args.rehearsal_report:
        rehearsal = json.loads(args.rehearsal_report.read_text())
        if (rehearsal.get('source_commit') != commit or rehearsal.get('engine_abi') != meta['engine_abi']
                or any(rehearsal.get(k) != 'passed' for k in
                       ('compatible_update', 'whole_folder_backup', 'interruption_during_recovery', 'rollback'))):
            raise ValueError('installer rehearsal is failed or stale')
    target = args.output.resolve()
    if not target.is_relative_to(ROOT/'work'):
        raise SystemExit('Private package must remain under ignored work/')
    out = target.parent
    out.mkdir(parents=True,exist_ok=True)
    if target.exists() or (out/'manifest.json').exists():
        raise SystemExit('Frozen ZIP/manifest exists; do not overwrite it')
    files = {f'3ds/{APP}/{n}': bundle/n for n in (*FILES, MANIFEST)}
    files['CAMPAIGN_AUDIT.json'] = args.campaign_report
    if args.native_baseline:files['NATIVE_BASELINE.json'] = args.native_baseline
    if args.rehearsal_report:files['INSTALLER_REHEARSAL.json'] = args.rehearsal_report
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
              'data_recipe_sha256':meta['recipe_sha256'], 'campaign_image_sha256':image_sha,
              'native_baseline_source':native_source, 'native_recompiled':False if native_source else None}
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
