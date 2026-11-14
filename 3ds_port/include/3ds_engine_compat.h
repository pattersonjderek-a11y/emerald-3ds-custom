#ifndef CTR_ENGINE_COMPAT_H
#define CTR_ENGINE_COMPAT_H
/* UI-only reads across the two pinned engines; gameplay uses native accessors. */
#ifdef PORT_EXPANSION
#define CtrFrontPic(s) (gSpeciesInfo[(s)].frontPic)
#define CtrNormalPal(s) (gSpeciesInfo[(s)].palette)
#define CtrShinyPal(s) (gSpeciesInfo[(s)].shinyPalette)
#define CtrWildInfo(h,member,time) ((h)->encounterTypes[(time)].member)
#define CtrContestDescription(m) (gContestEffects[GetMoveContestEffect(m)].description)
#else
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
