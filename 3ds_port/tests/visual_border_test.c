#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32; typedef int16_t s16; typedef int32_t s32; typedef uint8_t bool8;
#define TRUE 1
#define FALSE 0
#define PORT_BRIDGE 1
#define MAP_OFFSET 7
#define MAPGRID_COLLISION_MASK 0xC00
#define MAPGRID_IMPASSABLE 0xC00
#define MAPGRID_METATILE_ID_MASK 0x3FF
#define UNPACK_METATILE(n) ((n)&MAPGRID_METATILE_ID_MASK)
#define CONNECTION_NORTH 1
#define CONNECTION_SOUTH 2
#define CONNECTION_WEST 3
#define CONNECTION_EAST 4
struct Tileset { unsigned id; };
struct MapLayout { int width,height; const u16 *border; const struct Tileset *primaryTileset,*secondaryTileset; bool isFrlg; u8 borderWidth,borderHeight; };
struct MapConnection { unsigned direction; int offset; u8 mapGroup,mapNum; };
struct MapConnections { int count; const struct MapConnection *connections; };
struct MapHeader { const struct MapLayout *mapLayout; const struct MapConnections *connections; };
static struct MapHeader gMapHeader, neighbors[2];
static struct { struct { u8 mapGroup,mapNum; } location; } save;
#define gSaveBlock1Ptr (&save)
static const void *Port_ResolveAssetPointer(const void *p) { return p; }
static unsigned GetNumMetatilesInPrimary(const struct MapLayout *layout) { (void)layout; return 512; }
static const struct MapHeader *GetMapHeaderFromConnection(const struct MapConnection *c) { assert(c->mapNum<2); return &neighbors[c->mapNum]; }
static struct { int originX,originY; const struct MapLayout *layout; } sInstances[1];
static unsigned sInstanceCount=1;
static int sBorderMemo;
static bool MemoGet(int *memo,const void *source,const void **dest) { (void)memo;(void)source;(void)dest;return false; }
static void MemoPut(int *memo,const void *source,const void *dest) { (void)memo;(void)source;(void)dest; }
/* PRODUCTION */
static void Select(const struct MapLayout *layout,const struct MapConnections *connections)
{
    gMapHeader=(struct MapHeader){layout,connections};
    save.location.mapGroup=1;save.location.mapNum=1;
    sCameraMapCount=0;
    sInstances[0].layout=layout;sInstances[0].originX=0;sInstances[0].originY=0;
}
int main(void)
{
    static const struct Tileset a={1},b={2},c={3};
    static const u16 hoenn[]={1,2,3,4}, different[]={5,6,7,8}, secondary[]={1,2,3,520};
    static const u16 rectangular[]={10,11,12,13,14,15};
    struct MapLayout layout={4,4,hoenn,&a,&b,false,0,0};
    Select(&layout,NULL);
    for(int y=-9;y<20;++y) for(int x=-9;x<20;++x) {
        u8 index=255;
        const u16 *p=MapGridGetCameraBorderAt(x,y,&index);
        assert(p==hoenn && index<4);
        assert(VoxelWorld_BorderMetatile(x,y)==(GetBorderBlockAt(x+MAP_OFFSET,y+MAP_OFFSET)&MAPGRID_METATILE_ID_MASK));
    }
    struct MapLayout neighbor=layout;neighbor.secondaryTileset=&c;neighbor.border=secondary;
    assert(!CameraBorderDrawable(&neighbor)); /* Hoenn's implicit four entries must be examined. */
    neighbor.border=hoenn;assert(CameraBorderDrawable(&neighbor));
    struct MapConnection east={CONNECTION_EAST,0,1,0};
    struct MapConnections linked={1,&east};
    layout.width=5;
    neighbor=layout;neighbor.border=different;neighbors[0]=(struct MapHeader){&neighbor,NULL};
    Select(&layout,&linked);UpdateCameraMaps();
    assert(sCameraMapCount==2 && sCameraMaps[0].phaseX==0); /* different border: no zero-byte memcmp alias */
    neighbor.border=hoenn;Select(&layout,&linked);UpdateCameraMaps();
    assert(sCameraMaps[0].phaseX==5); /* same border uses lower stable map ID */
    int samples[30];
    for(int x=-9;x<21;++x) samples[x+9]=VoxelWorld_BorderMetatile(x,-5);
    struct MapConnection west={CONNECTION_WEST,0,1,1};
    struct MapConnections back={1,&west};
    neighbors[1]=(struct MapHeader){&layout,&linked};
    Select(&neighbor,&back);save.location.mapNum=0;
    for(int x=-9;x<21;++x) assert(VoxelWorld_BorderMetatile(x-5,-5)==samples[x+9]);
    layout.isFrlg=true;layout.borderWidth=3;layout.borderHeight=2;layout.border=rectangular;
    Select(&layout,NULL);
    for(int y=-9;y<20;++y) for(int x=-9;x<20;++x) {
        unsigned ix=(x%3+3)%3,iy=(y%2+2)%2;
        assert(VoxelWorld_BorderMetatile(x,y)==rectangular[ix+iy*3]);
        assert(VoxelWorld_BorderMetatile(x,y)==(GetBorderBlockAt(x+MAP_OFFSET,y+MAP_OFFSET)&MAPGRID_METATILE_ID_MASK));
    }
    layout.borderWidth=0;Select(&layout,NULL);
    u8 index=255;assert(MapGridGetCameraBorderAt(-5,2,&index)==NULL);
    assert(!CameraBorderDrawable(&layout));
    assert(VoxelWorld_BorderMetatile(-5,2)==-1);
    puts("PASS production camera/voxel borders: implicit Hoenn, rectangular FRLG, negative coordinates, native 2D phase, tileset rejection and stable phase anchors");
    return 0;
}
