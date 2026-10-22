"""Compile production run configuration, menu, save adapter and sector code.

Hardware graphics/input and power-loss behavior remain separate device tests.
No ROM or private save fixture is needed: all game-progress buffers are synthetic.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile
from voxel_runtime_test import function

HERE = Path(__file__).resolve().parent


def run(cc, tree, source, extra=()):
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary)
        (path / 'test.c').write_text(source)
        subprocess.run([cc, '-std=gnu11', '-g', '-O1', '-Wall', '-Werror',
                        '-Wno-unused-parameter', '-Wno-sign-compare',
                        '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                        '-fno-pie', '-no-pie', '-iquote', str(tree / 'include'),
                        str(path / 'test.c'), str(tree / 'src/custom_run_config.c'),
                        str(tree / 'src/custom_run_menu_model.c'), *extra,
                        '-o', str(path / 'test')], check=True)
        subprocess.run([str(path / 'test')], check=True)


def adapter(tree):
    actual = (tree / 'src/custom_run.c').read_text()
    source = r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "custom_run_menu_model.h"
#define CustomRandom_Validate(c) ((void)(c),true)
typedef uint8_t u8;
static struct { u8 prefix[0x988], customRunConfig[52]; uint32_t money; uint16_t registeredItem; } save1;
static struct { u8 playerTrainerId[4]; uint32_t encryptionKey; u8 specialSaveWarpFlags,gcnLinkFlags; } save2;
#define gSaveBlock1Ptr (&save1)
#define gSaveBlock2Ptr (&save2)
static struct CRMenu sMenu;
'''
    for signature in ['static uint32_t TrainerId(void)',
                      'enum CRStatus CustomRun_Read(', 'bool CustomRun_CanPlay(',
                      'bool CustomRun_HasConfirmedDraft(', 'bool CustomRun_CommitNewSave(']:
        source += function(actual, signature)
    # Execute the complete real initialization routine; unrelated subsystems are
    # no-ops, but the destructive clear and trainer-ID initialization are real
    # fixture operations. Hook order is therefore exercised, not string matched.
    init = function((tree / 'src/new_game.c').read_text(), 'void NewGameInitData(void)')
    source += r'''
#define PORT_BRIDGE 1
#define IS_FRLG 0
#define TRUE 1
#define SAVE_STATUS_EMPTY 0
#define SAVE_STATUS_CORRUPT 2
#define B_TRAINER_PLAYER 0
#define ITEM_NONE 0
#define DIFFICULTY_NORMAL 0
#define EventScript_ResetAllMapFlagsFrlg 1
#define EventScript_ResetAllMapFlags 2
static unsigned gSaveFileStatus, gDifferentSaveFile, gPartiesCount[1];
static void ClearSav1(void) { memset(&save1,0,sizeof(save1)); }
static void InitPlayerTrainerId(void) { save2.playerTrainerId[0]=123; }
static void SetMoney(uint32_t *p,unsigned n) { *p=n; }
static void SetCoins(unsigned n) { (void)n; }
static void RunScriptImmediately(unsigned n) { (void)n; }
static void SetCurrentDifficultyLevel(unsigned n) { assert(n==DIFFICULTY_NORMAL); }
'''
    import re
    names = set(re.findall(r'^\s+(\w+)\(\);', init, re.M))
    names -= {'ClearSav1', 'InitPlayerTrainerId', 'CustomRun_CommitNewSave'}
    source += ''.join(f'static void {name}(void) {{}}\n' for name in sorted(names))
    source += init
    source += r'''
int main(void) {
    struct CRConfig c;
    uint8_t old[sizeof(save1)];
    assert(CustomRun_CanPlay() && CustomRun_Read(NULL)==CR_LEGACY);
    save2.playerTrainerId[0]=123;
    CR_MenuBegin(&sMenu,42,100);
    assert(!CustomRun_HasConfirmedDraft());
    assert(CR_Confirm(&sMenu.draft));
    NewGameInitData();
    assert(CustomRun_Read(&c)==CR_OK && c.seed==42 && c.runId==100);
    assert(!CustomRun_HasConfirmedDraft() && !CustomRun_CommitNewSave());
    memcpy(old,&save1,sizeof(save1));
    CR_MenuBegin(&sMenu,88,200); CR_Cancel(&sMenu.draft);
    assert(!CustomRun_CommitNewSave() && !memcmp(old,&save1,sizeof(save1)));
    for(unsigned i=0;i<100;++i) assert(CustomRun_Read(&c)==CR_OK && c.seed==42 && c.runId==100);
    CR_MenuBegin(&sMenu,99,201); assert(CR_Confirm(&sMenu.draft));
    NewGameInitData();
    assert(CustomRun_Read(&c)==CR_OK && c.seed==99 && c.runId==201);
    save2.playerTrainerId[0]^=1; assert(!CustomRun_CanPlay() && CustomRun_Read(NULL)==CR_BINDING);
    save2.playerTrainerId[0]^=1;
    save1.customRunConfig[8]^=1; assert(!CustomRun_CanPlay() && CustomRun_Read(NULL)==CR_CORRUPT);
    puts("native save adapter + complete NewGameInitData: post-clear commit, cancellation, reset, Continue reads, binding PASS");
    return 0;
}
'''
    return source


def sectors(tree):
    save = (tree / 'src/save.c').read_text()
    header = (tree / 'include/save.h').read_text()
    source = r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "custom_run_config.h"
#define CustomRandom_Validate(c) ((void)(c),true)
typedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32; typedef uint8_t bool8;
#define TRUE 1
#define FALSE 0
'''
    source += header.split('#include "main.h"', 1)[1].split('extern u16', 1)[0]
    source += r'''
static struct SaveSector flash[28], gSaveDataBuffer;
static struct SaveSector *gReadWriteSector=&gSaveDataBuffer;
static u16 gLastWrittenSector;
static u32 gSaveCounter;
static void CopyFromSaveBlock3(u32 id,struct SaveSector *s) { (void)id; (void)s; }
static void CopyToSaveBlock3(u32 id,struct SaveSector *s) { (void)id; (void)s; }
static u8 TryWriteSector(u8 sector,u8 *data) { memcpy(&flash[sector],data,SECTOR_SIZE); return SAVE_STATUS_OK; }
static bool8 ReadFlashSector(u8 sector,struct SaveSector *out) { *out=flash[sector]; return TRUE; }
'''
    for signature in ['static u16 CalculateChecksum(void *data,',
                      'static u8 HandleWriteSector(u16 sectorId,',
                      'static u8 CopySaveSlotData(u16 sectorId,',
                      'static u8 GetSaveValidStatus(const struct SaveSectorLocation *locations)\n{',
                      'static u8 TryLoadSaveSlot(u16 sectorId,']:
        source += function(save, signature)
    source += r'''
static _Alignas(4) uint8_t buffers[14][3968];
static struct SaveSectorLocation locations[14];
static void SaveAll(unsigned counter,unsigned seed) {
    struct CRDraft d;
    CR_Begin(&d,seed,counter); assert(CR_Confirm(&d));
    assert(CR_Commit(&d,buffers[1]+0x988,123));
    gSaveCounter=counter; gLastWrittenSector=counter%14;
    for(unsigned i=0;i<14;++i) assert(HandleWriteSector(i,locations)==SAVE_STATUS_OK);
}
int main(void) {
    struct CRConfig c;
    assert(sizeof(struct SaveSector)==4096);
    for(unsigned i=0;i<14;++i) locations[i]=(struct SaveSectorLocation){buffers[i],3968};
    SaveAll(2,42); SaveAll(3,99);
    memset(buffers,0,sizeof(buffers));
    assert(TryLoadSaveSlot(FULL_SAVE_SLOT,locations)==SAVE_STATUS_OK);
    assert(gSaveCounter==3 && CR_Decode(buffers[1]+0x988,123,&c)==CR_OK && c.seed==99);
    /* Alter a record byte, without updating the native sector checksum. The
       real loader must reject the newest slot and recover the older full slot. */
    flash[14+4].data[0x988+8]^=1;
    memset(buffers,0,sizeof(buffers));
    assert(TryLoadSaveSlot(FULL_SAVE_SLOT,locations)==SAVE_STATUS_ERROR);
    assert(gSaveCounter==2 && CR_Decode(buffers[1]+0x988,123,&c)==CR_OK && c.seed==42);
    /* Native checksum may be valid but internal record CRC invalid: do not
       silently run as Standard or generate a replacement seed. */
    flash[3].data[0x988+8]^=1;
    flash[3].checksum=CalculateChecksum(flash[3].data,3968);
    memset(buffers,0,sizeof(buffers)); TryLoadSaveSlot(FULL_SAVE_SLOT,locations);
    assert(CR_Decode(buffers[1]+0x988,123,NULL)==CR_CORRUPT);
    assert(TryLoadSaveSlot(1,locations)==SAVE_STATUS_ERROR);
    puts("native sector write/load/checksum + two-slot fallback: record round trip and corruption recovery PASS");
    return 0;
}
'''
    return source


def guards(tree):
    actual = (tree / 'src/custom_run.c').read_text()
    source = r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "custom_run_config.h"
#define CustomRandom_Validate(c) ((void)(c),true)
typedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32; typedef uint8_t bool8;
#define PORT_BRIDGE 1
#define TRUE 1
#define FALSE 0
static struct { u8 customRunConfig[52]; } save1;
static struct { u8 playerTrainerId[4]; } save2;
#define gSaveBlock1Ptr (&save1)
#define gSaveBlock2Ptr (&save2)
'''
    for signature in ['static uint32_t TrainerId(void)', 'enum CRStatus CustomRun_Read(', 'bool CustomRun_CanPlay(']:
        source += function(actual, signature)
    header = (tree / 'include/save.h').read_text()
    source += header.split('#include "main.h"', 1)[1].split('extern u16', 1)[0]
    source += r'''
static unsigned effects, viewed, writes;
static void Noop(void) { ++effects; }
static void CB2_InitMainMenu(void) {}
static void CustomRunMenu_View(void (*cb)(void)) { assert(cb==CB2_InitMainMenu); ++viewed; }
static void CB2_LoadMap(void) {}
static void CB1_Overworld(void) {}
static void FieldCB_FadeTryShowMapPopup(void) {}
static void (*gFieldCallback)(void);
static unsigned gExitStairsMovementDisabled, gSaveFileStatus, gSaveAttemptStatus, gDamagedSaveSectors;
static unsigned gFlashMemoryPresent=TRUE;
static u32 *gTrainerHillVBlankCounter;
static void *gHoFSaveBuffer;
static struct { unsigned mapLayoutId; } gMapHeader;
#define LAYOUT_BATTLE_FRONTIER_BATTLE_PYRAMID_FLOOR 99
#define TRAINER_HILL_ENTRANCE 1
#define GAME_STAT_ENTERED_HOF 1
static struct SaveSectorLocation gRamSaveSectorLocations[14];
#define SetMainCallback1(cb) ((void)(cb),++effects)
#define SetMainCallback2(cb) ((void)(cb),++effects)
#define InitBattlePyramidMap(n) (++effects)
#define GetCurrentTrainerHillMapId() 0
#define UseContinueGameWarp() 0
#define GetGameStat(n) 0
#define IncrementGameStat(n) (++effects)
#define EraseFlashSector(n) (++writes)
#define WriteSaveSectorOrSlot(a,b) ((void)(a),(void)(b),++writes)
#define HandleWriteSectorNBytes(a,b,c) ((void)(a),(void)(b),(void)(c),++writes)
#define HandleReplaceSector(a,b) ((void)(a),(void)(b),++writes)
#define WriteSectorSignatureByte_NoOffset(a,b) ((void)(a),(void)(b),++writes)
#define RestoreSaveBackupVarsAndIncrement(a) ((void)(a),++writes)
#define DoSaveFailedScreen(n) (++effects)
'''
    cont = function((tree / 'src/overworld.c').read_text(), 'void CB2_ContinueSavedGame(void)')
    save = (tree / 'src/save.c').read_text()
    functions = cont + function(save, 'u8 HandleSavingData(u8 saveType)')
    functions += function(save, 'u8 TrySavingData(u8 saveType)')
    functions += function(save, 'bool8 LinkFullSave_Init(void)')
    import re
    names = set(re.findall(r'^\s+(\w+)\(\);', functions, re.M))
    source += ''.join(f'#define {name} Noop\n' for name in sorted(names))
    source += functions
    source += r'''
int main(void) {
    struct CRDraft d; u8 old[52];
    save2.playerTrainerId[0]=123;
    CR_Begin(&d,42,5); assert(CR_Confirm(&d)); assert(CR_Commit(&d,save1.customRunConfig,123));
    memcpy(old,save1.customRunConfig,52);
    CB2_ContinueSavedGame(); assert(effects && !viewed && !memcmp(old,save1.customRunConfig,52));
    assert(TrySavingData(SAVE_NORMAL)==SAVE_STATUS_OK && writes);
    effects=writes=0;
    /* A valid CRC with a future schema must be blocked, preserving bytes. */
    save1.customRunConfig[4]=2;
    u32 crc=CR_Crc32(save1.customRunConfig,48);
    for(unsigned i=0;i<4;++i) save1.customRunConfig[48+i]=crc>>(8*i);
    memcpy(old,save1.customRunConfig,52);
    CB2_ContinueSavedGame(); assert(viewed==1 && !effects && !writes);
    for(unsigned type=0;type<6;++type) {
        assert(TrySavingData(type)==SAVE_STATUS_ERROR && gSaveAttemptStatus==SAVE_STATUS_ERROR);
        assert(!effects && !writes && !memcmp(old,save1.customRunConfig,52));
    }
    assert(LinkFullSave_Init()==TRUE && !effects && !writes);
    save1.customRunConfig[48]^=1;
    CB2_ContinueSavedGame(); assert(viewed==2 && !effects && !writes);
    memset(save1.customRunConfig,0,52); CB2_ContinueSavedGame(); assert(effects && viewed==2);
    puts("production Continue/save guards: future/corrupt blocked before side effects; legacy/recorded fixed runs allowed PASS");
    return 0;
}
'''
    return source


def start_access(tree):
    actual = (tree / 'src/start_menu.c').read_text()
    source = r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
typedef uint8_t u8; typedef int bool8;
#define PORT_BRIDGE 1
#define TRUE 1
#define FALSE 0
#define MENU_ACTION_NONE_CTR 255
#define FLAG_GET_SEEN 1
#define FADE_TO_BLACK 1
static u8 sCtrRequest=MENU_ACTION_NONE_CTR;
static bool8 replaced=TRUE;
static unsigned frozen, taskCreated, faded;
static unsigned seen=1;
static bool8 CtrStartMenu_IsReplaced(void) { return replaced; }
static unsigned GetNationalPokedexCount(unsigned flag) { assert(flag==FLAG_GET_SEEN); return seen; }
static void FreezeObjectEvents(void) { ++frozen; }
static void PlayerFreeze(void) {}
static void StopPlayerAvatar(void) {}
static void LockPlayerFieldControls(void) {}
static void AddStartMenuWindow(unsigned n) { assert(n==1); }
static void FadeScreen(unsigned kind,unsigned n) { assert(kind==FADE_TO_BLACK && !n); ++faded; }
static bool8 RunPage(void) { return TRUE; }
static bool8 OtherPage(void) { return TRUE; }
static bool8 CtrSaveStartCallback(void) { return TRUE; }
static bool8 (*gMenuCallback)(void);
static void Task_CtrStartMenuAction(u8 id) { (void)id; }
static void CreateTask(void (*fn)(u8),unsigned priority) { assert(fn==Task_CtrStartMenuAction && priority==0x50); ++taskCreated; }
'''
    source += actual.split('// Menu actions', 1)[1].split('// Save status', 1)[0]
    source += r'''
static const struct { struct { bool8 (*u8_void)(void); } func; } sStartMenuItems[] = {
 [MENU_ACTION_RUN_SETTINGS]={{RunPage}}, [MENU_ACTION_BAG]={{OtherPage}},
 [MENU_ACTION_POKEDEX]={{OtherPage}}
};
'''
    source += function(actual, 'static bool8 CtrStartMenu_Divert(void)\n{')
    source += function(actual, 'bool8 CtrStartMenu_AcceptStart(void)')
    source += r'''
int main(void) {
    /* The actual dual-screen adapter consumes plain physical START. */
    assert(CtrStartMenu_AcceptStart() && sCtrRequest==MENU_ACTION_RUN_SETTINGS);
    assert(CtrStartMenu_Divert() && sCtrRequest==MENU_ACTION_NONE_CTR);
    assert(gMenuCallback==RunPage && frozen==1 && faded==1 && taskCreated==1);
    sCtrRequest=MENU_ACTION_BAG;
    assert(CtrStartMenu_AcceptStart() && CtrStartMenu_Divert() && gMenuCallback==OtherPage);
    sCtrRequest=MENU_ACTION_SAVE;
    assert(CtrStartMenu_AcceptStart() && CtrStartMenu_Divert() && gMenuCallback==CtrSaveStartCallback);
    sCtrRequest=MENU_ACTION_POKEDEX; seen=0;
    assert(!CtrStartMenu_AcceptStart() && sCtrRequest==MENU_ACTION_NONE_CTR);
    sCtrRequest=MENU_ACTION_EXIT; assert(!CtrStartMenu_AcceptStart());
    replaced=FALSE; sCtrRequest=MENU_ACTION_NONE_CTR;
    assert(CtrStartMenu_AcceptStart() && !CtrStartMenu_Divert());
    puts("production dual-screen START adapter: Run Settings reachable; bag/save/Dex and classic fallback retained PASS");
    return 0;
}
'''
    return source


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tree', type=Path, required=True)
    parser.add_argument('--cc', default='cc')
    args = parser.parse_args()
    tree = args.tree.resolve()
    run(args.cc, tree, (HERE / 'custom_run_test.c').read_text())
    run(args.cc, tree, adapter(tree))
    run(args.cc, tree, sectors(tree))
    run(args.cc, tree, guards(tree))
    run(args.cc, tree, start_access(tree))
    print('Production run configuration tests PASS (ASan + UBSan)')


if __name__ == '__main__':
    main()
