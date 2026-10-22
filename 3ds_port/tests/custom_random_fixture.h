/* Synthetic engine tables for executing the production native adapters. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "custom_random_core.h"
typedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32; typedef int32_t s32;
#define PORT_BRIDGE 1
#define TRUE 1
#define FALSE 0
#define ARRAY_COUNT(a) (sizeof(a)/sizeof((a)[0]))
#define NUM_SPECIES 80
#define MAX_MON_MOVES 4
#define NUM_ABILITY_SLOTS 3
#define MOVE_NONE 0
#define MOVE_TACKLE 1
#define MOVE_EMBER 2
#define MOVE_STATUS 3
#define MOVE_SNORE 4
#define MOVE_DREAM_EATER 5
#define MOVE_LAST_RESORT 6
#define MOVE_EXPLOSION 7
#define MOVE_SELF_DESTRUCT 8
#define MOVE_ILLEGAL 9
#define LEVEL_UP_MOVE_END 65535
#define FORM_CHANGE_TERMINATOR 0
#define FORM_CHANGE_BATTLE_MEGA_EVOLUTION_ITEM 1
#define FORM_CHANGE_BATTLE_PRIMAL_REVERSION 2
#define FORM_CHANGE_ITEM_HOLD 3
#define EVOLUTIONS_END 65535
#define EVO_LEVEL 1
#define ITEM_NONE 0
#define TRAINER_MON_RANDOM_GENDER 0
#define TRAINER_CLASS_RIVAL 3
#define TRAINERS_COUNT 64
#define BATTLE_TYPE_LINK 1
#define BATTLE_TYPE_RECORDED 2
#define BATTLE_TYPE_FRONTIER 4
#define BATTLE_TYPE_TRAINER_HILL 8
#define BATTLE_TYPE_SECRET_BASE 16
#define BATTLE_TYPE_TWO_OPPONENTS 32
#define B_MULTI_HALF_TEAMS 1
#define MULTI_TEAM_SIZE_HALF 1
#define PARTY_SIZE 6
#define VAR_STARTER_MON 1
#define MAP_UNDEFINED 65535
#define MAP_ALTERING_CAVE 0x0202
#define MAP_NUM(x) ((x)&255)
#define VAR_ALTERING_CAVE_WILD_SET 2
#define NUM_ALTERING_CAVE_TABLES 1
#define HEADER_NONE 65535
#define MAP_GROUP(x) ((x)>>8)
#define TIMES_OF_DAY_COUNT 2
#define NUM_LAND_MONS_ENCOUNTER_SLOTS 12
#define NUM_WATER_MONS_ENCOUNTER_SLOTS 5
#define NUM_ROCK_SMASH_MONS_ENCOUNTER_SLOTS 5
#define NUM_FISHING_MONS_ENCOUNTER_SLOTS 10
#define NUM_HIDDEN_MONS_ENCOUNTER_SLOTS 3
#define SPECIES_POOCHYENA 1
#define SPECIES_TREECKO 7
#define SPECIES_TORCHIC 8
#define SPECIES_MUDKIP 9
#define SPECIES_GROVYLE 28
#define SPECIES_SCEPTILE 29
#define SPECIES_COMBUSKEN 30
#define SPECIES_BLAZIKEN 31
#define SPECIES_MARSHTOMP 32
#define SPECIES_SWAMPERT 33
#define SPECIES_DARMANITAN_GALAR_ZEN 34
#define SPECIES_SPRIGATITO 25
#define SPECIES_FUECOCO 26
#define SPECIES_QUAXLY 27
#define SPECIES_PECHARUNT 35
#define MON_DATA_SPECIES 0
#define MON_DATA_LEVEL 1
#define MON_DATA_MOVE1 2
#define OTID_STRUCT_PRESET(n) ((struct OriginalTrainerId){1,n})
#define GET_BASE_SPECIES_ID(n) bases[n]
enum { HOLD_EFFECT_SOUL_DEW=10,HOLD_EFFECT_LIGHT_BALL,HOLD_EFFECT_THICK_CLUB,HOLD_EFFECT_LEEK,HOLD_EFFECT_ADAMANT_ORB,HOLD_EFFECT_LUSTROUS_ORB,HOLD_EFFECT_GRISEOUS_ORB,HOLD_EFFECT_PLATE,HOLD_EFFECT_DRIVE,HOLD_EFFECT_MEGA_STONE,HOLD_EFFECT_PRIMAL_ORB,HOLD_EFFECT_MEMORY,HOLD_EFFECT_Z_CRYSTAL,HOLD_EFFECT_OGERPON_MASK };
struct LevelUpMove { u16 move,level; };
struct Evolution { u16 method,param,targetSpecies; };
struct FormChange { unsigned method,targetSpecies,param1; };
struct SpeciesInfo {
    unsigned natDexNum,baseHP,baseAttack,baseDefense,baseSpeed,baseSpAttack,baseSpDefense;
    const void *frontPic,*backPic,*iconSprite,*palette,*shinyPalette;
    u16 abilities[3]; const struct LevelUpMove *levelUpLearnset;
    const struct Evolution *evolutions; const struct FormChange *formChangeTable;
    bool isPaldeanForm,isGalarianForm,isHisuianForm,isAlolanForm;
    bool isMegaEvolution,isPrimalReversion,isUltraBurst,isGigantamax,isTeraForm,isTotem;
    bool isRestrictedLegendary,isSubLegendary,isMythical,isUltraBeast;
};
static struct SpeciesInfo gSpeciesInfo[NUM_SPECIES];
static u16 bases[NUM_SPECIES];
struct WildPokemon { u8 minLevel,maxLevel; u16 species; };
struct WildPokemonInfo { u8 encounterRate; const struct WildPokemon *wildPokemon; };
struct WildEncounterTypes { const struct WildPokemonInfo *landMonsInfo,*waterMonsInfo,*rockSmashMonsInfo,*fishingMonsInfo,*hiddenMonsInfo; };
struct WildPokemonHeader { u8 mapGroup,mapNum; struct WildEncounterTypes encounterTypes[TIMES_OF_DAY_COUNT]; };
static struct WildPokemonHeader gWildMonHeaders[3];
static struct { u8 customRunConfig[52]; struct { u8 mapGroup,mapNum; } location; } save1;
static struct { u8 playerTrainerId[4]; } save2;
#define gSaveBlock1Ptr (&save1)
#define gSaveBlock2Ptr (&save2)
struct TrainerMon {
    const u8 *nickname,*ev; u32 iv; u16 moves[4],species,heldItem,ability;
    unsigned lvl,ball,friendship,nature,gender,isShiny,teraType,gigantamaxFactor,shouldUseDynamax,dynamaxLevel;
};
struct OriginalTrainerId { unsigned method,id; };
struct TrainerGenerator { unsigned localRngState; struct OriginalTrainerId otID; };
struct Pokemon { unsigned species,level; u16 moves[4]; struct TrainerMon source; unsigned personality; };
struct Trainer { unsigned partySize,multiTeamSize,poolSize,overrideTrainer,trainerClass; const struct TrainerMon *party; };
static struct Trainer trainers[64];
static unsigned gBattleTypeFlags,selectedStarter,globalRng;
static unsigned Port_GetAssetSize(const void *p) { return p && p!=(void *)1 ? 1024 : 0; }
static unsigned GetMovePower(unsigned move) { return move && move!=MOVE_STATUS ? 40 : 0; }
static unsigned GetMonData(const struct Pokemon *p,unsigned n) { return n==0 ? p->species : n==1 ? p->level : p->moves[n-2]; }
static void SetMonMoveSlot(struct Pokemon *p,unsigned move,unsigned slot) { p->moves[slot]=move; }
static unsigned GetItemHoldEffect(unsigned item) { return item==123 ? HOLD_EFFECT_MEGA_STONE : item; }
static unsigned LocalRandomSeed(unsigned key) { return key; }
static unsigned VarGet(unsigned var) { assert(var==VAR_STARTER_MON); return selectedStarter; }
static const struct Trainer *GetTrainerStructFromId(unsigned id) { assert(id<64); return &trainers[id]; }
static void ZeroPartyMons(struct Pokemon *p) { memset(p,0,sizeof(*p)*6); }
#define AllocZeroed(n) calloc(1,n)
#define Free(p) free(p)
static void MakeTrainerGenerator(struct TrainerGenerator *g,const struct Trainer *t) { (void)t; g->localRngState=globalRng; }
static void DoTrainerPartyPool(const struct Trainer *t,u32 *indices,unsigned n,unsigned flags) { (void)t; (void)flags; for(unsigned i=0;i<n;++i) indices[i]=i; }
static void GenerateMonFromTrainerMon(struct Pokemon *p,const struct TrainerMon *m,struct TrainerGenerator *g) {
    p->species=m->species; p->level=m->lvl; p->source=*m; p->personality=g->localRngState++;
    memcpy(p->moves,m->moves,sizeof(p->moves));
}

#define STARTER_MON_COUNT 3
#define B_TRAINER_PLAYER 0
#define B_TRANSITION_BLUR 0
static const u16 sStarterMon[3]={7,8,9};
static struct Pokemon gParties[1][6];
static unsigned gSpecialVar_Result,starterCallbacks;
static unsigned *GetVarPointer(unsigned v) { assert(v==VAR_STARTER_MON); return &selectedStarter; }
static void ScriptGiveMon(unsigned species,unsigned level,unsigned item) { (void)item; gParties[0][0]=(struct Pokemon){.species=species,.level=level}; }
static void ResetTasks(void) { ++starterCallbacks; }
static void PlayBattleBGM(void) { ++starterCallbacks; }
static void CB2_StartFirstBattle(void) {}
static void SetMainCallback2(void (*cb)(void)) { assert(cb==CB2_StartFirstBattle); ++starterCallbacks; }
static void BattleTransition_Start(unsigned kind) { assert(kind==B_TRANSITION_BLUR); ++starterCallbacks; }
#define B_POOL_SETTING_USE_FIXED_SEED 0
#define B_POOL_SETTING_FIXED_SEED 0
#define READ_OTID_FROM_SAVE 123

static void CustomDifficulty_BeginTrainer(u16 id) { (void)id; }
static void CustomDifficulty_EndTrainer(void) {}
static void CustomDifficulty_FinishMon(struct Pokemon *mon) { (void)mon; }
