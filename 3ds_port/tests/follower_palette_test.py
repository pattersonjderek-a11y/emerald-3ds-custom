"""Production expansion follower bounds/palette selection under ASan/UBSan."""
import argparse
from pathlib import Path
import subprocess,tempfile
from voxel_runtime_test import function

def main():
 p=argparse.ArgumentParser();p.add_argument('--tree',type=Path,required=True);p.add_argument('--cc',default='cc');a=p.parse_args()
 actual=(a.tree/'src/event_object_movement.c').read_text()
 code=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
typedef uint16_t u16;typedef uint32_t u32;typedef unsigned bool32;
enum Species{SPECIES_NONE,SPECIES_ONE,SPECIES_UNOWN};
#define NUM_SPECIES 8
#define OW_POKEMON_OBJECT_EVENTS 1
#define OW_PKMN_OBJECTS_SHARE_PALETTES 0
#define OW_SUBSTITUTE_PLACEHOLDER 1
#define P_GENDER_DIFFERENCES 1
#define OBJ_EVENT_PAL_TAG_DYNAMIC 9
#define TAG_NONE 65535
#define OBJ_EVENT_MON 100
#define OBJ_EVENT_MON_SHINY 1024
#define OBJ_EVENT_MON_FEMALE 2048
#define TRUE 1
#define FALSE 0
#define WEATHER_FOG_HORIZONTAL 1
struct ObjectEventGraphicsInfo{u16 tileTag,paletteTag;const void*oam,*images,*anims;};
struct SpeciesInfo{struct ObjectEventGraphicsInfo overworldData,overworldDataFemale;
const u16 *overworldPalette,*overworldShinyPalette,*overworldPaletteFemale,*overworldShinyPaletteFemale;};
static struct SpeciesInfo gSpeciesInfo[NUM_SPECIES];
struct SpritePalette{const u16*data;u16 tag;};
static struct{unsigned currWeather;}weather;
#define gWeatherPtr (&weather)
static const u16 normal[16]={1},shiny[16]={2},female[16]={3},femaleShiny[16]={4};
static const u16 *last;static unsigned cacheTag=65535,cacheSlot=255,loads,blends;static bool fail;
static u32 IndexOfSpritePaletteTag(u16 tag){return tag==cacheTag?cacheSlot:255;}
static u32 LoadSpritePalette(const struct SpritePalette *p){last=p->data;loads++;if(fail)return 255;cacheTag=p->tag;cacheSlot=3;return 3;}
static const u16 *GetMonSpritePalFromSpecies(unsigned s,bool32 sh,bool32 f){(void)s;(void)f;return sh?shiny:normal;}
static void LoadSpritePaletteWithTag(const u16*p,u16 tag){struct SpritePalette x={p,tag};LoadSpritePalette(&x);}
static void UpdateSpritePaletteWithWeather(unsigned n,bool32 b){(void)b;assert(n<16);blends++;}
'''
 code+=function(actual,'const struct ObjectEventGraphicsInfo *SpeciesToGraphicsInfo(enum Species species, bool32 shiny, bool32 female)\n{')
 code+=function(actual,'static u32 LoadDynamicFollowerPalette(enum Species species, bool32 shiny, bool32 female)\n{')
 code+=r'''
int main(void){
 gSpeciesInfo[0].overworldData=(struct ObjectEventGraphicsInfo){1,9,(void*)1,(void*)1,(void*)1};
 gSpeciesInfo[1].overworldData=gSpeciesInfo[0].overworldData;
 gSpeciesInfo[1].overworldDataFemale=gSpeciesInfo[0].overworldData;
 gSpeciesInfo[1].overworldPalette=normal;gSpeciesInfo[1].overworldShinyPalette=shiny;
 gSpeciesInfo[1].overworldPaletteFemale=female;gSpeciesInfo[1].overworldShinyPaletteFemale=femaleShiny;
 assert(SpeciesToGraphicsInfo(8000,0,0)==&gSpeciesInfo[0].overworldData);
 assert(SpeciesToGraphicsInfo(1,0,1)==&gSpeciesInfo[1].overworldDataFemale);
 gSpeciesInfo[1].overworldDataFemale.images=0;
 assert(SpeciesToGraphicsInfo(1,0,1)==&gSpeciesInfo[0].overworldData);
 assert(LoadDynamicFollowerPalette(1,0,0)==3&&last==normal);
 unsigned prev=loads;assert(LoadDynamicFollowerPalette(1,0,0)==3&&loads==prev);
 assert(LoadDynamicFollowerPalette(1,1,0)==3&&last==shiny);
 assert(LoadDynamicFollowerPalette(1,0,1)==3&&last==female);
 assert(LoadDynamicFollowerPalette(1,1,1)==3&&last==femaleShiny);
 gSpeciesInfo[1].overworldShinyPaletteFemale=0;cacheTag=65535;
 assert(LoadDynamicFollowerPalette(1,1,1)==3&&last==shiny);
 assert(LoadDynamicFollowerPalette(9000,0,0)==255);
 cacheTag=65535;fail=true;prev=blends;
 assert(LoadDynamicFollowerPalette(1,0,0)==255&&blends==prev);
 puts("Production follower: bounds, incomplete mappings, normal/shiny/female palettes, cache tags, allocation failure PASS");
}
'''
 with tempfile.TemporaryDirectory() as d:
  f=Path(d)/'test.c';f.write_text(code);exe=Path(d)/'test'
  subprocess.run([a.cc,'-std=gnu11','-O1','-g','-fsanitize=address,undefined','-fno-pie','-no-pie',str(f),'-o',str(exe)],check=True)
  subprocess.run([str(exe)],check=True)
if __name__=='__main__':main()
