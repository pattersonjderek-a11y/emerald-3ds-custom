#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#define CTR_VOXEL_ENABLED 1
static bool sBattle=true,sBattleWorld,enabled=true,scenic=true,available=true,inBattle,sliding,moveBg;
static unsigned sWorldLayers,work,begins,updates,idles;
static unsigned display=0x800;
static bool CtrSettings_Voxel(void) { return enabled; }
static bool CtrSettings_VoxelBattle(void) { return scenic; }
static bool CtrVoxel_IsAvailableForBattle(void) { return available; }
static bool CtrBattleIntro_Sliding(void) { return sliding; }
static bool CtrBattleBg_MoveBgShown(void) { return moveBg; }
static bool CtrVoxel_InBattle(void) { return inBattle; }
static void CtrVoxel_BeginBattle(void) { inBattle=true;++begins; }
static float BattleScenerySway(unsigned n) { return (float)n; }
static void CtrVoxel_SetBattleFrame(bool intro,float x,float y) { if(intro || moveBg) assert(x==0 && y==0); }
static bool CtrVoxel_Update(void) { ++updates;return work>=2; }
static bool VoxelBattle_IsLink(void) { return false; }
static unsigned Reg(unsigned n) { assert(!n);return display; }
static void CtrVoxel_AfterSubmit(uint64_t start) { (void)start;++work; }
static void CtrVoxel_Idle(void) { ++idles; }
/* PRODUCTION */
int main(void)
{
    // New scene cannot draw until two post-submit build slices have run.
    assert(!Frame(false) && work==1);
    assert(!Frame(false) && work==2);
    assert(Frame(false) && inBattle && begins==1 && sWorldLayers==(1u<<3));
    sliding=true;assert(Frame(false) && sWorldLayers==14);sliding=false;
    moveBg=true;assert(!Frame(false) && sWorldLayers==0);moveBg=false;
    assert(Frame(false));
    display|=128;assert(!Frame(false));display&=~128u;assert(Frame(false));
    scenic=false;unsigned oldWork=work,oldUpdates=updates;
    assert(!Frame(false) && updates==oldUpdates && work==oldWork);scenic=true;
    available=false;assert(!Frame(false) && updates==oldUpdates && work==oldWork);available=true;
    enabled=false;assert(!Frame(false) && updates==oldUpdates && work==oldWork);enabled=true;
    sBattle=false;assert(!Frame(false) && updates==oldUpdates && work==oldWork);
    assert(!Frame(true) && work==oldWork+1); /* field preparation retained */
    assert(idles>=4);
    puts("PASS production scenic scheduler: pending scene progresses through flat fallback; one begin, native intro/move background/forced blank fallbacks and disabled/unavailable states");
    return 0;
}
