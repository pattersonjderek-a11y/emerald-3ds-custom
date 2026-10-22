# Emerald 3DS Custom device tests

Current follow-up: **Stage C VisualFixes**. Follow the first checklist below
to update the existing C app after backup; baseline A/B/C instructions are
preserved afterward for their original packages.

Historical Stage A package implementation: `c73ea2a28e7050be1f31dfd63fa478fe4cc9e5ae`;
manifest and artifact hashes: `BUILD_OUTPUTS.json`. Native builds and host
checks passed; the private ZIP is ready for this checklist.

All physical-console results for this Stage A build are **PENDING**.
No emulator was run. Successful source inspection, host tests and native
compilation do not establish boot, frame rate, campaign stability or complete
Gen 1–9 art. Do not reuse historical upstream hardware results as new results.

## Visual fixes after Stage C (retest PENDING)

Baseline report from Derek: original 3DS XL, Stage C generally tested/working;
Torchic follower in Littleroot flickers/is invisible and sometimes appears as
an incorrectly colored Poochyena; voxel borders black; early-route wild battles
use stock scenery despite scenic ON. Do not convert this report into a full
save/reload, boss, double-battle, frame-rate or campaign pass. The table below
records these actual visual failures; all fix-build results remain PENDING.

This is a compatible C visual upgrade, with a separate package named
`Emerald3DS-Custom-StageC-VisualFixes-private.zip` (implementation `4562a90`).
ZIP SHA-256: `a4e936f23d49b63029c5b85dd721170f3fcbc2096fe006e817ea186976265e17`.
Exact artifact metadata: STAGE_C_VISUAL_FIXES_OUTPUTS.json. It keeps C's existing runtime
and save directory so the current run can continue. Keep the original C ZIP
and a complete backup of the existing C directory for rollback.

1. On the laptop, back up the whole `3ds/emerald3ds-custom-stage-c` directory.
   Extract the VisualFixes ZIP, then copy its `Emerald3DS.3dsx` and matching
   `.smdh` into that existing C directory. Keep saves, settings, clocks and logs.
   Do not delete/recreate the directory or start a new game merely to apply
   this fix. Keep A/B/original installations unchanged. Use the embedded app;
   do not retain another build's loose-data marker or external data pack.
2. Launch C and Continue. Confirm existing player/location/party and START Run
   Settings (seed/options/rules) are unchanged. Keep VOXEL ON for boundary and
   scenic tests; enable the voxel-battle/scenic option too. The separate
   BATTLE SCENE option controls move animations, not map scenery. Confirm the
   scenic option stays ON after a restart. Original XL uses existing performance
   defaults; no forced stereoscopic setting is needed.
3. In Littleroot, walk to each outer edge in voxel view and turn the camera as
   available. Expect the repeating native trees/ground beyond the map, including
   corners. Cross to Route 101 and back: no black strips, phase jumps or trees
   replacing a connected map. Compare with 2D's boundary pattern.
4. Put Torchic first and enable FOLLOWER. Test male/female and shiny only if
   already available; do not change an existing Pokémon just for this test.
   Check idle/walking/turning in 2D and voxel modes, follower OFF/ON, entering/
   exiting a house, map connection, bag/menu return, battle return and save/
   restart. Expect the Torchic sprite and correct color, without Poochyena
   flashes or intermittent disappearance. Native restrictions while hidden,
   surfing/biking or other scripted states still apply. Later species with
   missing native artwork may retain documented fallbacks; report the species.
5. Trigger several ordinary wild encounters on early routes, at visibly different
   places (grass near a tree, open grass, beside a building if possible). Expect
   scenery from that map/location, not a permanent stock battle backdrop.
   A short loading fallback may appear while a new view is built; it must
   progress. Test after boot/Continue, an options/menu return, map connection,
   and a second battle. Moves that temporarily replace the background must
   return to map scenery. End the battle and verify the field/follower returns.
6. If practical, test an early trainer battle and later a double/partner battle,
   plus a different town/indoor map. Record unsupported contexts separately.
   Watch frame pacing on the original XL; host tests do not measure it.
7. After a failure, exit and copy `port.log`, `port-prev.log`, crash dumps if any,
   the manifest, seed/options and exact steps privately before relaunch rotates
   logs. Rollback restores the original C app/metadata and its matching backup;
   never use another stage's save as a workaround.

| Check | Baseline user result | VisualFixes result |
| --- | --- | --- |
| Boot/basic play | Reported working | PENDING |
| Original XL hardware model | Confirmed | Same console requested |
| Littleroot/route voxel boundaries | FAIL: black edges | PENDING |
| Torchic follower identity/color/visibility | FAIL: flicker/invisible/wrong appearance | PENDING in both 2D and voxel |
| Early-route scenic wild battles | FAIL: stock background | PENDING |
| Scenic setting persists across restart | Unreported | PENDING |
| Existing C save/rules retained by update | Not yet upgraded | PENDING |
| Map/menu/battle returns, trainer/double, performance | Unreported | PENDING |

## Stage C: core randomizer console test (all results PENDING)

Use the separate Stage C package, not the unchanged Stage B Dropbox ZIP.
Implementation: `66fc31d`; exact package/native hashes: STAGE_C_BUILD_OUTPUTS.json.
Stage C ZIP: 20,511,090 bytes, SHA-256
`cbc9963e5ade1110a4486840cfdcfae2c62a4ae224d176666de75304afbdd60a`.
No console or emulator result has been supplied. Keep A/B available as controls;
C has its own runtime directory. Record source/hash/model and each result.

1. Back up the SD on the laptop. Extract `Emerald3DS-Custom-StageC-private.zip`
   to the **SD root**. Confirm the app is
   `3ds/emerald3ds-custom-stage-c/Emerald3DS.3dsx` with matching `.smdh`.
   Leave original/A/B folders untouched. Start with no save/settings/clock/pack
   copied from another build. Launch **Emerald 3DS Custom Stage C** in Homebrew
   Launcher; no CIA or separate pack is needed. Shared DSP setup is below.
2. New Game → Randomized → Normal → manual seed **42**. Digits: left/right
   select position, up/down change it, A accepts. Customization: starters/wild/
   trainers ON; in eligible generations turn Gen 1–8 OFF, leave Gen 9 ON;
   both balance restrictions OFF. Abilities/items and Hard/Custom must stay locked.
   Read the confirmation summary before beginning the normal introduction.
3. At the bag, record all three displayed names/sprites/cries. Compare against
   the linked-pool seed preview documented below. Choose one, inspect received
   species/summary/moves and complete the intro battle. It must have a usable
   attack. The scripted intro opponent is protected, so it need not be Gen 9.
4. Press START in the field: read-only Run Settings must show seed 42,
   Randomized/Normal, three core toggles ON, only Gen 9, rules `00020001`, ALG 1.
   B returns cleanly. Save, exit, relaunch and Continue: all settings, party and
   progress must stay identical. Repeated reset must not reroll the starter roster.
5. On an ordinary route, verify randomized Gen 9 wild species and legal moves.
   With visible encounters ON, note the overworld species/shiny appearance and
   touch it: battle/summary must agree. Test land and later water, rods, rocks,
   hidden tables/DexNav as unlocked. Capture one, inspect summary/moves, store/
   withdraw and save/reload. Follower fallback artwork is a separate known limit.
6. Test Route 103 rival and later rematches: the starter family should remain
   coherent with the corresponding offered starter. At later levels ordinary
   eligible level evolution may advance it; item/trade evolution is not forced.
   Test ordinary trainers, first Gym, a later Gym, Elite Four and Champion when
   available. Levels/size remain native; replacement moves must suit species.
   Record doubles, scripted partner and an inherited Mega battle separately.
7. Back up the whole C directory before another run. New Game/setup then B
   cancel must preserve the existing save. A confirmed new run without saving
   must also leave that on-card save available after restart. After intentionally
   saving a new seed, Continue must retain that new run. Repeat seed 42/options
   to compare identical choices; another seed should change the roster. Do not
   expect every random encounter or battle action to repeat.
8. In a separate backed-up test run, Standard/Normal must show ordinary Hoenn
   starters/fixed tables and ALG 0. Compare existing visual/QoL/follower behavior
   against B. Also try starters-only and trainers-only customization. Difficulty
   and optional ability/item randomization are not implemented in C.
9. After failure copy C's `port.log`, `port-prev.log`, any `crash_dump_*.dmp`,
   manifest and exact actions to the laptop before relaunch rotates logs. Keep
   saves/logs private. Do not delete the run record to bypass a recovery error.

The pool audit verifies Gen 9 data and indexed front/back/icon/palette assets,
including Sprigatito, Fuecoco, Quaxly, Ogerpon, Terapagos and Pecharunt. This is
**linked-data evidence**, not a console screenshot or complete follower audit.
The seed preview executes the real C resolver with this exact linked pool.
For **42 / Gen 9 only / both balance flags OFF**, slots 1–3 are **Toedscruel,
Tatsugiri (Curly), Meowscarada** (internal 1337 / 1367 / 1291). Seed 43 instead
predicts Pawmot / Iron Moth / Wo-Chien. These are host predictions for comparison;
a console mismatch is a test failure to report, not proof the console was tested. Eligibility does not
mean every species appears in every seed, or that every form/follower is complete.

| Stage C check | Result |
| --- | --- |
| Boot/setup/summary/read-only settings and UI return | PENDING |
| Predicted Gen 9 starter names/sprites/gift/moves/first battle | PENDING |
| Save/restart/Continue preserves seed, rules and progress | PENDING |
| Same seed/options repeat; changed seed varies | PENDING |
| Visible wild identity/shiny state matches battle | PENDING |
| Land/water/rods/rocks/hidden/DexNav mapping | PENDING |
| Rival family and rematch evolution continuity | PENDING |
| Ordinary trainer/Gym/Elite Four/Champion | PENDING |
| Double/partner/tutorial/protected facilities/Mega | PENDING |
| Standard control; individual core switches | PENDING |
| Cancel/new run and original/A/B/C storage isolation | PENDING |
| Renderer/effects/dual screens/followers and frame pacing | PENDING |

Host storage sentinels protect original/A/B paths; hardware SD/FAT behavior is
still pending. Rollback backs up and removes only C's directory. Never replace
the B package with C under the B name or import a B save automatically.

### Optional Stage B Gen 9 demonstration

For the preserved **development** B build on a disposable/backed-up save:
hold **R + START** in the field → **Give X… → Pokémon (Basic)**, select
Sprigatito (internal ID 1289), then inspect its summary and use it in battle.
Fuecoco is 1292, Quaxly 1295, Ogerpon 1416, Terapagos 1431, Pecharunt 1434.
These are internal species IDs, not National Dex numbers. This is a clearly
marked developer grant, not evidence of ordinary fixed-campaign encounter
placement. B's normal starter choices remain Treecko/Torchic/Mudkip.

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
