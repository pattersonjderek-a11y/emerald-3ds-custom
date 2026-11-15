"""Malformed pack layouts with valid CRCs must fail before any payload read."""
import struct
from pathlib import Path
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from emerald3ds_builder import pak


class PakLayoutTests(unittest.TestCase):
    def test_invalid_layouts_with_valid_header_and_index_checksums(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp)/'test.pak'
            pak.write_pak(file, [('data/fixture.bin', b'synthetic fixture')], 123, bytes(20))
            original = file.read_bytes()
            index = struct.unpack_from('<Q', original, 40)[0]
            cases = [('empty count',36,'I',0), ('excessive count',36,'I',(1<<20)+1),
                     ('index in header',40,'Q',0), ('data in index',48,'Q',64),
                     ('compression',index+12,'I',1), ('unknown flags',index+12,'I',2),
                     ('different stored size',index+24,'I',1),
                     ('payload in metadata',index+16,'Q',64),
                     ('unaligned payload',index+16,'Q',129),
                     ('payload beyond file',index+16,'Q',len(original)+32)]
            for label,offset,kind,value in cases:
                with self.subTest(label=label):
                    blob=bytearray(original);struct.pack_into('<'+kind,blob,offset,value)
                    struct.pack_into('<I',blob,56,zlib.crc32(blob[index:index+pak.ENTRY.size]))
                    struct.pack_into('<I',blob,60,zlib.crc32(blob[:60]));file.write_bytes(blob)
                    with self.assertRaises(pak.PakError):pak.PakReader(file)

    def test_writer_output_with_empty_payload_remains_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/'test.pak'
            pak.write_pak(file,[('data/empty.bin',b''),('data/normal.bin',b'synthetic')],123,bytes(20))
            with pak.PakReader(file) as reader:
                self.assertEqual(reader.verify(),2)
                self.assertEqual(reader.read('data/empty.bin'),b'')


if __name__=='__main__':unittest.main()
