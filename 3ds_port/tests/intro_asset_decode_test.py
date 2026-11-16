"""Exercise production expansion codecs/heap loader with real intro pack bytes.

The expected bytes are the native compressor's raw inputs in the build tree.
Host C only: this neither renders sprites nor executes ARM/GPU code.
"""
import argparse
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from voxel_runtime_test import function

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'builder'))
from emerald3ds_builder.pak import PakReader

BASE = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t u8;typedef uint16_t u16;typedef uint32_t u32;
typedef int32_t s32;typedef uint64_t u64;typedef unsigned bool32;
#define TRUE 1
#define FALSE 0
#define ARM_FUNC
#define UNUSED
#define PORT_LZ77_HEADER 0x10
#define IWRAM_DATA
#define PLATFORM_3DS 1
#define PORT_BRIDGE 1
#define CTR_LANG_PT_BR 0
#define PORT_LOG(...) ((void)0)
static const void *stub=(void*)0x1000;static u8 *payload;static u32 payloadSize;
static const char *assetName;
static const char *Port_GetAssetPath(const void*p){return p==stub?assetName:NULL;}
static bool Port_IsAssetStub(const void*p){return p==stub;}
static u32 Port_GetAssetSize(const void*p){return p==stub?payloadSize:0;}
static u32 Port_GetDecompressedAssetSize(const void*p){(void)p;return 0;}
static const void *Port_ResolveAssetPointer(const void*p){return p==stub?payload:p;}
static bool Port_LoadAssetPointerToBufferSized(const void*p,void*out,u32 n){if(p!=stub||n!=payloadSize)return false;memcpy(out,payload,n);return true;}
static bool Port_LoadAssetPointerToHeap(const void*p,u8**b,u32*n){(void)p;(void)b;(void)n;return false;}
static void *Alloc(size_t n){void*p=malloc(n);assert(p);memset(p,0xCD,n);return p;}
static void Free(void*p){free(p);}
static void Port_SetAssetDebugEx(unsigned a,...){(void)a;}
static void Port_SetGfxTilesetDebug(unsigned a,...){(void)a;}
static void CpuCopy32(const void*p,void*q,unsigned n){memcpy(q,p,n);}
static void DecompressionError(const void*p,unsigned e){(void)p;(void)e;assert(!"invalid compression header");}
#define HEADER_ERROR 1
static uint32_t CPUReadMemory(const void*p){return *(const uint32_t*)p;}
static uint8_t CPUReadByte(const void*p){return *(const uint8_t*)p;}
static void CPUWriteByte(void*p,uint8_t v){*(uint8_t*)p=v;}
void LZ77UnCompWram(const u32*,void*);
void LZ77UnCompVram(const u32*p,void*q){LZ77UnCompWram(p,q);}
void FastLZ77UnCompWram(const u32*p,void*q){LZ77UnCompWram(p,q);}
'''


def source(tree):
    decode=(tree/'src/decompress.c').read_text()
    header=(tree/'include/decompress.h').read_text()
    bios=(tree/'src/platform/bios.c').read_text()
    padding=re.search(r'^#define CTR_ASSET_READ_PADDING .+$',(ROOT/'3ds_port/include/3ds_assets.h').read_text(),re.M)[0]
    code=BASE+'\n'+padding+'\n'+function((ROOT/'3ds_port/src/3ds_assets.c').read_text(),'static u8 *AllocatePayload(')
    code+=header[header.index('#define MAX_DECOMPRESSION_BUFFER_SIZE'):header.index('void DecompressDataWithHeaderVram')]
    code+='\nstatic void SmolDecompressData(const struct SmolHeader*,const u32*,void*);\n'
    code+='static void SmolDecompressTilemap(const struct SmolTilemapHeader*,const u32*,u16*);\n'
    code+='static bool32 isModeLoEncoded(enum CompressionMode);\nstatic bool32 isModeSymEncoded(enum CompressionMode);\nstatic bool32 isModeSymDelta(enum CompressionMode);\n'
    code+=decode[decode.index('#define TABLE_READ_K'):decode.index('// Checks if `ptr`')]
    code+=decode[decode.index('#define REP0(X)'):decode.index('void LoadSpecialPokePic(')]
    for sig in ('void DecompressDataWithHeaderVram(', 'void DecompressDataWithHeaderWram(', 'u32 GetDecompressedDataSize('):
        code+=function(decode,sig)
    code+=function(bios,'static bool32 Port_IsValidLz77Header(')
    code+=function(bios,'static bool32 Port_RejectInvalidLz77Source(')
    code+=function(bios,'void LZ77UnCompWram(')
    code+=function((tree/'src/menu.c').read_text(),'void *malloc_and_decompress(')
    title=(tree/'src/title_screen.c').read_text()
    for symbol in ('gTitleScreenPokemonLogoGfx','gTitleScreenPokemonLogoTilemap'):
        callee=re.search(r'^\s*(\w+)\('+symbol+r',',title,re.M)[1]
        code+=f'\nstatic void Load_{symbol}(const u32 *p,void *d){{{callee}(p,d);}}\n'
    code+=r'''
static void *readFile(const char*path,u32*n){FILE*f=fopen(path,"rb");assert(f);fseek(f,0,SEEK_END);*n=ftell(f);rewind(f);void*p=AllocatePayload(*n);assert(p&&fread(p,1,*n,f)==*n);fclose(f);return p;}
int main(int argc,char**argv){
 assert(argc==4);assetName=argv[1];payload=readFile(argv[2],&payloadSize);
 u32 expectedSize;u8 *expected=readFile(argv[3],&expectedSize);
 assert(GetDecompressedDataSize((u32*)payload)==expectedSize);
 u8 *out=malloc(expectedSize);memset(out,0xCD,expectedSize);
 DecompressDataWithHeaderWram((u32*)stub,out);
 assert(!memcmp(out,expected,expectedSize));free(out);
 u32 heapSize=0;out=malloc_and_decompress(stub,&heapSize);
 if(!out||heapSize!=expectedSize||memcmp(out,expected,expectedSize)){
  fprintf(stderr,"FAIL production heap decode %s: mode=%u size=%u expected=%u\n",assetName,payload[0]&15,heapSize,expectedSize);
  free(out);free(expected);free(payload);return 1;
 }
 if(strstr(assetName,"/title_screen/pokemon_logo.png.")){
  memset(out,0xCD,heapSize);Load_gTitleScreenPokemonLogoGfx((const u32*)stub,out);
  assert(!memcmp(out,expected,expectedSize));
 }
 if(strstr(assetName,"/title_screen/pokemon_logo.bin.")){
  memset(out,0xCD,heapSize);Load_gTitleScreenPokemonLogoTilemap((const u32*)stub,out);
  assert(!memcmp(out,expected,expectedSize));
 }
 free(out);free(expected);free(payload);return 0;
}
'''
    return code


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--tree',type=Path,required=True)
    ap.add_argument('--code-tree',type=Path,help='compile codec/helper from a separate fresh source bootstrap')
    ap.add_argument('--pak',type=Path,required=True)
    ap.add_argument('--cc',default='gcc')
    ap.add_argument('--scope',choices=('intro','tilesets','all'),default='all')
    a=ap.parse_args();tree=a.tree.resolve()
    cases=[]
    for row in (tree/'3ds_port/romfs/assets/asset_map.txt').read_text().splitlines():
        if not row or row.startswith('#'):continue
        _,_,path=row.split(maxsplit=2)
        intro=any(x in path for x in ('/intro/','/expansion_intro/','/title_screen/'))
        tileset=path.startswith('data/tilesets/') or '/data/tilesets/' in path
        representative=any('/pokemon/'+mon+'/' in path for mon in
                           ('bulbasaur','chikorita','torchic','poochyena','vigoroth','turtwig','snivy',
                            'chespin','rowlet','grookey','sprigatito','floragato','lechonk'))
        if not ((intro and a.scope!='tilesets') or (tileset and a.scope!='intro')
                or (representative and a.scope=='all')):continue
        suffix=next((s for s in ('.smol','.fastSmol','.smolTM','.lz') if path.endswith(s)),None)
        if not suffix:continue
        raw=path[:-len(suffix)]
        expected=tree/raw
        if not expected.is_file():expected=tree/raw.removeprefix('build/assets/')
        if expected.is_file():cases.append((path,expected))
    assert len(cases)>=20, f'not enough raw/native intro comparisons: {len(cases)}'
    with tempfile.TemporaryDirectory() as tmp:
        d=Path(tmp);c=d/'test.c';exe=d/'decode';c.write_text(source(a.code_tree.resolve() if a.code_tree else tree))
        subprocess.run([a.cc,'-std=gnu11','-O1','-g','-fno-pie','-no-pie',
                        '-fsanitize=address,undefined','-fno-omit-frame-pointer',
                        '-Wno-pointer-to-int-cast',str(c),'-o',str(exe)],check=True)
        failed=[]
        with PakReader(a.pak) as pack:
            for i,(path,expected) in enumerate(cases):
                compressed=d/f'input-{i}.bin';compressed.write_bytes(pack.read(path))
                result=subprocess.run([str(exe),path,str(compressed),str(expected)])
                if result.returncode:failed.append(path)
        if failed:raise SystemExit(f'FAIL: {len(failed)}/{len(cases)} production intro heap decodes')
    print(f'PASS: {len(cases)} actual intro/title/tileset compressed pack assets through production codecs + heap helper; raw-input byte parity (host ASan/UBSan)')


if __name__=='__main__':main()
