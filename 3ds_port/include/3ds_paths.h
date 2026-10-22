#ifndef CTR_PATHS_H
#define CTR_PATHS_H

/* All mutable state and external data are private to this project.
 * Never migrate another installation's save into this namespace. */
#ifdef PORT_EXPANSION
#define CTR_SD_DIR "/3ds/emerald3ds-custom-stage-c/"
#else
#define CTR_SD_DIR "/3ds/emerald3ds-custom/"
#endif
#define CTR_DATA_DIR "sdmc:" CTR_SD_DIR

#endif
