# Emerald 3DS Custom device tests

Stage A package implementation: `c73ea2a28e7050be1f31dfd63fa478fe4cc9e5ae`;
manifest and artifact hashes: `BUILD_OUTPUTS.json`. Native builds and host
checks passed; the private ZIP is ready for this checklist.

All physical-console results for this Stage A build are **PENDING**.
No emulator was run. Successful source inspection, host tests and native
compilation do not establish boot, frame rate, campaign stability or complete
Gen 1–9 art. Do not reuse historical upstream hardware results as new results.

## Laptop and SD card

1. Back up the SD card to your laptop. Record whether the console is an
   **original Nintendo 3DS XL** or **New Nintendo 3DS XL**; this does not block
   compiling the shared build. Use Homebrew Launcher on your already modded console.
2. Extract the private Stage A ZIP onto the SD root. The ZIP places only
   `3ds/emerald3ds-custom/Emerald3DS.3dsx`, its `.smdh`, and `debug.txt`.
   Keep your original `3ds/emerald3ds` and `3ds/pokeemerald` folders intact.
   Use the application's launcher title **Emerald 3DS Custom**.
3. Use a fresh custom directory for this first run. Do not copy an old save,
   settings file, clock, `devdata/` or pack into it. The development application
   embeds matching data and needs no separate pack. If updating a previous
   custom test, first back up that entire directory, then remove its loose-data
   marker so it cannot override embedded data.
4. For sound, the port requires your console's existing
   `SD:/3ds/dspfirm.cdc` (see `INSTALLATION.md`, Sound). No firmware is bundled
   or downloaded by this workflow. This shared firmware is read by libctru;
   it is not a mutable game-state path.
5. Eject the SD card safely, launch through Homebrew Launcher, start a **new**
   game, and follow the checklist below. Copy logs back after a failure before
   another launch rotates them. Disable routine logging by deleting only
   `3ds/emerald3ds-custom/debug.txt` after diagnosis.

Rollback: remove only the custom folder after backing it up. The legacy
application and saves must remain unchanged. Do not install the inherited CIA
forwarder: its title ID has not been assigned/tested for a side-by-side custom
installation. No CIA is included in the private package.

## Isolation audit

Canonical `3ds_port/include/3ds_paths.h` selects
`sdmc:/3ds/emerald3ds-custom/`. Production save and filesystem tests create
sentinels for both legacy installations, initialize and write a new custom
save, reload it, write custom settings, reject traversal/absolute paths, and
compare every sentinel afterward. `make verify` also exercises real settings
shutdown and clock storage/recovery.

| Runtime data | Custom location / behavior |
| --- | --- |
| Save | `emerald3ds.sav` within custom directory; rotating game slots stay inside this file |
| Save migration | Removed: never reads, moves or renames `/3ds/pokeemerald/pokeemerald.sav` |
| Settings | `settings.txt` and `settings.txt.tmp` within custom directory |
| Clock | `emerald3ds.clock`, `.clock.tmp`, `.clock.bak`, bound to this save |
| Logs | `debug.txt`, `port.log`, `port-prev.log`, `perf.bin`, `perf-prev.bin` within custom directory |
| External game data | `emerald3ds.pak`, `devdata/`, `.emerald3ds-dev` marker within custom directory |
| Diagnostics | `scenario.txt`, `scenarios/`, `measure.txt`, `slider.txt`, `ext_test.txt`, `audio.raw`, `frames.raw` within custom directory |
| Executable assets | Own read-only RomFS: shader, engine metadata, embedded content |
| Install/upload tools | Builder installer and `tools/dev_assets.py` default to custom directory |

Source scanning and sentinel host tests are evidence of isolation, not a
console test of FAT behavior or power loss. After testing, compare hashes of
your original installation with the backup too.

## Minimum smoke checklist

For each run record model, source revision and source-diff hash, application
and data hashes from the package manifest, settings, result, log paths and
observed performance. Record original/New XL and system/Homebrew Launcher
versions. Do not enable new features to work around an unexplained failure.

| Check | Result | Notes / log |
| --- | --- | --- |
| Boot; New Game; introduction; three starter choices; first battle | PENDING | |
| Walking, map transition, doors, stairs, interiors | PENDING | |
| 2D/voxel switch; camera; blur; colors; lighting; particles | PENDING | |
| Sound/music and distinct species cries | PENDING | |
| Follower on/off; map/door transitions; party reorder; battle return in 2D and voxel | PENDING | |
| Later-generation test Pokémon: capture, summary/moves, deposit/withdraw, evolution | PENDING | Developer grants must be labeled; current catch locations are not an all-species claim |
| Save; close/restart; Continue preserves player, party, progress and settings | PENDING | |
| Settings/clock round trip; old installation hashes unchanged | PENDING | |
| Single trainer; rival; double/partner; Gym Leader; Elite Four representative | PENDING | Requires progression or a separately authorized private test setup |
| Existing Mega behavior: eligibility, START selection, transformation, restored form | PENDING | |
| Mossdeep partner battle: all four send-outs, health bars, subsequent turns | PENDING | Existing upstream regression |
| Pokédex then capture; summary move details; berry tags/Blender | PENDING | Existing upstream regressions |
| Busy town/route/interior and battle frame pacing/memory | PENDING | Record settings/model; no promised FPS |

New randomizer seeds and difficulty choices do not exist in Stage A. The
blueprint's seed-change/new-run check becomes applicable in Stage B/C.
Do not erase your first run to test New Game: back up its complete custom
folder first. No full campaign or postgame acceptance has been performed.
