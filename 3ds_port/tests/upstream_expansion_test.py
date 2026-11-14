"""v0.5.0 production core and expansion settings/ID adapters (host, no ARM execution)."""
import argparse
from pathlib import Path
import subprocess,tempfile
from voxel_runtime_test import function
ROOT=Path(__file__).resolve().parents[2]

def main():
 p=argparse.ArgumentParser();p.add_argument('--tree',type=Path,required=True);p.add_argument('--cc',default='cc');a=p.parse_args()
 actual=(ROOT/'3ds_port/src/3ds_randomizer.c').read_text()
 code=r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "3ds_randomizer.h"
typedef uint16_t u16;typedef uint32_t u32;
#define NUM_SPECIES 1600
#define CTR_LOG_GAME 1
#define CtrLog_Write(...) ((void)0)
static struct{unsigned baseHP;}gSpeciesInfo[NUM_SPECIES];
static u16 bases[NUM_SPECIES];
#define GET_BASE_SPECIES_ID(s) bases[s]
static u16 SpeciesToNationalPokedexNum(u16 s){return s<=1025?s:0;}
static u16 NationalPokedexNumToSpecies(u16 n){return n<=1025?n:0;}
static int settings[3],seed;
static int CtrSettings_GetInt(const char *key,int def){(void)def;
 if(!strcmp(key,"rand_seed"))return seed;
 return settings[!strcmp(key,"rand_wild")?0:!strcmp(key,"rand_starters")?1:2];
}
static const char *const sKindKeys[CTR_RANDOMIZE_KINDS]={"rand_wild","rand_starters","rand_trainers"};
static CtrRandomizerTable sTable;static bool sTableBuilt;
'''
 for signature in ['static u16 ToNational(','static u16 ToSpecies(','bool CtrRandomizer_Enabled(','uint32_t CtrRandomizer_Seed(','uint16_t CtrRandomizer_Species(']:code+=function(actual,signature)
 code+=r'''
int main(void){
 for(unsigned i=1;i<NUM_SPECIES;++i){bases[i]=i;gSpeciesInfo[i].baseHP=50;}
 CtrRandomizerTable first,second;bool seen[1026]={0};
 CtrRandomizer_Build(&first,42);CtrRandomizer_Build(&second,42);assert(!memcmp(&first,&second,sizeof(first)));
 unsigned gen9=0;
 for(unsigned i=1;i<=1025;++i){u16 n=first.map[i];assert(n&&n<=1025&&!seen[n]);seen[n]=true;if(n>=906)++gen9;}
 assert(gen9==120); // every National Dex number appears exactly once
 CtrRandomizer_Build(&second,43);assert(memcmp(first.map,second.map,sizeof(first.map)));
 assert(!CtrRandomizer_MapNational(NULL,1)&&!CtrRandomizer_MapNational(&first,1026));
 seed=42;assert(CtrRandomizer_Species(CTR_RANDOMIZE_WILD,252)==252);
 settings[0]=settings[1]=settings[2]=1;
 for(unsigned i=1;i<=1025;++i){
  u16 expected=first.map[i];
  assert(CtrRandomizer_Species(CTR_RANDOMIZE_WILD,i)==expected);
  assert(CtrRandomizer_Species(CTR_RANDOMIZE_STARTERS,i)==expected);
  assert(CtrRandomizer_Species(CTR_RANDOMIZE_TRAINERS,i)==expected);
 }
 settings[0]=0;assert(CtrRandomizer_Species(CTR_RANDOMIZE_WILD,252)==252);
 assert(CtrRandomizer_Species(CTR_RANDOMIZE_STARTERS,252)==first.map[252]);
 seed=43;assert(CtrRandomizer_Species(CTR_RANDOMIZE_TRAINERS,252)==second.map[252]);
 seed=42;assert(CtrRandomizer_Species(CTR_RANDOMIZE_TRAINERS,252)==first.map[252]);
 bases[1100]=25;assert(CtrRandomizer_Species(CTR_RANDOMIZE_TRAINERS,1100)==1100);
 gSpeciesInfo[900].baseHP=0;assert(CtrRandomizer_Species(CTR_RANDOMIZE_TRAINERS,900)==900);
 assert(CtrRandomizer_Species(CTR_RANDOMIZE_TRAINERS,65535)==65535);
 settings[2]=2;assert(!CtrRandomizer_Enabled(CTR_RANDOMIZE_TRAINERS));
 seed=-1;assert(CtrRandomizer_Seed()==0x7fffffff);
 printf("Production v0.5.0 core/adapters PASS: 1025-entry bijection, Gen 9, global mutable seed/toggles, shared permutation, native ID/form guards. Seed 42 starter nationals %u/%u/%u\n",first.map[252],first.map[255],first.map[258]);
}
'''
 with tempfile.TemporaryDirectory() as d:
  f=Path(d)/'test.c';f.write_text(code);exe=Path(d)/'test'
  subprocess.run([a.cc,'-DPORT_EXPANSION','-std=gnu11','-g','-O1','-fsanitize=address,undefined','-fno-pie','-no-pie','-I'+str(ROOT/'3ds_port/include'),str(f),str(ROOT/'3ds_port/src/3ds_randomizer_core.c'),'-o',str(exe)],check=True)
  subprocess.run([str(exe)],check=True)
if __name__=='__main__':main()
