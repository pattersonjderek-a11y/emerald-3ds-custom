#ifndef CTR_ENGINE_COMPAT_H
#define CTR_ENGINE_COMPAT_H
/* UI-only reads across the two pinned engines; gameplay uses native accessors. */
#ifdef PORT_EXPANSION
#define CTR_UI_SPECIES_LIMIT (SPECIES_EGG+1)
/* Native palettes can contain fewer than 16 used colours (Sandile has 13).
 * Never request 32 bytes through a short asset and receive its unresolved stub. */
static inline bool8 CtrUI_ReadPalette(const void *base,u16 out[16])
{
    u32 size=Port_GetAssetSizeExact(base);
    memset(out,0,32);
    if(!size || (size&1))return FALSE;
    if(size>32)size=32;
    return Port_LoadAssetRangeToBuffer(base,0,out,size);
}
#define CtrFrontPic(s) (gSpeciesInfo[(s)].frontPic)
#define CtrNormalPal(s) (gSpeciesInfo[(s)].palette)
#define CtrShinyPal(s) (gSpeciesInfo[(s)].shinyPalette)
#define CtrWildInfo(h,member,time) ((h)->encounterTypes[(time)].member)
#define CtrContestDescription(m) (gContestEffects[GetMoveContestEffect(m)].description)
#else
#define CTR_UI_SPECIES_LIMIT (NUM_SPECIES+28)
#define GetSpeciesName(s) (gSpeciesNames[(s)])
#define GetMoveDescription(m) (gMoveDescriptionPointers[(m)-1])
#define GetMoveName(m) (gMoveNames[(m)])
#define GetMovePower(m) (gBattleMoves[(m)].power)
#define GetMoveAccuracy(m) (gBattleMoves[(m)].accuracy)
#define GetMovePP(m) (gBattleMoves[(m)].pp)
#define GetMoveType(m) (gBattleMoves[(m)].type)
#define GetMoveTarget(m) (gBattleMoves[(m)].target)
#define GetMoveContestCategory(m) (gContestMoves[(m)].contestCategory)
#define GetMoveContestEffect(m) (gContestMoves[(m)].effect)
#define GetItemIconPic(i) GetItemIconPicOrPalette((i),0)
#define GetItemIconPalette(i) GetItemIconPicOrPalette((i),1)
#define CtrFrontPic(s) (gMonFrontPicTable[(s)].data)
#define CtrNormalPal(s) (gMonPaletteTable[(s)].data)
#define CtrShinyPal(s) (gMonShinyPaletteTable[(s)].data)
#define CtrWildInfo(h,member,time) ((h)->member)
#define CtrContestDescription(m) (gContestEffectDescriptionPointers[GetMoveContestEffect(m)])
#define NUM_LAND_MONS_ENCOUNTER_SLOTS LAND_WILD_COUNT
#define NUM_WATER_MONS_ENCOUNTER_SLOTS WATER_WILD_COUNT
#define NUM_ROCK_SMASH_MONS_ENCOUNTER_SLOTS ROCK_WILD_COUNT
#define NUM_FISHING_MONS_ENCOUNTER_SLOTS FISH_WILD_COUNT
#endif
#endif
