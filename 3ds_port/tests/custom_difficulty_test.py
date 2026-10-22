"""Execute Stage D production save, caps, AI and trainer hooks under ASan/UBSan.

Engine data and battle constructors use controlled fixtures; this is host testing,
not an emulator battle or a console playthrough.
"""
import argparse
from pathlib import Path
import re
from custom_random_test import compile_run
from voxel_runtime_test import function

HERE = Path(__file__).resolve().parent


def native(tree):
    source = (HERE / 'custom_random_fixture.h').read_text()
    source = source[:source.index('#define STARTER_MON_COUNT')]
    source = source.replace('unsigned n) { return n==0', 'unsigned n,...) { return n==0')
    source = source.replace('typedef uint8_t u8;', 'typedef uint64_t u64; typedef uint8_t u8;')
    source = source.replace('unsigned natDexNum,baseHP', 'unsigned types[2],growthRate; unsigned natDexNum,baseHP')
    source = source.replace('struct Trainer { unsigned partySize', 'struct Trainer { u64 aiFlags; unsigned partySize')
    source = source.replace('static struct Trainer trainers[64];', '''#include "constants/difficulty.h"
static struct Trainer gTrainers[DIFFICULTY_COUNT][64];
#define trainers gTrainers[DIFFICULTY_NORMAL]
static enum DifficultyLevel GetTrainerDifficultyLevel(u16 id);
''')
    source = source.replace('return &trainers[id];', 'return &gTrainers[GetTrainerDifficultyLevel(id)][id];')
    source += '''
#include "custom_run_menu_model.h"
#include "custom_difficulty.h"
#include "custom_random.h"
enum CRStatus CustomRun_ReadRules(struct CRConfig *out);
enum CRStatus CustomRun_Read(struct CRConfig *out);
enum Species { SPECIES_TEST };
#include "constants/battle_ai.h"
#define BATTLE_TYPE_TRAINER 64
#define BATTLE_TYPE_EREADER_TRAINER 128
#define BATTLE_TYPE_FIRST_BATTLE 256
#define BATTLE_TYPE_CATCH_TUTORIAL 512
#define BATTLE_TYPE_POKEDUDE 1024
#define BATTLE_TYPE_SAFARI 2048
#define BATTLE_TYPE_ROAMER 4096
#define BATTLE_TYPE_FACTORY 8192
#define MON_DATA_EXP 20
#define DAMAGE_CATEGORY_STATUS 0
#define FLAG_BADGE01_GET 100
#define FLAG_IS_CHAMPION 200
#define B_VAR_DIFFICULTY 0
static bool flags[256];
static unsigned FlagGet(unsigned id) { return flags[id]; }
static const unsigned gExperienceTables[1][101] = {
'''
    source += '{' + ','.join(str(i**3) for i in range(101)) + '}};\n'
    # Native GetMonData fixture can expose synthetic EXP without changing production adapters.
    source = source.replace('return n==0 ? p->species', 'if(n==20) return p->level*p->level*p->level; return n==0 ? p->species')
    # Item battle usages copied from the actual native enum, not duplicated numbering.
    items = (tree / 'include/constants/items.h').read_text()
    source += items[items.index('enum EffectItem\n'):items.index('#endif  // GUARD_CONSTANTS_ITEMS_H')]
    source += '''
static unsigned GetMoveType(unsigned move) { return move==MOVE_EMBER ? 1 : 0; }
static unsigned GetMoveAccuracy(unsigned move) { (void)move; return 100; }
static unsigned GetMoveCategory(unsigned move) { return move==MOVE_STATUS ? DAMAGE_CATEGORY_STATUS : 1; }
'''
    actual = (tree / 'src/custom_difficulty.c').read_text()
    source += actual[actual.index('static bool sPreparedTrainer;'):actual.rindex('#endif')]
    run = (tree / 'src/custom_run.c').read_text()
    for signature in ('static uint32_t TrainerId(void)', 'enum CRStatus CustomRun_ReadRules(', 'enum CRStatus CustomRun_Read(', 'bool CustomRun_CanPlay('):
        source += function(run, signature)
    source += function((tree / 'src/difficulty.c').read_text(), 'enum DifficultyLevel GetCurrentDifficultyLevel(void)')
    source += function((tree / 'src/difficulty.c').read_text(), 'enum DifficultyLevel GetTrainerDifficultyLevel(u16 trainerId)')
    random = (tree / 'src/custom_random.c').read_text()
    source += random[random.index('static struct CRPoolEntry'):random.rindex('#endif')]
    source += '''
#define MAX_LEVEL 100
#define B_LEVEL_CAP_TYPE 0
#define LEVEL_CAP_FLAG_LIST 1
#define LEVEL_CAP_VARIABLE 2
#define B_LEVEL_CAP_VARIABLE 0
#define B_EXP_CAP_TYPE 0
#define EXP_CAP_NONE 0
#define EXP_CAP_HARD 1
#define EXP_CAP_SOFT 2
#define B_LEVEL_CAP_EXP_UP 0
'''
    for i in range(2,9):
        source += f'#define FLAG_BADGE0{i}_GET {99+i}\n'
    caps = (tree / 'src/caps.c').read_text()
    source += function(caps,'u32 GetCurrentLevelCap(void)')
    source += function(caps,'u32 GetSoftLevelCapExpValue(')
    # Native generic level increment, invoked by battle and daycare.
    source += '''
typedef int bool8;
static void SetMonData(struct Pokemon *mon,unsigned key,const void *value) {
    if(key==MON_DATA_LEVEL) mon->level=*(const u8 *)value;
    if(key==MON_DATA_EXP) mon->experience=*(const u32 *)value;
}
'''
    source += function((tree / 'src/pokemon.c').read_text(),'bool8 TryIncrementMonLevel(')
    # GetAiFlags is the production dispatcher; unsupported facilities retain their native policy.
    source += '''
enum BattlerId { B_BATTLER_0,B_BATTLER_1,B_BATTLER_2,B_BATTLER_3 };
static bool IsSmartBattle(void) { return true; }
static u64 GetWildAiFlags(void) { return AI_FLAG_CHECK_BAD_MOVE; }
static u64 GetAiScriptsInRecordedBattle(unsigned battler) { (void)battler; return 3; }
static u64 GetAiScriptsInBattleFactory(void) { return 5; }
static u64 GetTrainerAIFlagsFromId(unsigned id) { return GetTrainerStructFromId(id)->aiFlags; }
static bool IsDoubleBattle(void) { return (gBattleTypeFlags&BATTLE_TYPE_TWO_OPPONENTS)!=0; }
static void *sDynamicAiFunc;
'''
    source += function((tree / 'src/battle_ai_main.c').read_text(),'static u64 GetAiFlags(')
    battle = (tree / 'src/battle_setup.c').read_text()
    source += function(battle,'void CreateNPCTrainerPartyFromTrainer(struct Pokemon *party,')
    source += function(battle,'static void CreateNPCTrainerParty(struct Pokemon *party, u16 trainerNum)\n{')
    # Test the actual post-multiplier reward statement, not a parallel clamp in a mock dispatcher.
    battle_script = (tree / 'src/battle_script_commands.c').read_text()
    assert 'gBattleStruct->battlerExpReward=CustomDifficulty_ClampExp(' in battle_script
    assert 'CustomDifficulty_ItemBlocked(battleUsage)' in (tree/'src/item_use.c').read_text()
    assert 'CustomDifficulty_ForceSet()' in (tree/'src/battle_main.c').read_text()
    source = source.replace('struct Pokemon { unsigned species,level;', 'struct Pokemon { unsigned species,level,experience;')
    source = source.replace('return p->level*p->level*p->level;', 'return p->experience ? p->experience : p->level*p->level*p->level;')
    source = source.replace('if(n==20)', 'if(n==21) return 50; if(n==22) return 100; if(n==23) return 0; if(n==20)')
    source = source.replace('static struct { u8 playerTrainerId[4]; } save2;', 'static struct { u8 playerTrainerId[4]; unsigned optionsBattleStyle; } save2;')
    source += r'''
#define OPTIONS_BATTLE_STYLE_SET 1
#define PLATFORM_3DS 1
#define TESTING 0
static struct { unsigned windowsType,specialTrainerBattleType,battleStyle,expOnCatch; } gBattleScripting;
static unsigned CtrExtras_Get(const char *name) { return 0; }
'''
    source += function((tree/'src/battle_main.c').read_text(),'static void ClearSetBScriptingStruct(void)')
    source += candy_fixture(tree)
    source += item_fixture(tree)
    source += (HERE / 'custom_difficulty_test.c').read_text()
    return source


def candy_fixture(tree):
    pokemon=(tree/'src/pokemon.c').read_text()
    start=pokemon.index('            // Rare Candy / EXP Candy')
    end=pokemon.index('            // Cure status',start)
    fragment=pokemon[start:end]
    source=r'''
#define EXP_100 1
#define EXP_800 2
#define EXP_3000 3
#define EXP_10000 4
#define EXP_30000 5
#define ITEM3_LEVEL_UP 1
static unsigned candyParam;
static unsigned GetItemHoldEffectParam(unsigned item) { return candyParam; }
static void CalculateMonStats(struct Pokemon *mon) {
    unsigned exp=GetMonData(mon,MON_DATA_EXP);
    while(mon->level<100 && gExperienceTables[0][mon->level+1]<=exp) ++mon->level;
}
'''
    import re
    table=re.search(r'const u32 sExpCandyExperienceTable\[.*?\] =\s*\{.*?\};',pokemon,re.S).group(0)
    source+=table+'\n'
    source+=r'''
static bool Candy(struct Pokemon *mon,unsigned param) {
    unsigned itemEffect[8]={0,0,0,ITEM3_LEVEL_UP},i=3,item=0,dataUnsigned;
    unsigned levelBefore=mon->level;
    bool retVal=true,didLevelUp=false;
    candyParam=param;
    switch(0) { case 0:
'''+fragment+r'''
    }
    (void)didLevelUp;
    return !retVal;
}
struct BoxPokemon { unsigned level,experience; };
struct DaycareMon { struct BoxPokemon mon; u32 steps; };
static u32 GetBoxMonData(struct BoxPokemon *mon,unsigned key) { (void)key;return mon->experience; }
static void SetBoxMonData(struct BoxPokemon *mon,unsigned key,const u32 *value) { (void)key;mon->experience=*value; }
static u8 GetLevelFromBoxMonExp(struct BoxPokemon *mon) {
    unsigned level=1;
    while(level<100 && gExperienceTables[0][level+1]<=mon->experience) ++level;
    return level;
}
'''
    daycare=(tree/'src/daycare.c').read_text()
    source+=function(daycare,'static u8 GetLevelAfterDaycareSteps(')
    source+=function(daycare,'static u8 GetNumLevelsGainedFromSteps(')
    source+=r'''
static struct CRConfig SaveRules(unsigned preset,bool randomized);
static void CandiesAndDaycare(void)
{
    struct Pokemon mon={.species=1,.level=14};
    SaveRules(CR_HARD,false);memset(flags,0,sizeof(flags));
    assert(Candy(&mon,0) && mon.level==15 && mon.experience==3375);
    assert(!Candy(&mon,0) && mon.level==15 && mon.experience==3375);
    mon=(struct Pokemon){.species=1,.level=14};
    assert(Candy(&mon,5) && mon.level==15 && mon.experience==3375);
    mon=(struct Pokemon){.species=1,.level=20};assert(!Candy(&mon,5) && mon.level==20 && !mon.experience);
    struct DaycareMon dc={.mon={.level=14,.experience=2744},.steps=100000};
    assert(GetNumLevelsGainedFromSteps(&dc)==1);
    dc.mon.level=20;dc.mon.experience=8000;assert(!GetNumLevelsGainedFromSteps(&dc));
    SaveRules(CR_NORMAL,false);mon=(struct Pokemon){.species=1,.level=14};assert(Candy(&mon,5) && mon.level>15);
    assert(GetNumLevelsGainedFromSteps(&dc)>0);
    puts("production Rare/EXP candy fragment + daycare level/cost: hard cap, no item effect at cap, over-cap gift preserved, no unsigned underflow, Normal unaffected PASS");
}
'''
    return source


def item_fixture(tree):
    source = r'''
/* Native item validator + actual party-use callback, with synthetic UI/bag. */
enum Item { ITEM_TEST,ITEM_BLUE_FLUTE,ITEM_RED_FLUTE,ITEM_YELLOW_FLUTE };
enum Ability { ABILITY_TEST };
#define MON_DATA_HP 21
#define MON_DATA_MAX_HP 22
#define MON_DATA_STATUS 23
#define MON_DATA_PP_BONUSES 24
#define MON_DATA_PP1 10
#define B_POSITION_PLAYER_LEFT 0
#define B_POSITION_PLAYER_RIGHT 2
#define MAX_POSITION_COUNT 4
#define BATTLE_TYPE_DOUBLE 16384
#define BATTLE_TYPE_MULTI 32768
#define ITEM_USE_BAG_MENU 0
#define STAT_ATK 1
#define NUM_STATS 6
#define MAX_STAT_STAGE 12
#define CMP_EQUAL 0
#define ITEM4_HEAL_PP 1
#define SIDE_STATUS_MIST 1
#define BALL_THROW_UNABLE_TWO_MONS 1
#define BALL_THROW_UNABLE_NO_ROOM 2
#define BALL_THROW_UNABLE_SEMI_INVULNERABLE 3
#define BALL_THROW_UNABLE_DISABLED_FLAG 4
#define SE_SELECT 1
static struct { unsigned slotId,data1; } gPartyMenu;
static struct { struct { unsigned embargoTimer,dragonCheer,focusEnergy; } volatiles; } gBattleMons[4];
static unsigned gSideStatuses[2],gBattlerInMenuId,gSpecialVar_ItemId;
static unsigned usage=EFFECT_ITEM_RESTORE_HP,removed,messages;
static u8 gStringVar4[128];
static const u8 sText_RunItemRestricted[]="This run restricts that item in TRAINER battles.";
static const u8 sText_CantThrowPokeBall_TwoMons[]="two mons",gText_BoxFull[]="full",sText_CantThrowPokeBall_SemiInvulnerable[]="hidden",sText_CantThrowPokeBall_Disabled[]="disabled",gText_WontHaveEffect[]="no effect";
static enum EffectItem GetItemBattleUsage(enum Item item) { (void)item; return usage; }
static unsigned GetItemType(enum Item item) { (void)item; return ITEM_USE_BAG_MENU; }
static unsigned GetBattlerAbility(unsigned target) { (void)target; return ABILITY_TEST; }
static const u8 *GetItemEffect(unsigned item) { (void)item; static const u8 effect[8]={0}; return effect; }
static bool CompareStat(unsigned target,unsigned stat,unsigned stage,unsigned op,unsigned ability) { return false; }
static unsigned GetBattlerSide(unsigned battler) { return 0; }
static unsigned GetBallThrowableState(void) { return 0; }
static unsigned GetItemStatus1Mask(enum Item item) { return 0; }
static bool SelectedMonHasVolatile(enum Item item) { return false; }
static unsigned CalculatePPWithBonus(unsigned move,unsigned bonus,unsigned slot) { return 10; }
static void StringExpandPlaceholders(u8 *out,const u8 *text) { strcpy((char *)out,(const char *)text); }
typedef void (*TaskFunc)(u8);
static struct { TaskFunc func; } gTasks[1];
static bool gPartyMenuUseExitCallback;
static struct { unsigned itemPartyIndex[4]; } battleStruct;
#define gBattleStruct (&battleStruct)
static struct Pokemon itemMon={.species=1,.level=10};
static struct Pokemon *GetPartyMonFromPartyMenuId(unsigned id) { return &itemMon; }
static unsigned GetPartyIdFromBattleSlot(unsigned id) { return id; }
static void PlaySE(unsigned id) {}
static void DisplayPartyMenuMessage(const u8 *text,bool normal) { ++messages; }
static void ScheduleBgCopyTilemapToVram(unsigned bg) {}
static void RemoveBagItem(unsigned item,unsigned count) { removed+=count; }
'''
    source += function((tree/'src/item_use.c').read_text(),'bool32 CannotUseItemsInBattle(')
    party=(tree/'src/party_menu.c').read_text()
    source += function(party,'static bool32 IsItemFlute(')
    source += function(party,'void ItemUseCB_BattleScript(')
    source += r'''
static void ItemDone(u8 id) {}
static void ActualItemCallback(void)
{
    SaveRules(CR_HARD,false);
    gBattleTypeFlags=BATTLE_TYPE_TRAINER;
    removed=messages=0;usage=EFFECT_ITEM_RESTORE_HP;
    ItemUseCB_BattleScript(0,ItemDone);
    assert(!removed && messages==1 && !gPartyMenuUseExitCallback && strstr((const char *)gStringVar4,"restricts"));
    usage=EFFECT_ITEM_INCREASE_STAT; ItemUseCB_BattleScript(0,ItemDone);assert(!removed);
    usage=EFFECT_ITEM_THROW_BALL;assert(!CannotUseItemsInBattle(ITEM_TEST,NULL));
    gBattleTypeFlags=BATTLE_TYPE_CATCH_TUTORIAL;usage=EFFECT_ITEM_RESTORE_HP;
    ItemUseCB_BattleScript(0,ItemDone);assert(removed==1 && gPartyMenuUseExitCallback);
    gBattleTypeFlags=BATTLE_TYPE_TRAINER;SaveRules(CR_NORMAL,false);
    ItemUseCB_BattleScript(0,ItemDone);assert(removed==2 && gPartyMenuUseExitCallback);
    puts("native item validator + actual party callback: restrictions before removal, no blocked turn/use, balls/tutorials/Normal retained PASS");
}
'''
    # SaveRules is defined with the remaining test cases below.
    return 'typedef int bool32;\nstatic struct CRConfig SaveRules(unsigned preset,bool randomized);\n' + source


def trainer_source_audit(tree):
    # Audit native source inputs, not generated trainers.h, so a bootstrap cannot drop variants.
    text = (tree/'src/data/trainers.party').read_text()
    entries = re.findall(r'^=== (TRAINER_\w+) ===\n(.*?)(?=^=== |\Z)',text,re.M|re.S)
    normal = {name: body for name,body in entries if 'Difficulty: Hard' not in body}
    hard = {name: body for name,body in entries if 'Difficulty: Hard' in body}
    assert len(hard)==49
    for name,body in hard.items():
        assert re.findall(r'^Level: (\d+)$',body,re.M)==re.findall(r'^Level: (\d+)$',normal[name],re.M),name
        assert re.search(r'^Double Battle: (\w+)$',body,re.M).group(1)==re.search(r'^Double Battle: (\w+)$',normal[name],re.M).group(1)
        assert re.search(r'^AI: (.*)$',body,re.M).group(1)==re.search(r'^AI: (.*)$',normal[name],re.M).group(1)
        assert 'Omniscient' not in body and 'Predict' not in body
    assert 'Aron @ Oran Berry' in hard['TRAINER_ROXANNE_1']
    print('Source audit: 49 prepared native variants, retained IDs/levels/party sizes/battle types; no omniscient policy PASS')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--tree',type=Path,required=True)
    p.add_argument('--cc',default='cc')
    args=p.parse_args()
    tree=args.tree.resolve()
    trainer_source_audit(tree)
    compile_run(args.cc,tree,native(tree),[str(tree/"src/custom_run_menu_model.c")])
    print('Production difficulty hooks PASS (ASan + UBSan; controlled host state)')


if __name__=='__main__':
    main()
