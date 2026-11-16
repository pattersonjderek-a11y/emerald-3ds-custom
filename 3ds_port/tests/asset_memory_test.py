"""Run production asset allocation/cache policy against original-XL log values."""
from pathlib import Path
import argparse
import re
import subprocess
import tempfile
from voxel_runtime_test import function

PORT=Path(__file__).resolve().parents[1]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--cc',default='gcc');a=ap.parse_args()
    src=(PORT/'src/3ds_assets.c').read_text()
    code=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
typedef uint8_t u8;typedef uint32_t u32;typedef uint64_t u64;
#include "3ds_assets.h"
static unsigned room;
static u32 CtrPlatform_HeapAvailable(void){return room;}
static void CtrLock_Lock(unsigned*p){(void)p;}
static void CtrLock_Unlock(unsigned*p){(void)p;}
static unsigned sLock,sStamp,sEntryCount,sBudget;static bool sLoaded;
static struct CtrAssetStats sStats;
struct AssetPayload{u8*data;u32 size,stamp;};
static struct AssetPayload *sPayloads;
'''
    code+=function(src,'static u8 *AllocatePayload(')+function(src,'static u32 CacheBudgetForRoom(')
    code+=function(src,'void CtrAssets_Collect(')
    code+=r'''
int main(void){
 for(unsigned n=0;n<100;n++){
  u8*p=AllocatePayload(n);assert(p);for(unsigned i=0;i<n+CTR_ASSET_READ_PADDING;i++)assert(!p[i]);free(p);
 }
 assert(!AllocatePayload(UINT32_MAX));
 // Actual reported XL: 1,421 KiB before AgbMain, falling to 280 KiB
 // with 1,491 KiB of cached payloads, and failed 2x64KiB atlas scratch.
 assert(CacheBudgetForRoom(1421u*1024u,9u*1024u)<=256u*1024u);
 unsigned budget=CacheBudgetForRoom(280u*1024u,1491u*1024u);
 assert(budget<=256u*1024u);
 assert(280u*1024u+1491u*1024u-budget>=1024u*1024u);
 assert(CacheBudgetForRoom(64u*1024u*1024u,0)==CTR_ASSET_CACHE_BUDGET);
 assert(CacheBudgetForRoom(100u*1024u,0)==0);
 struct AssetPayload payloads[2]={{AllocatePayload(65536),65536,0},
                                 {AllocatePayload(65536),65536,100}};
 sLoaded=true;sStamp=100;sEntryCount=2;sPayloads=payloads;sStats.bytes=131072;room=100u*1024u;
 CtrAssets_Collect();assert(!payloads[0].data&&payloads[1].data&&sStats.bytes==65536&&sStats.evictions==1);
 for(unsigned i=0;i<6;i++)CtrAssets_Collect();
 assert(payloads[1].data); // preserve the upstream eight-frame grace
 CtrAssets_Collect();assert(!payloads[1].data&&!sStats.bytes&&sStats.evictions==2);
 puts("PASS production payload padding + cache: observed XL heap values, atlas reserve, high-memory ceiling, recent-pointer grace and reclamation (host ASan/UBSan)");
}
'''
    with tempfile.TemporaryDirectory() as tmp:
        f=Path(tmp)/'test.c';f.write_text(code);exe=Path(tmp)/'test'
        subprocess.run([a.cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror',
                        '-fsanitize=address,undefined','-fno-pie','-no-pie',
                        '-I'+str(PORT/'include'),str(f),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)


if __name__=='__main__':main()
