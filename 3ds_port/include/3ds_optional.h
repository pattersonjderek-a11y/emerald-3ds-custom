#ifndef CTR_OPTIONAL_H
#define CTR_OPTIONAL_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
/* Independent domains; changing optional toggles never rebuilds the species permutation. */
#define CTR_OPT_ABILITY 0x4142494cu
#define CTR_OPT_FIELD 0x4649544du
#define CTR_OPT_HELD 0x4849544du
uint32_t CtrOptional_Key(uint32_t seed,uint32_t domain,uint32_t a,uint32_t b);
uint16_t CtrOptional_Pick(const uint16_t *pool,size_t count,uint32_t key,
                          const uint16_t *exclude,size_t excluded);
uint16_t CtrOptional_Ability(uint16_t species,unsigned slot,uint16_t native);
uint16_t CtrOptional_Field(uint16_t item,unsigned kind,unsigned localId);
uint16_t CtrOptional_Held(uint16_t item,unsigned identity,unsigned slot);
void CtrOptional_WildHeld(void);
#endif
