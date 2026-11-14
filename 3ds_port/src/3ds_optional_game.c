/* Optional abilities/items extending the authoritative v0.5.0 settings model.
 * Native form/ability slots and item acquisition machinery remain in use. */
#include "global.h"
#include "main.h"
#include "pokemon.h"
#include "battle.h"
#include "item.h"
#include "item_icon.h"
#include "3ds_platform.h"
#include "3ds_randomizer.h"
#include "3ds_optional.h"
#include "constants/hold_effects.h"
#include <string.h>
#ifdef PORT_EXPANSION
static const u16 sAbilities[]={
 ABILITY_STENCH,ABILITY_DRIZZLE,ABILITY_SPEED_BOOST,ABILITY_BATTLE_ARMOR,
 ABILITY_STURDY,ABILITY_DAMP,ABILITY_LIMBER,ABILITY_SAND_VEIL,ABILITY_STATIC,
 ABILITY_VOLT_ABSORB,ABILITY_WATER_ABSORB,ABILITY_OBLIVIOUS,ABILITY_CLOUD_NINE,
 ABILITY_COMPOUND_EYES,ABILITY_INSOMNIA,ABILITY_COLOR_CHANGE,ABILITY_IMMUNITY,
 ABILITY_FLASH_FIRE,ABILITY_SHIELD_DUST,ABILITY_OWN_TEMPO,ABILITY_SUCTION_CUPS,
 ABILITY_INTIMIDATE,ABILITY_ROUGH_SKIN,ABILITY_EFFECT_SPORE,ABILITY_LEVITATE,
 ABILITY_CLEAR_BODY,ABILITY_NATURAL_CURE,ABILITY_LIGHTNING_ROD,ABILITY_SERENE_GRACE,
 ABILITY_SWIFT_SWIM,ABILITY_CHLOROPHYLL,ABILITY_ILLUMINATE,ABILITY_TRACE,
 ABILITY_POISON_POINT,ABILITY_INNER_FOCUS,ABILITY_MAGMA_ARMOR,ABILITY_WATER_VEIL,
 ABILITY_MAGNET_PULL,ABILITY_RAIN_DISH,ABILITY_SAND_STREAM,ABILITY_PRESSURE,
 ABILITY_THICK_FAT,ABILITY_EARLY_BIRD,ABILITY_FLAME_BODY,ABILITY_RUN_AWAY,
 ABILITY_KEEN_EYE,ABILITY_HYPER_CUTTER,ABILITY_PICKUP,ABILITY_MARVEL_SCALE,
 ABILITY_VITAL_SPIRIT,ABILITY_WHITE_SMOKE,ABILITY_PURE_POWER,ABILITY_SHELL_ARMOR,
 ABILITY_AIR_LOCK,ABILITY_SCRAPPY,ABILITY_TECHNICIAN,ABILITY_IRON_FIST,
 ABILITY_SOLID_ROCK,ABILITY_FILTER,ABILITY_REGENERATOR,ABILITY_MULTISCALE
};
static const u16 sField[]={ITEM_POKE_BALL,ITEM_GREAT_BALL,ITEM_ULTRA_BALL,ITEM_NET_BALL,
 ITEM_DIVE_BALL,ITEM_NEST_BALL,ITEM_REPEAT_BALL,ITEM_TIMER_BALL,ITEM_LUXURY_BALL,
 ITEM_PREMIER_BALL,ITEM_POTION,ITEM_SUPER_POTION,ITEM_HYPER_POTION,ITEM_MAX_POTION,
 ITEM_FULL_RESTORE,ITEM_ANTIDOTE,ITEM_PARALYZE_HEAL,ITEM_AWAKENING,ITEM_BURN_HEAL,
 ITEM_ICE_HEAL,ITEM_FULL_HEAL,ITEM_REVIVE,ITEM_MAX_REVIVE,ITEM_ETHER,ITEM_MAX_ETHER,
 ITEM_ELIXIR,ITEM_MAX_ELIXIR,ITEM_REPEL,ITEM_SUPER_REPEL,ITEM_MAX_REPEL,
 ITEM_RARE_CANDY,ITEM_NUGGET,ITEM_PEARL,ITEM_BIG_PEARL,ITEM_STARDUST,ITEM_STAR_PIECE,
 ITEM_ORAN_BERRY,ITEM_SITRUS_BERRY,ITEM_LUM_BERRY,ITEM_LEPPA_BERRY};
static const u16 sHeld[]={ITEM_ORAN_BERRY,ITEM_SITRUS_BERRY,ITEM_LUM_BERRY,
 ITEM_CHESTO_BERRY,ITEM_PECHA_BERRY,ITEM_RAWST_BERRY,ITEM_ASPEAR_BERRY,
 ITEM_CHERI_BERRY,ITEM_PERSIM_BERRY,ITEM_LEPPA_BERRY,ITEM_LEFTOVERS,
 ITEM_SHELL_BELL,ITEM_QUICK_CLAW,ITEM_FOCUS_BAND,ITEM_KINGS_ROCK,
 ITEM_BRIGHT_POWDER,ITEM_WHITE_HERB,ITEM_MENTAL_HERB,ITEM_CHOICE_BAND,
 ITEM_SCOPE_LENS,ITEM_SHARP_BEAK,ITEM_POISON_BARB,ITEM_SOFT_SAND,
 ITEM_HARD_STONE,ITEM_SILVER_POWDER,ITEM_SPELL_TAG,ITEM_CHARCOAL,
 ITEM_MYSTIC_WATER,ITEM_MIRACLE_SEED,ITEM_MAGNET,ITEM_TWISTED_SPOON,
 ITEM_NEVER_MELT_ICE,ITEM_DRAGON_FANG,ITEM_BLACK_GLASSES,ITEM_BLACK_BELT,
 ITEM_METAL_COAT,ITEM_SILK_SCARF};
static bool sBattleSnapshot,sBattleAbilities;
static u32 sBattleSeed;
void CtrOptional_BeginBattle(void)
{
 sBattleSeed=CtrRandomizer_Seed();
 sBattleAbilities=CtrSettings_GetInt("rand_abilities",0)==1;
 sBattleSnapshot=true;
}
static bool AbilityEnabled(void)
{ return gMain.inBattle&&sBattleSnapshot ? sBattleAbilities : CtrSettings_GetInt("rand_abilities",0)==1; }
static u32 AbilitySeed(void)
{ return gMain.inBattle&&sBattleSnapshot ? sBattleSeed : CtrRandomizer_Seed(); }
static bool sBuilt,sFormItems[ITEMS_COUNT];
static u16 sAbilityCache[NUM_SPECIES][NUM_ABILITY_SLOTS];
static u32 sAbilitySeed;
static bool sAbilityCached;
static u16 sAbilityPool[ARRAY_COUNT(sAbilities)],sFieldPool[ARRAY_COUNT(sField)],sHeldPool[ARRAY_COUNT(sHeld)];
static size_t sAbilityCount,sFieldCount,sHeldCount;
static bool ProtectedBattle(void)
{
 return gMain.inBattle && (gBattleTypeFlags&(BATTLE_TYPE_LINK|BATTLE_TYPE_RECORDED|
 BATTLE_TYPE_FRONTIER|BATTLE_TYPE_TRAINER_HILL|BATTLE_TYPE_SECRET_BASE|
 BATTLE_TYPE_FIRST_BATTLE|BATTLE_TYPE_CATCH_TUTORIAL|BATTLE_TYPE_EREADER_TRAINER));
}
static bool SafeAbility(u16 ability)
{
 if(!ability||ability>=ABILITIES_COUNT)return false;
 const struct AbilityInfo *a=&gAbilitiesInfo[ability];
 return !a->cantBeSwapped && !a->cantBeSuppressed && !a->cantBeOverwritten
    && ability!=ABILITY_PURE_POWER && ability!=ABILITY_HUGE_POWER && ability!=ABILITY_WONDER_GUARD
    && ability!=ABILITY_PARENTAL_BOND && ability!=ABILITY_TRUANT && ability!=ABILITY_SLOW_START
    && ability!=ABILITY_DEFEATIST && ability!=ABILITY_SHADOW_TAG && ability!=ABILITY_ARENA_TRAP;
}
static bool SafeItem(u16 item)
{
 if(!item||item>=ITEMS_COUNT||sFormItems[item]||GetItemImportance(item))return false;
 if(GetItemPocket(item)==POCKET_KEY_ITEMS||GetItemPocket(item)==POCKET_TM_HM||item==ITEM_MASTER_BALL)return false;
 switch(GetItemHoldEffect(item)){
 case HOLD_EFFECT_MEGA_STONE:case HOLD_EFFECT_PRIMAL_ORB:case HOLD_EFFECT_PLATE:
 case HOLD_EFFECT_MEMORY:case HOLD_EFFECT_DRIVE:case HOLD_EFFECT_Z_CRYSTAL:
 case HOLD_EFFECT_OGERPON_MASK:case HOLD_EFFECT_SOUL_DEW:case HOLD_EFFECT_LIGHT_BALL:
 case HOLD_EFFECT_THICK_CLUB:case HOLD_EFFECT_LEEK:case HOLD_EFFECT_ADAMANT_ORB:
 case HOLD_EFFECT_LUSTROUS_ORB:case HOLD_EFFECT_GRISEOUS_ORB:case HOLD_EFFECT_BOOSTER_ENERGY:return false;
 default:return true;
 }
}
static void Pools(void)
{
 if(sBuilt)return;
 for(unsigned s=1;s<NUM_SPECIES;++s){
  const struct FormChange *f=gSpeciesInfo[s].formChangeTable;
  for(unsigned i=0;f&&i<128&&f[i].method!=FORM_CHANGE_TERMINATOR;++i)
   if((f[i].method==FORM_CHANGE_ITEM_HOLD||f[i].method==FORM_CHANGE_ITEM_USE||
      f[i].method==FORM_CHANGE_BATTLE_MEGA_EVOLUTION_ITEM||f[i].method==FORM_CHANGE_BATTLE_PRIMAL_REVERSION)
      && f[i].param1<ITEMS_COUNT)sFormItems[f[i].param1]=true;
 }
 for(unsigned i=0;i<ARRAY_COUNT(sAbilities);++i)if(SafeAbility(sAbilities[i]))sAbilityPool[sAbilityCount++]=sAbilities[i];
 for(unsigned i=0;i<ARRAY_COUNT(sField);++i)if(SafeItem(sField[i]))sFieldPool[sFieldCount++]=sField[i];
 for(unsigned i=0;i<ARRAY_COUNT(sHeld);++i)if(SafeItem(sHeld[i]))sHeldPool[sHeldCount++]=sHeld[i];
 sBuilt=true;
}
uint16_t CtrOptional_Ability(uint16_t species,unsigned slot,uint16_t native)
{
 if(!AbilityEnabled()||ProtectedBattle()||!native||slot>=NUM_ABILITY_SLOTS
    ||species>=NUM_SPECIES||!species)return native;
 const struct SpeciesInfo *p=&gSpeciesInfo[species];
 if(p->formChangeTable||GET_BASE_SPECIES_ID(species)!=species)return native;
 for(unsigned i=0;i<NUM_ABILITY_SLOTS;++i)if(p->abilities[i]&&!SafeAbility(p->abilities[i]))return native;
 Pools();
 u32 seed=AbilitySeed();
 if(!sAbilityCached||sAbilitySeed!=seed){memset(sAbilityCache,0,sizeof(sAbilityCache));sAbilitySeed=seed;sAbilityCached=true;}
 if(sAbilityCache[species][slot])return sAbilityCache[species][slot];
 u16 chosen[NUM_ABILITY_SLOTS]={0};
 for(unsigned i=0;i<NUM_ABILITY_SLOTS;++i){
  if(!p->abilities[i])continue;
  bool alias=false;
  for(unsigned j=0;j<i;++j)if(p->abilities[i]==p->abilities[j]){chosen[i]=chosen[j];alias=true;break;}
  if(!alias)chosen[i]=CtrOptional_Pick(sAbilityPool,sAbilityCount,
   CtrOptional_Key(seed,CTR_OPT_ABILITY,species,i),chosen,i);
 }
 memcpy(sAbilityCache[species],chosen,sizeof(chosen));
 return chosen[slot]?chosen[slot]:native;
}
uint16_t CtrOptional_Field(uint16_t item,unsigned kind,unsigned localId)
{
 if(CtrSettings_GetInt("rand_field_items",0)!=1||ProtectedBattle())return item;
 Pools();if(!SafeItem(item))return item;
 u32 map=((u32)gSaveBlock1Ptr->location.mapGroup<<8)|gSaveBlock1Ptr->location.mapNum;
 u16 out=CtrOptional_Pick(sFieldPool,sFieldCount,
  CtrOptional_Key(CtrRandomizer_Seed(),CTR_OPT_FIELD,map,(kind<<16)|localId),NULL,0);
 return out?out:item;
}
uint16_t CtrOptional_Held(uint16_t item,unsigned identity,unsigned slot)
{
 if(CtrSettings_GetInt("rand_held_items",0)!=1||ProtectedBattle())return item;
 Pools();if(!SafeItem(item))return item;
 u16 out=CtrOptional_Pick(sHeldPool,sHeldCount,
  CtrOptional_Key(CtrRandomizer_Seed(),CTR_OPT_HELD,identity,slot),NULL,0);
 return out?out:item;
}
void CtrOptional_WildHeld(void)
{
 if(ProtectedBattle()||(gBattleTypeFlags&BATTLE_TYPE_TRAINER))return;
 for(unsigned i=0;i<PARTY_SIZE;++i){
  struct Pokemon *p=&gEnemyParty[i];u16 species=GetMonData(p,MON_DATA_SPECIES);
  if(!species)continue;
  u16 item=GetMonData(p,MON_DATA_HELD_ITEM);
  u32 map=((u32)gSaveBlock1Ptr->location.mapGroup<<8)|gSaveBlock1Ptr->location.mapNum;
  item=CtrOptional_Held(item,(map<<16)|species,i);
  SetMonData(p,MON_DATA_HELD_ITEM,&item);
 }
}
#else
uint16_t CtrOptional_Ability(uint16_t species,unsigned slot,uint16_t native){(void)species;(void)slot;return native;}
uint16_t CtrOptional_Field(uint16_t item,unsigned kind,unsigned id){(void)kind;(void)id;return item;}
uint16_t CtrOptional_Held(uint16_t item,unsigned id,unsigned slot){(void)id;(void)slot;return item;}
void CtrOptional_WildHeld(void){}
void CtrOptional_BeginBattle(void){}
#endif
