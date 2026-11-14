/* Native expansion ABI adapters for authoritative v0.5.0 platform options. */
#include "global.h"
#include "3ds_extras.h"
#include "3ds_expansion.h"
#ifdef PORT_EXPANSION
#include "move.h"
uint8_t MoveSplitEnabled(void){return CtrExtras_Get("move_split")!=0;}
uint8_t CtrExpansion_MoveCategory(uint16_t move,uint8_t category)
{
    if(category==DAMAGE_CATEGORY_NONE || category==DAMAGE_CATEGORY_STATUS || MoveSplitEnabled())return category;
    return GetMoveType(move)>=TYPE_FIRE ? DAMAGE_CATEGORY_SPECIAL : DAMAGE_CATEGORY_PHYSICAL;
}
#endif
