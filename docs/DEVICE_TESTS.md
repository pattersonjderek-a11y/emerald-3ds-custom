# Emerald 3DS Custom device tests

Stage A package implementation: `c73ea2a28e7050be1f31dfd63fa478fe4cc9e5ae`;
manifest and artifact hashes: `BUILD_OUTPUTS.json`. Native builds and host
checks passed; the private ZIP is ready for this checklist.

All physical-console results for this Stage A build are **PENDING**.
No emulator was run. Successful source inspection, host tests and native
compilation do not establish boot, frame rate, campaign stability or complete
Gen 1–9 art. Do not reuse historical upstream hardware results as new results.

## Stage B: separate console test (all results PENDING)

The baseline Stage A ZIP is unchanged and separately preserved; test it using
the original checklist below. Stage B is a different app and runtime namespace.
No emulator, physical-console, restart or campaign result is claimed for Stage B.
Stage B implementation is `62d7edce10e4fc35e00b8c629e899bd9bb143390`;
package/native artifact hashes are in `STAGE_B_BUILD_OUTPUTS.json`.
Private ZIP SHA-256: `9e52bde5bece05774707e9ac075b4a7e79c8084de2dec6f9de6435d1d7b3efb3`.

1. Back up the SD card on your laptop, including existing Emerald installations
   and Stage A. Record original 3DS XL versus New 3DS XL and launcher version.
2. Extract **Emerald3DS-Custom-StageB-private.zip** onto the SD root. Its app is
   `3ds/emerald3ds-custom-stage-b/Emerald3DS.3dsx` with matching `.smdh` and an
   empty debug marker. Launch **Emerald 3DS Custom Stage B** through Homebrew
   Launcher. Leave Stage A's `3ds/emerald3ds-custom` and the original app folders
   intact. Use a fresh Stage B directory; copy no saves, settings, clocks,
   packs or loose-data markers from another installation.
3. The embedded app includes its matching generated data. Do not install a
   stock pack, use the generic builder installer, or use a CIA forwarder.
   Existing sound setup remains the same read-only shared DSP file described
   below; no firmware is included.
4. Choose New Game. Randomized and Hard must say UNAVAILABLE and refuse A.
   Custom is a locked preview; all rule changes remain unavailable. Confirm
   Standard/Normal. Try automatic seed regeneration and manual seeds 0 and
   4294967295; 4294967296 must be rejected. B discards an unaccepted digit edit.
5. Read the summary; confirm the chosen seed, fixed mode and Normal difficulty.
   Finish the normal introduction/name selection. Press START in the normal field to open RUN SETTINGS;
   confirm the same seed, fixed mode, rules ID and algorithm 0. B must restore
   the field/menu cleanly, with working graphics, controls and sound.
6. Save, exit cleanly, relaunch, Continue and read RUN SETTINGS again: seed/run
   ID/rules must be identical. Confirm player, party, location and progress.
   Open graphical/QoL settings, change display preferences and reopen RUN
   SETTINGS: its rules must stay unchanged.
7. With that existing save backed up, choose New Game, edit choices and B back
   to the mode page, then B cancel. Continue must still show the previous run
   and progress. On the laptop, compare the save against its pre-cancel copy.
   Opening setup/Run Settings must not change stored bytes. Clock/log files may
   legitimately advance independently, so compare the save specifically.
8. Back up the entire Stage B directory before replacing a run. A confirmed
   second New Game changes the in-RAM run only after initialization; without
   explicitly saving, restarting should still Continue the previous on-card
   run. After intentionally saving the second run, its new seed/run ID must
   survive restart. Keep the first backup outside the SD runtime directory.
9. Test the baseline rendering/follower/dual-screen/battle checks below in
   Stage B too. With optional DexNav enabled and every normal pause-menu item
   unlocked, RUN SETTINGS occupies the ninth row; B/START closes the menu
   (the explicit EXIT row is omitted in that full-menu case).
10. Copy `port.log`/`port-prev.log` and the Stage B package manifest to the
    laptop after a failure before relaunching rotates logs. Record exact menu
    actions and displayed error. Do not upload saves/logs publicly. Delete
    only Stage B's debug marker when routine logging is no longer needed.

| Stage B check | Result |
| --- | --- |
| Launcher/boot, readable setup, disabled choices | PENDING |
| Manual/automatic seed, overflow and summary | PENDING |
| Intro, name, first field, read-only page and return | PENDING |
| Save/restart/Continue preserves identity/options/progress | PENDING |
| Cancel leaves existing on-card save intact | PENDING |
| Confirmed new game without saving preserves old disk save | PENDING |
| New run after intentional save resets identity | PENDING |
| Display options do not modify run settings | PENDING |
| Original, Stage A and Stage B directories remain isolated | PENDING |
| Full normal pause menu, DexNav and B/START exit | PENDING |
| Existing graphics, voxel effects, followers and dual screens | PENDING |
| Corrupt/unsupported recovery UI on disposable synthetic test save | PENDING; developer-assisted only |
| Physical SD/FAT interruption recovery | PENDING; not part of this smoke test |

Stage B isolation was exercised with the production save/filesystem code on the
host: sentinels for `/3ds/emerald3ds`, `/3ds/pokeemerald` and Stage A remained
unchanged. The same central path macro controls saves, settings, clocks, logs,
external data and diagnostic paths. This is distinct from a real SD/FAT test.
If a run error appears, back up the full Stage B folder, restore a matching
complete save/clock backup or use its matching build; do not delete/zero the
run record to bypass rejection. See SAVE_FORMAT.md. Rollback removes only
Stage B's directory after backup; Stage A and the original installations stay.

## Stage A laptop and SD card

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

The frozen Stage A version of `3ds_port/include/3ds_paths.h` selects
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
