"""Packaging must reject a stale linked-data audit or a changed native output."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'tools'))
from package_stage_f import verify_campaign_report, verify_native_baseline


class PackageEvidenceTests(unittest.TestCase):
    def test_audit_from_before_relink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree=Path(tmp);image=tree/'3ds_port/build/gamedata_image.elf'
            image.parent.mkdir(parents=True);image.write_bytes(b'synthetic first link')
            evidence={'source_audit':'passed','native_data_audit':'passed',
                      'image_sha256':hashlib.sha256(image.read_bytes()).hexdigest()}
            report=tree/'audit.json';report.write_text(json.dumps(evidence))
            verify_campaign_report(tree,report)
            image.write_bytes(b'synthetic final link')
            with self.assertRaisesRegex(ValueError,'stale'):verify_campaign_report(tree,report)

    def test_reusing_native_outputs_requires_all_seven_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);prefix='build/stage-f/3ds_port/';files={}
            names=('emerald3ds.3dsx','emerald3ds.smdh','emerald3ds.elf','build/gamedata_image.elf',
                   'dist/Emerald3DS.3dsx','dist/Emerald3DS.smdh','build/emerald3ds.pak')
            for name in names:
                p=root/prefix/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'synthetic '+name.encode())
                files[prefix+name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
            report=root/'baseline.json';report.write_text(json.dumps({'source_commit':'baseline','files':files}))
            self.assertEqual(verify_native_baseline(root,report),'baseline')
            p.write_bytes(b'changed synthetic output')
            with self.assertRaisesRegex(ValueError,'native output changed'):verify_native_baseline(root,report)


if __name__=='__main__':unittest.main()
