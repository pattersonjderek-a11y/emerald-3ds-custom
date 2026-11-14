"""Execute the production expansion category adapter for upstream's split toggle."""
import argparse
from pathlib import Path
import subprocess,tempfile
from voxel_runtime_test import function
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--tree',type=Path,required=True);p.add_argument('--cc',default='cc');a=p.parse_args()
source=(ROOT/'3ds_port/src/3ds_expansion.c').read_text()
constants=(a.tree/'include/constants/moves.h').read_text()
# Categories and types come from native headers through their enum definitions.
import re
actual=(a.tree/'include/constants/pokemon.h').read_text()
types=re.search(r'enum (?:__attribute__\(\(packed\)\) )?Type\s*\{.*?\};',actual,re.S)[0]
category=re.search(r'enum (?:__attribute__\(\(packed\)\) )?DamageCategory\s*\{.*?\};',constants,re.S)
if not category:
 category=re.search(r'enum (?:__attribute__\(\(packed\)\) )?DamageCategory\s*\{.*?\};',actual,re.S)
assert category
code='''#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define GEN_3 3
#define GEN_4 4
#define GEN_6 6
#define GEN_9 9
'''+types+category[0]+'''
static unsigned split;
static unsigned CtrExtras_Get(const char *key){assert(!strcmp(key,"move_split"));return split;}
static unsigned GetMoveType(uint16_t move){return move;}
'''
code+=function(source,'uint8_t MoveSplitEnabled(')+function(source,'uint8_t CtrExpansion_MoveCategory(')
code+='''
int main(void){
 for(unsigned mode=0;mode<2;++mode){split=mode;
  for(unsigned type=0;type<NUMBER_OF_MON_TYPES;++type){
   assert(CtrExpansion_MoveCategory(type,DAMAGE_CATEGORY_NONE)==DAMAGE_CATEGORY_NONE);
   assert(CtrExpansion_MoveCategory(type,DAMAGE_CATEGORY_STATUS)==DAMAGE_CATEGORY_STATUS);
   for(unsigned native=DAMAGE_CATEGORY_PHYSICAL;native<=DAMAGE_CATEGORY_SPECIAL;++native)
    assert(CtrExpansion_MoveCategory(type,native)==(mode?native:type>=TYPE_FIRE?DAMAGE_CATEGORY_SPECIAL:DAMAGE_CATEGORY_PHYSICAL));
  }
 }
 puts("Production split adapter PASS: status/none preserved, upstream OFF type categories, ON native categories, all native types");
}
'''
with tempfile.TemporaryDirectory() as d:
 f=Path(d)/'test.c';f.write_text(code);exe=Path(d)/'test'
 subprocess.run([a.cc,'-std=c11','-Wall','-Werror','-fsanitize=address,undefined','-fno-pie','-no-pie',str(f),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
