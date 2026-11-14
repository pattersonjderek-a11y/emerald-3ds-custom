"""Execute native UI/Dex picture paths with compressed tiles and RAW palettes."""
import argparse
from pathlib import Path
import subprocess,tempfile
from voxel_runtime_test import function
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--tree',type=Path,required=True);p.add_argument('--cc',default='cc');a=p.parse_args()
base=r'''
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#define PORT_EXPANSION 1
#define TRUE 1
#define FALSE 0
#define SPECIES_NONE 0
#define CTR_UI_SPECIES_LIMIT 3
#define FRAME_BYTES 2048
#define CTR_DEX_TOP_DIM 64
typedef uint8_t u8;typedef uint16_t u16;typedef uint32_t u32;typedef unsigned bool8;
static u8 picture[4096];static u16 normal[16],shinyPal[16];static bool missing;static u32 paletteSize=32;
#define CtrFrontPic(s) ((const void*)picture)
#define CtrNormalPal(s) ((const void*)normal)
#define CtrShinyPal(s) ((const void*)shinyPal)
static const void *Port_ResolveAssetPointerSized(const void*p,unsigned size){assert(size<=paletteSize);return missing?NULL:p;}
static bool Port_IsAssetStub(const void*p){(void)p;return missing;}
static u32 Port_GetAssetSizeSized(const void*p,unsigned size){(void)p;(void)size;return missing?0:paletteSize;}
static u32 Port_GetAssetSizeExact(const void*p){(void)p;return missing?0:paletteSize;}
static bool Port_LoadAssetRangeToBuffer(const void*p,u32 offset,void*out,u32 size){assert(!offset&&size<=paletteSize);memcpy(out,p,size);return true;}
static void *HeapUnlz(const void *p,u32 *n){assert(p==picture);void *out=malloc(sizeof(picture));memcpy(out,picture,sizeof(picture));if(n)*n=sizeof(picture);return out;}
static u32 BufferUnlz(const void *p,void *out,u32 capacity){assert(p==picture&&capacity>=sizeof(picture));memcpy(out,picture,sizeof(picture));return sizeof(picture);}
static u16 CtrVideo_RGBA5551(u16 p){return p;}
#define gBagFemaleTiles picture
#define gBagMaleTiles picture
#define gBagPalette normal
typedef struct{u16 c[16];}Pal;
static void ToPals(Pal*p,const u16*raw,unsigned count){assert(count==1);memcpy(p->c,raw,32);}
#define FRONT_SLOTS 2
static struct{u16 species;bool8 shiny,valid,loaded;u32 age;u8 tiles[2048];Pal pal;}sFronts[FRONT_SLOTS];
static struct{bool8 female,valid,loaded;u8 frame;u8 tiles[2048];Pal pal;}sBagPic;
static bool sIconBudget=true;static u32 sIconClock;
'''
ui=(ROOT/'3ds_port/src/3ds_bottom_ui.c').read_text();dex=(ROOT/'3ds_port/src/3ds_dex_top_game.c').read_text()
code=base+function(ui,'static void PalSymbol(const void *src, Pal *dst, int count)\n{')+function((ROOT/'3ds_port/include/3ds_engine_compat.h').read_text(),'static inline bool8 CtrUI_ReadPalette(')+'#define Unlz HeapUnlz\n'+function(ui,'static int FrontPic(')+function(ui,'static int BagPic(')+'\n#undef Unlz\n#define Unlz BufferUnlz\n'+function(dex,'static unsigned DecodePicture(')
code+=r'''
int main(void){
 for(unsigned i=0;i<16;++i){normal[i]=i+100;shinyPal[i]=i+200;}
 memset(picture,0x11,sizeof(picture));
 int first=FrontPic(1,false);assert(first>=0&&!memcmp(sFronts[first].pal.c,normal,32));
 sIconBudget=true;int shiny=FrontPic(1,true);assert(shiny>=0&&shiny!=first&&!memcmp(sFronts[shiny].pal.c,shinyPal,32));
 assert(FrontPic(1,false)==first); // cache identity is species AND shiny
 static u16 pixels[64*64*2];assert(DecodePicture(1,pixels)==2);
 for(unsigned i=0;i<64*64*2;++i)assert(pixels[i]==normal[1]);
 sIconBudget=true;assert(BagPic(false,0)==0 && !memcmp(sBagPic.pal.c,normal,32));
 sIconBudget=true;assert(BagPic(true,1)==0);assert(BagPic(true,1)==0);
 assert(!DecodePicture(65535,pixels));
 u16 shortPal[16];paletteSize=26;assert(CtrUI_ReadPalette(normal,shortPal));
 for(unsigned i=0;i<13;++i)assert(shortPal[i]==normal[i]);
 for(unsigned i=13;i<16;++i)assert(!shortPal[i]);
 assert(DecodePicture(1,pixels)==2);
 Pal expanded;memset(&expanded,0xFF,sizeof(expanded));PalSymbol(normal,&expanded,1);
 for(unsigned i=0;i<16;++i)assert(expanded.c[i]==(i<13?normal[i]:0));
 paletteSize=3;assert(!CtrUI_ReadPalette(normal,shortPal));paletteSize=32;
 missing=true;sIconBudget=true;assert(FrontPic(2,false)==-1);assert(!DecodePicture(2,pixels));
 assert(FrontPic(65535,false)==-1);
 puts("Production native UI/Dex assets PASS: compressed tile boundary, raw normal/shiny palettes, two-frame output, cache identity, missing palette and species bounds");
}
'''
with tempfile.TemporaryDirectory() as d:
 f=Path(d)/'test.c';f.write_text(code);exe=Path(d)/'test'
 subprocess.run([a.cc,'-std=gnu11','-g','-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',str(f),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
