"""Exercise the production private installer with synthetic engine/data/state.

Interrupts occur at real file/directory operations, including after a commit.
No ROMs, actual game packages or player saves are used.
"""
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'builder'), str(ROOT / 'tools')]
from emerald3ds_builder import custom_package as cp, pak
import custom_payload


def synthetic_engine(abi, namespace=cp.APP):
    # Minimal raw RomFS with /engine/abi.bin; actual production parser reads it.
    root = struct.pack('<6I', 0, 0xffffffff, 24, 0xffffffff, 0xffffffff, 0)
    name = 'engine'.encode('utf-16le')
    child = struct.pack('<6I', 0, 0xffffffff, 0xffffffff, 0, 0xffffffff, len(name)) + name
    dirs = root + child
    fname = 'abi.bin'.encode('utf-16le')
    files = struct.pack('<IIQQII', 24, 0xffffffff, 0, 4, 0xffffffff, len(fname)) + fname
    dm, fm = 40, 40 + len(dirs)
    data = fm + len(files)
    rom = struct.pack('<10I', 40, 40, 0, dm, len(dirs), fm, 0, fm, len(files), data)
    rom += dirs + files + struct.pack('<I', abi)
    head = bytearray(256)
    head[:4] = b'3DSX'
    struct.pack_into('<H', head, 4, 44)
    struct.pack_into('<I', head, 40, len(head))
    return bytes(head) + rom + ('sdmc:/3ds/' + namespace + '/').encode()


class CustomPackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.sd = self.root / 'sd'
        self.sd.mkdir()
        self.bundle = self.root / 'bundle'
        self.bundle.mkdir()
        self.abi = pak.engine_abi([('gamedata/test.bin', 7, zlib.crc32(b'fixture'))])
        (self.bundle / cp.FILES[0]).write_bytes(synthetic_engine(self.abi))
        (self.bundle / cp.FILES[1]).write_bytes(b'SMDH' + bytes(14012))
        pak.write_pak(self.bundle / cp.FILES[2], [('gamedata/test.bin', b'fixture')], self.abi, bytes(20))
        self.meta = {'schema': 1, 'namespace': cp.APP, 'rules': cp.RULES, 'save_schema': 1,
            'engine_abi': self.abi, 'private_content_bearing': True, 'data_files': 1,
            'rom_profile_sha1': '00' * 20}
        self.receipt()
        self.dest = self.sd / '3ds' / cp.APP

    def receipt(self):
        self.meta['files'] = {n: {'bytes': (self.bundle/n).stat().st_size,
                                  'sha256': cp.sha(self.bundle/n)} for n in cp.FILES}
        (self.bundle/cp.MANIFEST).write_text(json.dumps(self.meta))

    def install_old(self):
        cp.install_bundle(self.sd, self.bundle)
        for name in ('emerald3ds.sav', 'settings.txt', 'settings.txt.tmp',
                     'emerald3ds.clock', 'emerald3ds.clock.tmp', 'emerald3ds.clock.bak',
                     'emerald3ds.nuzlocke', 'emerald3ds.nuzlocke.tmp', 'emerald3ds.nuzlocke.bak',
                     'plates.bin', 'port.log', 'backup/old-test.txt'):
            p = self.dest/name
            p.parent.mkdir(exist_ok=True)
            p.write_bytes(b'SYNTHETIC STATE: ' + name.encode())
        return self.snapshot(self.dest)

    @staticmethod
    def snapshot(folder):
        return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob('*') if p.is_file()}

    def change_engine(self):
        p = self.bundle/cp.FILES[0]
        p.write_bytes(p.read_bytes() + b' NEW ENGINE')
        self.receipt()

    def test_actual_romfs_parser_roundtrip_and_bad_tables(self):
        p = self.bundle/cp.FILES[0]
        self.assertEqual(cp.engine_romfs(p)['engine/abi.bin'], struct.pack('<I',self.abi))
        blob = bytearray(p.read_bytes())
        struct.pack_into('<I',blob,256+12,0xffffffff)
        p.write_bytes(blob)
        with self.assertRaises(cp.PackageError): cp.engine_romfs(p)

    def test_first_install_and_legacy_namespaces_untouched(self):
        originals = {}
        for app in ('emerald3ds', 'pokeemerald', 'emerald3ds-custom', 'emerald3ds-custom-stage-b',
                    'emerald3ds-custom-stage-c', 'emerald3ds-custom-stage-d', 'emerald3ds-custom-stage-e-v050'):
            folder = self.sd/'3ds'/app
            folder.mkdir(parents=True)
            for n in ('emerald3ds.sav','settings.txt','emerald3ds.clock','emerald3ds.nuzlocke','plates.bin'):
                p = folder/n; p.write_bytes(b'LEGACY ' + app.encode() + n.encode()); originals[p] = p.read_bytes()
        result = cp.install_bundle(self.sd,self.bundle)
        self.assertIsNone(result['backup'])
        self.assertEqual(cp.sha(self.dest/cp.FILES[0]), cp.sha(self.bundle/cp.FILES[0]))
        self.assertFalse((self.dest/'emerald3ds.sav').exists())
        for p,data in originals.items(): self.assertEqual(p.read_bytes(),data)

    def test_update_preserves_all_state_and_complete_backup(self):
        old = self.install_old()
        self.change_engine()
        result = cp.install_bundle(self.sd,self.bundle)
        self.assertEqual(self.snapshot(Path(result['backup'])), old)
        for name,data in old.items():
            if name not in (*cp.FILES,cp.MANIFEST,'.install-token'):
                self.assertEqual((self.dest/name).read_bytes(),data)
        self.assertNotEqual((self.dest/cp.FILES[0]).read_bytes(),old[cp.FILES[0]])
        self.assertFalse(cp.recover(self.sd))

    def test_corrupt_file_rejected_before_any_sd_write(self):
        p=self.bundle/cp.FILES[2]; p.write_bytes(p.read_bytes()+b'corrupt')
        with self.assertRaises(cp.PackageError): cp.install_bundle(self.sd,self.bundle)
        self.assertEqual(list(self.sd.iterdir()),[])

    def test_wrong_pack_abi_rejected_even_with_new_file_hash(self):
        pak.write_pak(self.bundle/cp.FILES[2], [('gamedata/test.bin',b'fixture')],self.abi^1,bytes(20))
        self.receipt()
        with self.assertRaisesRegex(cp.PackageError,'ABI'): cp.validate_bundle(self.bundle)

    def test_wrong_engine_abi_or_namespace_rejected(self):
        for abi,app in ((self.abi^1,cp.APP),(self.abi,'emerald3ds-custom-stage-e-v050')):
            with self.subTest(abi=abi,app=app):
                (self.bundle/cp.FILES[0]).write_bytes(synthetic_engine(abi,app));self.receipt()
                with self.assertRaises(cp.PackageError): cp.validate_bundle(self.bundle)

    def test_corrupt_pack_payload_rejected_with_recomputed_file_hash(self):
        p=self.bundle/cp.FILES[2]; blob=bytearray(p.read_bytes());blob[-32]^=1;p.write_bytes(blob);self.receipt()
        with self.assertRaises(pak.PakError): cp.validate_bundle(self.bundle)

    def test_unknown_schema_rules_and_state_payload_rejected(self):
        for key,value in (('schema',2),('rules',0x00040050),('save_schema',2),('namespace','emerald3ds')):
            old=self.meta[key];self.meta[key]=value;self.receipt()
            with self.subTest(key=key),self.assertRaises(cp.PackageError): cp.validate_bundle(self.bundle)
            self.meta[key]=old
        self.receipt();(self.bundle/'emerald3ds.sav').write_bytes(b'SYNTHETIC')
        with self.assertRaises(cp.PackageError): cp.validate_bundle(self.bundle)

    def test_missing_receipt_and_incompatible_update_preserve_old_folder(self):
        old=self.install_old();(self.dest/cp.MANIFEST).unlink()
        before=self.snapshot(self.dest)
        with self.assertRaises(cp.PackageError): cp.install_bundle(self.sd,self.bundle)
        self.assertEqual(self.snapshot(self.dest),before)
        meta=dict(self.meta);meta['rules']^=1;(self.dest/cp.MANIFEST).write_text(json.dumps(meta))
        before=self.snapshot(self.dest)
        with self.assertRaises(cp.PackageError): cp.install_bundle(self.sd,self.bundle)
        self.assertEqual(self.snapshot(self.dest),before)

    def test_loose_data_override_refused(self):
        self.install_old();(self.dest/'devdata').mkdir()
        with self.assertRaises(cp.PackageError): cp.install_bundle(self.sd,self.bundle)

    def test_symlink_dest_and_state_refused(self):
        outside=self.root/'outside';outside.mkdir();(self.sd/'3ds').mkdir();self.dest.symlink_to(outside,target_is_directory=True)
        with self.assertRaises(cp.PackageError): cp.install_bundle(self.sd,self.bundle)
        self.dest.unlink();self.install_old();(self.dest/'state-link').symlink_to(outside,target_is_directory=True)
        with self.assertRaises(cp.PackageError): cp.install_bundle(self.sd,self.bundle)
        self.assertEqual(list(outside.iterdir()),[])

    def test_symlink_bundle_file_refused(self):
        p=self.bundle/cp.FILES[1];outside=self.root/'metadata';p.rename(outside);p.symlink_to(outside)
        with self.assertRaises(cp.PackageError): cp.validate_bundle(self.bundle)

    def test_copy_failure_rolls_back_before_old_folder_moves(self):
        old=self.install_old()
        with patch.object(cp.shutil,'copyfile',side_effect=OSError('injected disk error')):
            with self.assertRaises(OSError): cp.install_bundle(self.sd,self.bundle)
        self.assertEqual(self.snapshot(self.dest),old)
        self.assertFalse((self.dest.parent/cp.JOURNAL).exists())

    def test_rename_failure_restores_old_folder(self):
        old=self.install_old();real=os.replace
        def failing(src,dst):
            if str(src).endswith('.staging'):raise OSError('injected rename failure')
            return real(src,dst)
        with patch.object(cp.os,'replace',side_effect=failing):
            with self.assertRaises(OSError):cp.install_bundle(self.sd,self.bundle)
        self.assertEqual(self.snapshot(self.dest),old)

    def test_process_interrupt_before_and_after_new_directory_commit(self):
        old=self.install_old();self.change_engine();real=os.replace
        class PowerLoss(BaseException):pass
        for after in (False,True):
            with self.subTest(after_commit=after):
                def interrupt(src,dst):
                    if str(src).endswith('.staging'):
                        if after:real(src,dst)
                        raise PowerLoss()
                    return real(src,dst)
                with patch.object(cp.os,'replace',side_effect=interrupt):
                    with self.assertRaises(PowerLoss):cp.install_bundle(self.sd,self.bundle)
                with self.assertRaisesRegex(cp.PackageError,'recover'):cp.install_bundle(self.sd,self.bundle)
                self.assertTrue(cp.recover(self.sd))
                self.assertEqual(self.snapshot(self.dest),old)
                self.assertFalse(cp.recover(self.sd))

    def test_first_install_interrupt_does_not_create_a_partial_application(self):
        real=os.replace
        class PowerLoss(BaseException):pass
        def interrupt(src,dst):
            real(src,dst);raise PowerLoss()
        with patch.object(cp.os,'replace',side_effect=interrupt):
            with self.assertRaises(PowerLoss):cp.install_bundle(self.sd,self.bundle)
        cp.recover(self.sd);self.assertFalse(self.dest.exists())

    def test_failed_recovery_can_be_retried(self):
        old=self.install_old();real=os.replace
        def fail(src,dst):
            if str(src).endswith('.staging') or '.backup-' in str(src):raise OSError('SD removed')
            return real(src,dst)
        with patch.object(cp.os,'replace',side_effect=fail):
            with self.assertRaises(OSError):cp.install_bundle(self.sd,self.bundle)
        self.assertTrue((self.dest.parent/cp.JOURNAL).exists())
        cp.recover(self.sd);self.assertEqual(self.snapshot(self.dest),old)

    def test_malformed_journal_cannot_redirect_recovery(self):
        old=self.install_old();j=self.dest.parent/cp.JOURNAL
        j.write_text(json.dumps({'schema':1,'token':'../../other','had_previous':True}))
        with self.assertRaises(cp.PackageError):cp.recover(self.sd)
        self.assertEqual(self.snapshot(self.dest),old)

    def test_low_space_refused_without_mutating_previous_install(self):
        old=self.install_old()
        with patch.object(cp.shutil,'disk_usage',return_value=type('Usage',(),{'free':1})()):
            with self.assertRaises(cp.PackageError):cp.install_bundle(self.sd,self.bundle)
        self.assertEqual(self.snapshot(self.dest),old)

    def test_hash_only_source_recipe_rebuilds_matching_pack_and_rejects_changed_data(self):
        romfs=self.root/'romfs';(romfs/'gamedata').mkdir(parents=True)
        f=romfs/'gamedata/test.bin';f.write_bytes(b'fixture')
        spec={**self.meta,'kind':'custom-pinned-source-data','engine':dict(self.meta['files']),
              'entries':[{'path':'gamedata/test.bin','bytes':7,'sha256':cp.sha(f)}]}
        del spec['engine'][cp.FILES[2]]
        recipe=self.root/'recipe.json';recipe.write_text(json.dumps(spec));out=self.root/'rebuilt'
        custom_payload.build(recipe,romfs,self.bundle,out)
        cp.validate_bundle(out)
        self.assertEqual((out/cp.FILES[2]).read_bytes(),(self.bundle/cp.FILES[2]).read_bytes())
        f.write_bytes(b'changed')
        with self.assertRaises(cp.PackageError):custom_payload.build(recipe,romfs,self.bundle,self.root/'bad')
        self.assertFalse((self.root/'bad').exists())


if __name__ == '__main__':
    unittest.main()
