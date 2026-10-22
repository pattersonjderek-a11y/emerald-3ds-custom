#include "custom_random_core.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void)
{
    struct CRDraft draft; CR_Begin(&draft,12345,1);
    struct CRConfig c=draft.config;
    c.mode=CR_RANDOMIZED; c.algorithm=CR_ALGORITHM; c.randomOptions=CR_CORE_OPTIONS;
    struct CRPoolEntry pool[30];
    for(unsigned i=0;i<27;++i) pool[i]=(struct CRPoolEntry){i+1,300+(i%3)*20,i/3+1,i%3==2,1};
    pool[27]=(struct CRPoolEntry){28,600,9,0,20};
    pool[28]=(struct CRPoolEntry){29,300,0,0,1};
    pool[29]=(struct CRPoolEntry){30,300,10,0,1};
    assert(CR_Validate(&c)==CR_OK);
    c.contentRules=CR_RULES_STAGE_C; /* C saves retain their historical key. */
    const uint32_t golden[]={0x5151ed33u,0x143b4572u,0x74e5cf8au,0xdceb3b81u};
    for(unsigned i=0;i<4;++i) assert(CRandom_Key(&c,CR_STREAM_STARTERS+i,7,12,3)==golden[i]);
    c.contentRules=CR_CONTENT_RULES;
    unsigned variation=0;
    for(unsigned seed=0;seed<10000;++seed) {
        c.seed=seed; c.generations=1u<<(seed%9); c.balanceFlags=CR_BALANCE_NO_LEGENDS;
        uint16_t chosen[3]={0};
        for(unsigned slot=0;slot<2;++slot) {
            chosen[slot]=CRandom_Pick(&c,pool,30,CR_STREAM_STARTERS,0,0,slot,320,5,chosen,slot);
            assert(chosen[slot] && pool[chosen[slot]-1].generation==seed%9+1 && !pool[chosen[slot]-1].legendary);
            if(slot) assert(chosen[0]!=chosen[1]);
        }
        assert(CRandom_Pick(&c,pool,30,CR_STREAM_STARTERS,0,0,2,320,5,chosen,2)==0);
        uint16_t first=CRandom_Pick(&c,pool,30,CR_STREAM_WILD,102,1,3,320,5,NULL,0);
        assert(first==CRandom_Pick(&c,pool,30,CR_STREAM_WILD,102,1,3,320,5,NULL,0));
        c.randomOptions^=CR_RANDOM_TRAINERS;
        assert(first==CRandom_Pick(&c,pool,30,CR_STREAM_WILD,102,1,3,320,5,NULL,0));
        variation|=first!=1;
    }
    assert(variation);
    c.generations=0; assert(!CRandom_Pick(&c,pool,30,CR_STREAM_WILD,0,0,0,300,5,NULL,0));
    c.generations=256; c.balanceFlags=CR_BALANCE_SIMILAR;
    assert(CRandom_Pick(&c,pool,30,CR_STREAM_WILD,0,0,0,10,5,NULL,0)); /* finite BST fallback */
    assert(!CRandom_Pick(&c,NULL,0,CR_STREAM_WILD,0,0,0,300,5,NULL,0));
    uint32_t state=0, buckets[7]={0};
    for(unsigned i=0;i<700000;++i) ++buckets[CRandom_Bounded(&state,7)];
    for(unsigned i=0;i<7;++i) assert(buckets[i]>98000 && buckets[i]<102000);
    assert(CRandom_Bounded(&state,0)==0);
    puts("pure core: 10k seeds, generations/legends/levels, distinct choices, stream independence, empty pools, finite fallback, bounded selection PASS");
    return 0;
}
