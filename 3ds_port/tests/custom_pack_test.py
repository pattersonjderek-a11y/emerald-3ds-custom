"""Read the actual private pack through production console C parser on host.

This executes C on Linux, not ARM or an emulator. No package is published.
"""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

PORT = Path(__file__).resolve().parents[1]
C = r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "3ds_pak.h"
int main(int argc,char **argv) {
 assert(argc==4);
 FILE *f=fopen(argv[1],"rb");assert(f);
 assert(fseek(f,0,SEEK_END)==0);long length=ftell(f);assert(length>=64);
 rewind(f);uint8_t *blob=malloc((size_t)length);assert(blob);
 assert(fread(blob,1,(size_t)length,f)==(size_t)length);fclose(f);
 uint32_t abi=(uint32_t)strtoul(argv[2],NULL,16);
 uint8_t rom[20];for(unsigned i=0;i<20;i++){unsigned value;assert(sscanf(argv[3]+i*2,"%2x",&value)==1);rom[i]=(uint8_t)value;}
 CtrPakHeader h;
 assert(CtrPak_ParseHeader(blob,abi^1u,rom,&h)==CTR_PAK_BAD_ABI);
 rom[0]^=1;assert(CtrPak_ParseHeader(blob,abi,rom,&h)==CTR_PAK_BAD_ROM);rom[0]^=1;
 assert(CtrPak_ParseHeader(blob,abi,rom,&h)==CTR_PAK_OK);
 uint64_t indexBytes=(uint64_t)h.entryCount*CTR_PAK_ENTRY_BYTES;
 assert(h.indexOffset<= (uint64_t)length && indexBytes<= (uint64_t)length-h.indexOffset);
 CtrPakEntry *entries=calloc(h.entryCount,sizeof(*entries));assert(entries);
 assert(CtrPak_ParseIndex(blob+h.indexOffset,&h,entries)==CTR_PAK_OK);
 for(unsigned i=0;i<h.entryCount;i++){
  const CtrPakEntry *e=&entries[i];
  assert(e->offset%32==0 && e->offset<=(uint64_t)length && e->rawSize<=(uint64_t)length-e->offset);
  assert(CtrPak_Crc32(0,blob+e->offset,e->rawSize)==e->crc32);
 }
 assert(CtrPak_Find(entries,h.entryCount,"gamedata/gamedata.bin"));
 printf("Production console pack parser PASS on host: %u actual payloads, ABI %08x; wrong ABI/profile refused\n",h.entryCount,abi);
 free(entries);free(blob);return 0;
}
'''


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle',type=Path,required=True)
    p.add_argument('--cc',default='gcc')
    a=p.parse_args();m=json.loads((a.bundle/'CUSTOM_INSTALL.json').read_text())
    with tempfile.TemporaryDirectory() as d:
        src=Path(d)/'pack.c';exe=Path(d)/'pack-test';src.write_text(C)
        subprocess.run([a.cc,'-std=c99','-O1','-g','-Wall','-Wextra','-Werror',
                        '-fsanitize=address,undefined','-fno-omit-frame-pointer',
                        '-I'+str(PORT/'include'),str(src),str(PORT/'src/3ds_pak.c'),'-o',str(exe)],check=True)
        subprocess.run([str(exe),str(a.bundle/'emerald3ds.pak'),f'{m["engine_abi"]:08x}',m['rom_profile_sha1']],check=True)


if __name__=='__main__':main()
