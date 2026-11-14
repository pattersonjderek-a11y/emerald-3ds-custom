/* Stage E project additions; no global RNG, SDK, clock or file dependencies. */
#include "3ds_optional.h"
static uint64_t Next(uint64_t *s)
{
    uint64_t z=(*s+=UINT64_C(0x9E3779B97F4A7C15));
    z=(z^(z>>30))*UINT64_C(0xBF58476D1CE4E5B9);
    z=(z^(z>>27))*UINT64_C(0x94D049BB133111EB);
    return z^(z>>31);
}
uint32_t CtrOptional_Key(uint32_t seed,uint32_t domain,uint32_t a,uint32_t b)
{
    uint64_t s=((uint64_t)seed<<32)|domain;
    s^=(uint64_t)a*UINT64_C(0xD6E8FEB86659FD93);
    s^=(uint64_t)b*UINT64_C(0xA5A3564E27F8862B);
    return (uint32_t)(Next(&s)>>32);
}
static bool Allowed(uint16_t value,const uint16_t *exclude,size_t excluded)
{
    for(size_t i=0;i<excluded;++i) if(value==exclude[i])return false;
    return value!=0;
}
uint16_t CtrOptional_Pick(const uint16_t *pool,size_t count,uint32_t key,
                          const uint16_t *exclude,size_t excluded)
{
    size_t eligible=0; uint64_t s=key; uint32_t v,limit;
    if(!pool||count>UINT16_MAX||(!exclude&&excluded))return 0;
    for(size_t i=0;i<count;++i)if(Allowed(pool[i],exclude,excluded))++eligible;
    if(!eligible)return 0;
    limit=UINT32_MAX-UINT32_MAX%(uint32_t)eligible;
    do v=(uint32_t)(Next(&s)>>32);while(v>=limit);
    size_t pick=v%eligible;
    for(size_t i=0;i<count;++i)if(Allowed(pool[i],exclude,excluded)&&pick--==0)return pool[i];
    return 0;
}
