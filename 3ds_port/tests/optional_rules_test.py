"""Execute production optional resolvers/native hooks using synthetic engine boundaries."""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile
from voxel_runtime_test import function
ROOT=Path(__file__).resolve().parents[2]

def source(tree):
    native=(ROOT/'3ds_port/src/3ds_optional_game.c').read_text()
    constants=set(re.findall(r'\b(?:ABILITY_|ITEM_|HOLD_EFFECT_|FORM_CHANGE_|BATTLE_TYPE_|MON_DATA_|POCKET_)[A-Z_0-9]+\b',native))
    out='#include <assert.h>\n#include <stdio.h>\n#include <string.h>\n#include "3ds_optional.h"\n'
    prefixes=['ABILITY_','ITEM_','HOLD_EFFECT_','FORM_CHANGE_','BATTLE_TYPE_','MON_DATA_','POCKET_']
    for prefix in prefixes:
        for i,name in enumerate(sorted(x for x in constants if x.startswith(prefix))):
            value=1<<i if prefix=='BATTLE_TYPE_' else i+1
            out+=f'#define {name} {value}u\n'
    out+='''
#define PORT_EXPANSION 1
#define PORT_BRIDGE 1
#define NUM_SPECIES 16
#define NUM_ABILITY_SLOTS 3
#define ABILITIES_COUNT 512
#define ITEMS_COUNT 512
#define PARTY_SIZE 6
#define ARRAY_COUNT(a) (sizeof(a)/sizeof((a)[0]))
typedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32;
static struct {bool inBattle;} gMain;
static u32 gBattleTypeFlags,seed;
static int options[3];
static int CtrSettings_GetInt(const char *key,int def) {
 (void)def;return options[strcmp(key,"rand_abilities")==0?0:strcmp(key,"rand_field_items")==0?1:2];
}
static u32 CtrRandomizer_Seed(void){return seed;}
struct FormChange{unsigned method,param1;};
struct SpeciesInfo{u16 abilities[3];const struct FormChange *formChangeTable;};
static struct SpeciesInfo gSpeciesInfo[NUM_SPECIES];
static u16 bases[NUM_SPECIES];
#define GET_BASE_SPECIES_ID(s) bases[s]
struct AbilityInfo{bool cantBeSwapped,cantBeSuppressed,cantBeOverwritten;};
static struct AbilityInfo gAbilitiesInfo[ABILITIES_COUNT];
static struct {unsigned importance,pocket,effect;} items[ITEMS_COUNT];
static unsigned GetItemImportance(u16 x){assert(x<ITEMS_COUNT);return items[x].importance;}
static unsigned GetItemPocket(u16 x){assert(x<ITEMS_COUNT);return items[x].pocket;}
static unsigned GetItemHoldEffect(u16 x){assert(x<ITEMS_COUNT);return items[x].effect;}
static struct{struct{u8 mapGroup,mapNum;}location;}save1;
#define gSaveBlock1Ptr (&save1)
struct Pokemon{u16 species,item;};static struct Pokemon gEnemyParty[6];
static unsigned GetMonData(struct Pokemon *p,unsigned what){return what==MON_DATA_SPECIES?p->species:p->item;}
static void SetMonData(struct Pokemon *p,unsigned what,const u16 *value){assert(what==MON_DATA_HELD_ITEM);p->item=*value;}
'''
    out+=re.sub(r'^#include .*\n','',native,flags=re.M)
    ball=(tree/'src/item_ball.c').read_text()
    out+='''
#define MAX_BAG_ITEM_CAPACITY 999
#define ITEM_NONE 0
struct ObjectEventTemplate{unsigned localId,movementRangeX,trainerRange_berryTreeId;};
static struct{struct{unsigned objectEventCount;const struct ObjectEventTemplate*objectEvents;}*events;}gMapHeader;
static u16 gSpecialVar_LastTalked,gSpecialVar_Result,gSpecialVar_0x8009;
enum Item{TEST_ITEM};
'''
    for sig in ['static u32 GetItemBallAmountFromTemplate(u32 itemBallId)','static u32 GetItemBallIdFromTemplate(u32 itemBallId)','void GetItemBallIdAndAmountFromTemplate(void)']:
        out+=function(ball,sig)
    out+='''
int main(void){
 const u16 pool[]={1,2,3,4},ex[]={1,3};
 assert(!CtrOptional_Pick(NULL,4,3,NULL,0));
 assert(!CtrOptional_Pick(pool,0,3,NULL,0));
 assert(!CtrOptional_Pick(pool,4,3,pool,4));
 for(unsigned n=0;n<2000;++n){u16 pick=CtrOptional_Pick(pool,4,n,ex,2);assert(pick==2||pick==4);}
 for(unsigned s=0;s<NUM_SPECIES;++s)bases[s]=s;
 gSpeciesInfo[1].abilities[0]=ABILITY_STATIC;gSpeciesInfo[1].abilities[1]=ABILITY_DAMP;
 gSpeciesInfo[2].abilities[0]=ABILITY_STATIC;gSpeciesInfo[2].abilities[1]=ABILITY_STATIC;
 gSpeciesInfo[3].abilities[0]=ABILITY_PURE_POWER;
 static const struct FormChange forms[]={{FORM_CHANGE_ITEM_HOLD,ITEM_LEFTOVERS},{FORM_CHANGE_TERMINATOR,0}};
 gSpeciesInfo[4].abilities[0]=ABILITY_STATIC;gSpeciesInfo[4].formChangeTable=forms;
 options[0]=1;options[1]=1;options[2]=1;seed=42;
 u16 ability=CtrOptional_Ability(1,0,ABILITY_STATIC);
 assert(ability && CtrOptional_Ability(1,0,ABILITY_STATIC)==ability);
 assert(CtrOptional_Ability(1,1,ABILITY_DAMP)!=ability);
 assert(CtrOptional_Ability(1,2,0)==0);
 assert(CtrOptional_Ability(2,0,ABILITY_STATIC)==CtrOptional_Ability(2,1,ABILITY_STATIC));
 assert(CtrOptional_Ability(3,0,ABILITY_PURE_POWER)==ABILITY_PURE_POWER);
 assert(CtrOptional_Ability(4,0,ABILITY_STATIC)==ABILITY_STATIC);
 assert(CtrOptional_Ability(NUM_SPECIES,0,ABILITY_STATIC)==ABILITY_STATIC);
 assert(CtrOptional_Ability(1,3,ABILITY_STATIC)==ABILITY_STATIC);
 for(unsigned i=0;i<100;++i){seed=i;u16 a=CtrOptional_Ability(1,0,ABILITY_STATIC);assert(a&&a!=ABILITY_PURE_POWER);}
 seed=42;assert(CtrOptional_Ability(1,0,ABILITY_STATIC)==ability);
 gMain.inBattle=true;gBattleTypeFlags=BATTLE_TYPE_LINK;
 assert(CtrOptional_Ability(1,0,ABILITY_STATIC)==ABILITY_STATIC);
 assert(CtrOptional_Held(ITEM_ORAN_BERRY,1,0)==ITEM_ORAN_BERRY);
 gMain.inBattle=false; // stale battle flags do not disable field effects
 assert(CtrOptional_Ability(1,0,ABILITY_STATIC)==ability);
 gBattleTypeFlags=0;
 items[400].importance=1;items[401].pocket=POCKET_TM_HM;items[402].pocket=POCKET_KEY_ITEMS;
 assert(CtrOptional_Field(0,0,1)==0);
 assert(CtrOptional_Field(400,0,1)==400&&CtrOptional_Field(401,0,1)==401&&CtrOptional_Field(402,1,1)==402);
 assert(CtrOptional_Field(ITEM_MASTER_BALL,0,1)==ITEM_MASTER_BALL);
 assert(CtrOptional_Held(ITEM_LEFTOVERS,1,0)==ITEM_LEFTOVERS);
 for(unsigned n=0;n<2000;++n){seed=n;
  assert(CtrOptional_Held(ITEM_ORAN_BERRY,1,0)!=ITEM_LEFTOVERS);
  assert(CtrOptional_Field(ITEM_ORAN_BERRY,0,3)!=ITEM_LEFTOVERS);
 }
 seed=42;save1.location.mapGroup=1;save1.location.mapNum=2;
 u16 field=CtrOptional_Field(ITEM_ORAN_BERRY,0,7),held=CtrOptional_Held(ITEM_ORAN_BERRY,100,0);
 options[0]=0;assert(CtrOptional_Field(ITEM_ORAN_BERRY,0,7)==field);
 options[1]=0;assert(CtrOptional_Held(ITEM_ORAN_BERRY,100,0)==held);
 assert(CtrOptional_Ability(1,0,ABILITY_STATIC)==ABILITY_STATIC);
 assert(CtrOptional_Field(ITEM_ORAN_BERRY,0,7)==ITEM_ORAN_BERRY);
 options[1]=1;
 struct ObjectEventTemplate objects[]={{9,5,ITEM_ORAN_BERRY},{42,0,ITEM_POTION}};
 typeof(*gMapHeader.events) events={2,objects};gMapHeader.events=&events;
 gSpecialVar_LastTalked=42;GetItemBallIdAndAmountFromTemplate();assert(gSpecialVar_Result==CtrOptional_Field(ITEM_POTION,0,42)&&gSpecialVar_0x8009==1);
 gSpecialVar_LastTalked=9;GetItemBallIdAndAmountFromTemplate();assert(gSpecialVar_0x8009==5);
 gSpecialVar_LastTalked=99;GetItemBallIdAndAmountFromTemplate();assert(gSpecialVar_Result==0&&gSpecialVar_0x8009==0);
 gMapHeader.events=NULL;GetItemBallIdAndAmountFromTemplate();assert(gSpecialVar_Result==0);
 gEnemyParty[0]=(struct Pokemon){1,ITEM_ORAN_BERRY};gEnemyParty[1]=(struct Pokemon){2,0};
 CtrOptional_WildHeld();assert(gEnemyParty[0].item&&gEnemyParty[1].item==0);
 gMain.inBattle=true;gBattleTypeFlags=BATTLE_TYPE_CATCH_TUTORIAL;
 gEnemyParty[0].item=ITEM_POTION;CtrOptional_WildHeld();assert(gEnemyParty[0].item==ITEM_POTION);
 puts("Production optional rules: determinism, independent streams, ability slots/forms, progression items, native item balls, wild held items PASS");
}
'''
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--tree',type=Path,required=True);p.add_argument('--cc',default='cc');a=p.parse_args()
    with tempfile.TemporaryDirectory() as d:
        path=Path(d);(path/'test.c').write_text(source(a.tree.resolve()))
        subprocess.run([a.cc,'-std=gnu11','-g','-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(ROOT/'3ds_port/include'),str(path/'test.c'),str(ROOT/'3ds_port/src/3ds_optional_core.c'),'-o',str(path/'test')],check=True)
        subprocess.run([str(path/'test')],check=True)
if __name__=='__main__':main()
