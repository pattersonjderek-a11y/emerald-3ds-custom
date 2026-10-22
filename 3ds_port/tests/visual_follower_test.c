#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32; typedef int16_t s16; typedef int32_t s32; typedef uint32_t bool32;
#define TRUE 1
#define FALSE 0
#define PORT_BRIDGE 1
#define TAG_NONE 65535
#define TILE_SIZE_4BPP 32
#define TESTING 0
struct SpriteFrameImage { const void *data; u16 size; };
struct SpriteTemplate { u16 tileTag; const struct SpriteFrameImage *images; };
struct SpriteSheet { const void *data; u16 size,tag; };
static unsigned char vram[32768];
#define OBJ_VRAM0 vram
static const u32 stub[2]={0};
static u32 packed[2];
static bool unresolved,failAllocation;
static unsigned rangeTag=TAG_NONE,rangeTiles,loads;
static unsigned decodedBytes=3072;
static bool Port_IsAssetStub(const void *p) { return p==stub; }
static const void *Port_ResolveAssetPointer(const void *p) { return p==stub && !unresolved ? packed:p; }
static u32 Port_GetDecompressedAssetSize(const void *p) { (void)p;return 0; }
static u32 Port_GetAssetSize(const void *p) { return p==stub ? 372:0; }
static const void *Port_ResolveAssetPointerSized(const void *p,u32 size) { (void)size;return Port_ResolveAssetPointer(p); }
static bool IsLZ77Data(const u32 *p,u32 minimum,u32 maximum) { return (*(const u8*)p)==0x10 && (*p>>8)>=minimum && (*p>>8)<maximum; }
static void *malloc_and_decompress(const void *p,u32 *size) {
    assert(p==stub || p==packed);
    if(failAllocation) return NULL;
    void *buffer=malloc(decodedBytes);assert(buffer);
    memset(buffer,0x5a,decodedBytes);if(size)*size=decodedBytes;return buffer;
}
static void Free(void *p) { free(p); }
static u16 GetSpriteTileStartByTag(u16 tag) { return rangeTag==tag ? 7:TAG_NONE; }
static s16 AllocSpriteTiles(u32 count) { assert(count>0 && count<1024);return 7; }
static void AllocSpriteTileRange(u16 tag,u16 start,u32 count) { assert(start==7);rangeTag=tag;rangeTiles=count;++loads; }
static void CpuFill16(u16 value,void *dest,u32 bytes) { assert(!value && !(bytes%2));memset(dest,0,bytes); }
static void CpuSmartCopy16(const void *src,void *dest,u32 bytes) { memcpy(dest,src,bytes); }
static u16 LoadSpriteSheetByTemplate(const struct SpriteTemplate *,u32,s32);
/* PRODUCTION */
static void Check(bool lz77)
{
    // Zero-filled linked placeholder; packed mode 5 is Torchic's real format.
    packed[0]=lz77 ? (decodedBytes<<8)|0x10u : (decodedBytes/4u)<<4|5u;
    packed[1]=0;
    memset(vram,0xcd,sizeof(vram));rangeTag=TAG_NONE;rangeTiles=0;
    assert(IsCompressedData(stub) && GetDecompressedDataSize(stub)==decodedBytes);
    struct SpriteFrameImage image={stub,512};
    struct SpriteTemplate template={123,&image};
    assert(LoadCompressedSpriteSheetByTemplate(&template,512)==7);
    assert(rangeTag==123 && rangeTiles==(decodedBytes+512)/32);
    for(unsigned i=0;i<sizeof(vram);++i) {
        unsigned char expected=i<7*32 || i>=7*32+512+decodedBytes ? 0xcd : i<7*32+512 ? 0:0x5a;
        assert(vram[i]==expected); /* blank frame cannot flash a previous Pokémon */
    }
    unsigned oldLoads=loads;
    assert(LoadCompressedSpriteSheetByTemplate(&template,512)==7 && loads==oldLoads);
    rangeTag=TAG_NONE;failAllocation=true;
    assert(LoadCompressedSpriteSheetByTemplate(&template,512)==TAG_NONE && loads==oldLoads);
    failAllocation=false;
}
int main(void)
{
    Check(false);Check(true);
    struct SpriteFrameImage image={stub,512};
    struct SpriteTemplate template={123,&image};
    assert(LoadCompressedSpriteSheetByTemplate(NULL,512)==TAG_NONE);
    template.images=NULL;assert(LoadCompressedSpriteSheetByTemplate(&template,512)==TAG_NONE);
    unresolved=true;assert(!IsCompressedData(stub));
    puts("PASS production follower sheet path: resolved SMOL/LZ77 headers, complete six-frame sheet, transparent prefix over stale OBJ tiles, caching and allocation failure");
    return 0;
}
