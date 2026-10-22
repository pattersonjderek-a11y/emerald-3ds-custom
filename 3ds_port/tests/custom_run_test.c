/* Host fixture linked to the actual engine codec and menu model. */
#include "custom_run_config.h"
#include "custom_run_menu_model.h"
#include "custom_random_core.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static void FixCrc(uint8_t *b)
{
    uint32_t n=CR_Crc32(b,48);
    for(unsigned i=0;i<4;++i) b[48+i]=(uint8_t)(n>>(i*8));
}
static void Reject(uint8_t *b, enum CRStatus status)
{
    struct CRConfig out, before;
    memset(&out,0xA5,sizeof(out)); before=out;
    assert(CR_Decode(b,123,&out)==status);
    assert(!memcmp(&out,&before,sizeof(out)));
}
static void Storage(void)
{
    uint8_t saveBlock1[15536];
    struct CRDraft d;
    memset(saveBlock1,0xA5,sizeof(saveBlock1));
    CR_Begin(&d,42,77); assert(CR_Confirm(&d));
    assert(CR_Commit(&d,saveBlock1+0x988,123));
    for(unsigned i=0;i<sizeof(saveBlock1);++i)
        if(i<0x988 || i>=0x988+52) assert(saveBlock1[i]==0xA5);
    /* Includes native event flags (0x1270) and variables (0x139C). */
    assert(saveBlock1[0x1270]==0xA5 && saveBlock1[0x139C]==0xA5);
    puts("storage reservation: every byte outside 52-byte record, flags and variables preserved PASS");
}
static void Codec(void)
{
    const uint32_t seeds[]={0,1,42,2147483648u,UINT32_MAX};
    uint8_t b[52], pristine[52];
    struct CRDraft d;
    struct CRConfig c;
    assert(CR_Crc32((const uint8_t *)"123456789",9)==0xCBF43926u);
    for(unsigned i=0;i<5;++i) {
        CR_Begin(&d,seeds[i],900+i);
        assert(!CR_Commit(&d,b,123));
        assert(CR_Confirm(&d)); assert(CR_Commit(&d,b,123));
        assert(!CR_Commit(&d,b,123));
        assert(CR_Decode(b,123,&c)==CR_OK);
        assert(c.seed==seeds[i] && c.runId==900+i && c.mode==CR_STANDARD && c.difficulty==CR_NORMAL);
        assert(c.algorithm==0 && c.contentRules==CR_CONTENT_RULES && c.generations==CR_GENERATIONS);
        memcpy(pristine,b,52);
        for(unsigned byte=0;byte<52;++byte) for(unsigned bit=0;bit<8;++bit) {
            memcpy(b,pristine,52); b[byte]^=1u<<bit; Reject(b,CR_CORRUPT);
        }
        memcpy(b,pristine,52);
        assert(CR_Decode(b,124,NULL)==CR_BINDING);
        for(unsigned n=0;n<100;++n) assert(CR_Decode(b,123,&c)==CR_OK && c.seed==seeds[i]);
    }
    const unsigned positions[]={4,6,32,44,20,12,16,34,36,37,38,39,40};
    const enum CRStatus statuses[]={CR_VERSION,CR_VERSION,CR_VERSION,CR_VERSION,CR_CONTENT,CR_RULES,CR_RULES,CR_RULES,CR_RULES,CR_RULES,CR_RULES,CR_RULES,CR_RULES};
    for(unsigned i=0;i<sizeof(positions)/sizeof(*positions);++i) {
        memcpy(b,pristine,52); b[positions[i]]^=1; FixCrc(b); Reject(b,statuses[i]);
    }
    for(unsigned fill=0;fill<2;++fill) { memset(b,fill?255:0,52); Reject(b,CR_LEGACY); }
    c.mode=CR_RANDOMIZED; memset(b,0xA5,52); memcpy(pristine,b,52);
    assert(!CR_Encode(b,123,&c) && !memcmp(b,pristine,52));
    CR_Begin(&d,42,100); d.config.mode=CR_RANDOMIZED; d.config.algorithm=CR_ALGORITHM;
    d.config.randomOptions=CR_CORE_OPTIONS; d.config.generations=256; d.config.balanceFlags=3;
    assert(CR_Confirm(&d) && CR_Commit(&d,b,123));
    assert(CR_Decode(b,123,&c)==CR_OK && c.randomOptions==7 && c.generations==256 && c.balanceFlags==3);
    c.randomOptions|=CR_RANDOM_ABILITIES; assert(!CR_Encode(b,123,&c));
    CR_Begin(&d,42,100); d.config.contentRules=0x00010001u;
    assert(CR_Confirm(&d) && CR_Commit(&d,b,123) && CR_Decode(b,123,&c)==CR_OK && c.algorithm==0);
    CR_Begin(&d,123,100); d.config.difficulty=CR_HARD; assert(!CR_Confirm(&d));
    CR_SetDifficulty(&d.config,CR_HARD); assert(CR_Confirm(&d));
    CR_Cancel(&d); assert(!d.editing && !d.confirmed && !CR_Commit(&d,b,123));
    uint32_t seed=77;
    const char *bad[]={"","-1","+1"," 1","1 ","0x10","4294967296","9999999999","00000000000","1a",NULL};
    for(unsigned i=0;i<sizeof(bad)/sizeof(*bad);++i) { assert(!CR_ParseSeed(bad[i],&seed)); assert(seed==77); }
    assert(CR_ParseSeed("0000000000",&seed) && seed==0);
    assert(CR_ParseSeed("4294967295",&seed) && seed==UINT32_MAX);
    puts("codec: round trips, all 416 single-bit corruptions, versions/rules/binding, legacy, parsing PASS");
}
static enum CROutcome Key(struct CRMenu *m,unsigned k) { return CR_MenuInput(m,k,56789); }
static void Menu(void)
{
    struct CRMenu m;
    CR_MenuBegin(&m,123,456);
    Key(&m,CR_DOWN); Key(&m,CR_A); assert(m.page==CR_PAGE_DIFFICULTY && m.draft.config.mode==CR_RANDOMIZED);
    assert(m.draft.config.randomOptions==CR_CORE_OPTIONS && m.draft.config.algorithm==1);
    Key(&m,CR_DOWN); Key(&m,CR_A); assert(m.page==CR_PAGE_SEED && m.draft.config.difficulty==CR_HARD);
    Key(&m,CR_B); m.selected=2; Key(&m,CR_A); assert(m.page==CR_PAGE_DIFFICULTY_CUSTOM);
    m.selected=6; Key(&m,CR_A); assert(m.page==CR_PAGE_SEED && m.draft.config.difficulty==CR_CUSTOM);
    m.selected=2; Key(&m,CR_A); assert(m.page==CR_PAGE_CUSTOM);
    for(unsigned i=3;i<6;++i) { m.selected=i; Key(&m,CR_A); assert(m.notice && m.draft.config.randomOptions==CR_CORE_OPTIONS); }
    m.selected=0; Key(&m,CR_A); assert(m.draft.config.randomOptions==6);
    m.selected=1; Key(&m,CR_A); assert(m.draft.config.randomOptions==4);
    m.selected=2; Key(&m,CR_A); assert(m.notice && m.draft.config.randomOptions==4);
    m.selected=0; Key(&m,CR_A); m.selected=1; Key(&m,CR_A);
    m.selected=6; Key(&m,CR_A); assert(m.page==CR_PAGE_GENERATIONS);
    for(unsigned i=0;i<8;++i) { m.selected=i; Key(&m,CR_A); }
    m.selected=8; Key(&m,CR_A); assert(m.notice && m.draft.config.generations==256);
    m.selected=9; Key(&m,CR_A); assert(m.page==CR_PAGE_CUSTOM);
    m.selected=7; Key(&m,CR_A); assert(m.page==CR_PAGE_BALANCE);
    Key(&m,CR_A); assert(m.draft.config.balanceFlags==CR_BALANCE_NO_LEGENDS);
    Key(&m,CR_B); Key(&m,CR_B); assert(m.page==CR_PAGE_SEED);
    assert(m.draft.config.seed==123); Key(&m,CR_A); assert(m.draft.config.seed==56789);
    Key(&m,CR_DOWN); Key(&m,CR_A); assert(m.page==CR_PAGE_DIGITS);
    strcpy(m.digits,"4294967296"); Key(&m,CR_A); assert(m.page==CR_PAGE_DIGITS && m.notice && m.draft.config.seed==56789);
    strcpy(m.digits,"4294967295"); Key(&m,CR_A); assert(m.page==CR_PAGE_SEED && m.draft.config.seed==UINT32_MAX && m.draft.manualSeed);
    Key(&m,CR_DOWN); Key(&m,CR_A); Key(&m,CR_UP); Key(&m,CR_B); assert(m.draft.config.seed==UINT32_MAX); /* discard edit */
    Key(&m,CR_DOWN); Key(&m,CR_DOWN); Key(&m,CR_DOWN); Key(&m,CR_A); assert(m.page==CR_PAGE_SUMMARY && !m.draft.confirmed);
    assert(Key(&m,CR_A)==CR_ACCEPTED && m.draft.confirmed);
    struct CRMenu accepted=m; Key(&m,CR_B); Key(&m,CR_DOWN); assert(!memcmp(&m,&accepted,sizeof(m)));
    uint8_t record[52], old[52]; memset(record,0x5A,52); memcpy(old,record,52);
    CR_MenuBegin(&m,3,4); assert(Key(&m,CR_B)==CR_CANCELLED);
    assert(!CR_Commit(&m.draft,record,1) && !memcmp(record,old,52));
    /* Explore actual input transitions and rendered labels under sanitizers. */
    for(unsigned trial=0;trial<100;++trial) {
        CR_MenuBegin(&m,trial,trial+1);
        uint32_t rng=trial+1;
        for(unsigned step=0;step<500;++step) {
            char lines[12][36]; CR_MenuLines(&m,lines);
            for(unsigned row=0;row<12;++row) assert(strlen(lines[row])<36);
            rng=rng*1664525u+1013904223u;
            enum CROutcome outcome=Key(&m,1u<<(rng%6));
            assert(CR_Validate(&m.draft.config)==CR_OK || outcome==CR_CANCELLED);
            if(outcome!=CR_STAY) break;
        }
    }
    puts("menu: randomized core, category/generation/balance options, locked later rules, auto/manual seed, overflow, confirmation, cancel and 50k transition budget PASS");
}
int main(void) { Storage(); Codec(); Menu(); return 0; }
