"""Run native follower selection/view eviction policies (host, not movement/GPU)."""
import argparse
from pathlib import Path
import subprocess,tempfile
from voxel_runtime_test import function
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--tree',type=Path,required=True);p.add_argument('--cc',default='cc');a=p.parse_args()
actual=(a.tree/'src/event_object_movement.c').read_text()
code=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include "3ds_field_view.h"
typedef uint8_t u8;typedef int16_t s16;typedef unsigned bool8;typedef unsigned u32;
#define MAP_OFFSET 7
#define TRUE 1
#define FALSE 0
#define PARTY_SIZE 6
#define B_TRAINER_PLAYER 0
#define MON_DATA_SPECIES_OR_EGG 1
#define SPECIES_NONE 0
#define OW_FOLLOWERS_ALLOWED_SPECIES 0
#define OW_FOLLOWERS_ALLOWED_MET_LVL 0
#define OW_FOLLOWERS_ALLOWED_MET_LOC 0
#define MON_DATA_MET_LEVEL 2
#define MON_DATA_MET_LOCATION 3
#define OBJECT_EVENTS_COUNT 16
#define OBJECT_EVENT_VIEW_MARGIN 2
#define OBJ_EVENT_ID_FOLLOWER 254
#define OBJ_EVENT_ID_NPC_FOLLOWER 253
#define OBJECT_EVENT_EVICT_GAP 4
struct Pokemon { unsigned species,hp;struct{bool isEgg,isBadEgg;}box;};
enum Species{SPECIES_TEST};
static struct Pokemon gParties[1][6];
static unsigned GetMonData(struct Pokemon *p,unsigned field){(void)field;return p->species;}
static unsigned VarGet(unsigned var){(void)var;return 0;}
struct ObjectEvent{bool active,isPlayer,frozen,heldMovementActive,exempt;u8 localId,mapNum,mapGroup;
 struct{s16 x,y;}currentCoords,initialCoords;};
static struct ObjectEvent gObjectEvents[16];
static struct{struct{s16 x,y;}pos;struct{u8 mapNum,mapGroup;}location;void *objectEventTemplates;}save;
#define gSaveBlock1Ptr (&save)
static struct{bool active;unsigned objEventId;}gLinkPlayerObjectEvents[2];
#define ARRAY_COUNT(a) (sizeof(a)/sizeof((a)[0]))
static CtrFieldView view;
static bool voxelMode;
bool CtrSettings_Voxel(void){return voxelMode;}
int CtrSettings_VoxelPitch(void){return 40;}
int CtrSettings_VoxelZoom(void){return 100;}
static bool IsOWEDespawnExempt(struct ObjectEvent *o){return o->exempt;}
static unsigned GetSpawnableObjectEventCount(void){return 1;}
static const void *FindObjectEventTemplateByLocalId(unsigned id,const void*p,unsigned count){(void)p;(void)count;return id==1?(void*)1:NULL;}
static void RemoveObjectEvent(struct ObjectEvent *o){o->active=false;}
'''
for sig in ['struct Pokemon *GetFirstLiveMon(','static void GetObjectEventWindow(','static float ObjectEventViewScore(','static bool8 IsLinkPlayerObjectEvent(','static bool8 IsInObjectEventWindow(','static bool8 CanEvictObjectEvent(','static bool8 HasFreeObjectEventSlot(','static bool8 EvictFurthestObjectEvent(','bool8 FreeObjectEventSlotNearPlayer(']:code+=function(actual,sig)
code+=r'''
int main(void){
 assert(GetFirstLiveMon()==NULL);
 gParties[0][0]=(struct Pokemon){.species=1,.hp=0};
 gParties[0][1]=(struct Pokemon){.species=2,.hp=10,.box.isEgg=true};
 gParties[0][2]=(struct Pokemon){.species=3,.hp=10,.box.isBadEgg=true};
 gParties[0][3]=(struct Pokemon){.species=4,.hp=10};
 assert(GetFirstLiveMon()==&gParties[0][3]);
 gParties[0][0].hp=10;assert(GetFirstLiveMon()==&gParties[0][0]);
 struct Pokemon swap=gParties[0][0];gParties[0][0]=gParties[0][3];gParties[0][3]=swap;
 assert(GetFirstLiveMon()->species==4); // party reorder is read afresh
 for(unsigned mode=0;mode<2;++mode){
  voxelMode=mode;
  if(mode)CtrFieldView_Voxel(&view,40,100);else CtrFieldView_Flat(&view);
  assert(FreeObjectEventSlotNearPlayer());
  for(unsigned i=0;i<16;++i)gObjectEvents[i]=(struct ObjectEvent){.active=true,.localId=1,.currentCoords={100,100},.initialCoords={100,100}};
  for(unsigned kind=0;kind<6;++kind){
   struct ObjectEvent protected={.active=true,.localId=1,.currentCoords={100,100},.initialCoords={100,100}};
   if(kind==0)protected.localId=OBJ_EVENT_ID_FOLLOWER;
   if(kind==1)protected.localId=OBJ_EVENT_ID_NPC_FOLLOWER;
   if(kind==2)protected.isPlayer=true;
   if(kind==3)protected.frozen=true;
   if(kind==4)protected.heldMovementActive=true;
   if(kind==5)protected.exempt=true;
   gObjectEvents[0]=protected;
   assert(!CanEvictObjectEvent(0,-10,10,-10,10));
  }
  assert(FreeObjectEventSlotNearPlayer());assert(!gObjectEvents[1].active);
  assert(gObjectEvents[0].active); // no follower/script eviction when slots fill
 }
 puts("Production follower policies PASS: fainted/egg/bad egg/empty party, reorder, 2D/voxel view, slot pressure, player/follower/NPC/script exemptions. Door/surf/bike/render tests need hardware.");
}
'''
with tempfile.TemporaryDirectory() as d:
 f=Path(d)/'test.c';f.write_text(code);exe=Path(d)/'test'
 subprocess.run([a.cc,'-std=c11','-g','-O1','-Wall','-Werror','-Wno-int-to-pointer-cast','-fsanitize=address,undefined','-fno-pie','-no-pie','-I'+str(ROOT/'3ds_port/include'),str(f),str(ROOT/'3ds_port/src/3ds_field_view.c'),'-lm','-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
