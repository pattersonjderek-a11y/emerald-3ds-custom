# Emerald 3DS v0.5.0 refresh and Stage E recovery

Source inspection: 13 November 2026 (America/Los_Angeles).

## Current result and blocker

Derek requested the latest original Emerald 3DS integration before completing
interrupted Stage E. This is an authorized change of order from the original
frozen-baseline task. **No upstream integration or new native build is claimed.**

The managed workspace failed provisioning/executor configuration. Terminal
requests repeatedly returned: `No usable execution environment is available.
Wait for an environment to become available before using this tool.`
Provider status reported running/connected, but no execution capability was
usable. This is not evidence of a compiler or project-source failure.

GitHub remains accessible. This documentation-only checkpoint is based on the
last remote custom checkpoint, `b2e811658ff7fd7dcfdf15e3b9612d22ffb7c7a7`, on
`project/stage-d`. The remote branch list contained A/B/C/D and visual fixes,
but no `project/stage-e`. Local Stage E source, logs and outputs cannot be
inspected, backed up, committed, merged or rebuilt from this failed runtime.

Restore/reconnect this chat's **existing** cloud environment. Inspect the
existing checkout and its uncommitted changes before any checkout, reset,
bootstrap or source import. If a replacement machine is required, recover the
old workspace first where possible: remote Stage D does not contain the local
Stage E implementation. Do not assume its absence remotely proves local loss.

## Exact upstream target inspected

| Component | Resolved revision |
| --- | --- |
| Original Emerald 3DS latest release | [v0.5.0](https://github.com/ZallaxDev/emerald-3ds/releases/tag/v0.5.0), published 30 October 2026 |
| Release tag object | `1561e874dc5ef7922b5e2758c73a282f31e8ae89` |
| Release commit and current main | `bcae4b70dac61419fc933084084469f6cfbe344b` |
| Blueprint original-port reference | `b198c08defb94081ae995796cf75ab8cdb51f2d0` |
| Expansion integration current main | `8ebb7355742ce43bbb10528044f9a175fc990a64`, unchanged from the candidate already used |

The original-port revision is 291 commits ahead of the blueprint reference.
The GitHub compare response caps the returned file list at 300 and returned
250 commit objects. The accompanying [machine-readable inventory](UPSTREAM_REFRESH.json)
uses complete, non-truncated recursive Git trees instead.

There are **757 changed paths**: 584 added and 173 modified, no removals.
Relative to saved custom Stage D, 122 retain the reference blob and 50 differ
from both reference and latest upstream. The 584 additions are absent from
saved Stage D. One existing upstream document, `docs/VOXEL_STATUS.md`, is
absent in custom. Blob differences identify review scope, not proven merge
conflicts, and this is not a three-way merge against the custom fork's proven
common ancestor. Local Stage E will add further differences.

## Integration findings from inspected source

- Upstream's release describes expanded voxel interiors/terrain, weather,
  camera and map-edge fixes, redesigned bottom-screen menus, battle-speed
  controls and other rendering/performance changes. Those are upstream
  claims, not acceptance results for our expansion build.
- `3ds_port/docs/seeded_randomizer.md` and
  `3ds_port/include/3ds_randomizer.h` explicitly define a **386-species**,
  globally configurable `settings.txt` permutation and a 31-bit seed.
  That conflicts with this project's immutable save-bound Gen 1–9 rules,
  independent streams and existing run codec. Preserve the custom randomizer
  as the expansion authority; adapt new UI controls to it or remove unavailable
  duplicate controls. Do not run both resolvers or expose a misleading toggle.
- Upstream `3ds_port/full.mk` directly compiles its randomizer and Nuzlocke
  modules. Its `3ds_port/Makefile` adds their verification targets. Reconcile
  these with expansion guards and custom production tests, rather than
  overwriting the custom Makefiles.
- The source changes include `3ds_bottom_ui.c`, `3ds_extras.c`,
  `3ds_game_bridge.c`, `3ds_game_full.c`, `3ds_compat.c`,
  `3ds_settings.c`, `3ds_data.c`, `ctr_voxel.c`,
  `voxel_world.c` and `voxel_battle.c`, each also changed in custom.
  Preserve custom Run Settings access, expansion API adapters, previous
  border/follower/scenic fixes, and the canonical namespace service.
- The latest upstream tree has no `3ds_port/include/3ds_paths.h`.
  Saved Stage D defines its expansion root there as
  `/3ds/emerald3ds-custom-stage-d/`. Retain E's isolated namespace when
  recovered, and route every new save/settings/clock/log/tracker/data path
  through it. Existing upstream `/3ds/emerald3ds/` defaults cannot simply
  replace the custom service.
- The latest upstream `upstream.lock` still pins original pokeemerald to
  `76463dac15cad36aca5e2b3f6366abf9e53f814f`, but contains no expansion
  section. Do not replace the custom lock or silently upgrade its expansion
  pin `dfb0f84374230f4d462191601179b742f9f077df`.
- That lock pins release voxel generation to Python **3.13**
  (`python:3.13.17-slim-bookworm`, Pillow **12.3.0**), and the same
  devkitARM image digest recorded in our baseline. The custom SDK currently
  documents Python 3.11.2/Pillow 9.4.0. Reproduce any newly required generator
  environment separately and record it; do not silently change the baseline SDK.
- Pack schema remains 1 in `3ds_pak.h`, but schema equality does not prove
  engine/data compatibility. Upstream v0.5.0 release notes require rebuilt
  data and explicitly say an executable-only quick update is insufficient.
  Rebuild and audit custom expansion assets and their matching ABI; do not
  use the stock website or stock pack for this build.
- Since v0.5.0, original upstream port contributions are **CC BY-NC-SA 4.0**,
  as specified in its `LICENSE-PORT.md` and `NOTICE.md`. Older published MIT
  copies and separately licensed third-party components retain their notices.
  Preserve attribution and applicable licence texts when importing new code.
  No v0.5.0 source or artwork is imported by this documentation checkpoint.

The inventory lists exact path/blob identities and all 50 overlapping changed
paths. It includes neither ROM bytes nor generated game data.

## Interrupted Stage E handoff: historical, not reverified here

The preceding work record reports a local `project/stage-e` branch based on
Stage D, with a separate `build/stage-e` tree and canonical expansion patch.
It reports optional per-species/slot abilities, location-keyed field/hidden
items, held-item rules, menu/codec updates, conservative protection policies,
follower bounds/palette/context fixes, and production regression/audit tools.
No Stage E commit, pushed source checkpoint or final private package had been
completed when work stopped.

Expected recovery locations, whose current existence is **unverified**:

- Canonical engine changes: `patches/pokeemerald-expansion/0001-port.patch`
  (reported 287 engine paths, including `include/custom_optional.h` and
  `src/custom_optional.c`); canonical root platform/tests/tools edits.
- Build wrapper: `tools/stage_e.sh`; intended runtime root
  `/3ds/emerald3ds-custom-stage-e/`.
- Native app/symbols: `build/stage-e/3ds_port/emerald3ds.3dsx`,
  `emerald3ds.elf`, `build/gamedata_image.elf`.
- Last pending command logs:
  `work/stage-e-release-ready-build.log` and
  `work/stage-e-content-final.log`.
- Earlier check logs: `work/stage-e-test-final.log`,
  `work/stage-e-verify-final.log`,
  `work/stage-e-fresh-final.log`,
  `work/stage-e-fresh-tests-final.log`.
- Fresh source scratch tree: `work/stage-e-clean`. Refresh its reproduction
  proof after the last protected-item output-pool change.
- Coverage output:
  `build/stage-e/3ds_port/build/content-audit.json`,
  `content-summary.json`, `content-coverage.csv`.
  The interrupted report noted 1,025 National Dex entries, 1,072 eligible
  species/forms including 124 Gen 9 entries, 62 eligible shared follower
  mappings and incomplete mappings outside the eligible pool. These are
  historical audit findings, not evidence of exact art or current refreshed
  build completeness. Re-run after upstream asset changes.
- Frozen SDK container: `emerald-visual-fixes`, image
  `emerald-stage-a-sdk`, repository mounted at `/project`.

The earlier work record reports passing native compilation and host checks,
but the latest small production/audit edits still needed final confirmation.
Do not promote those historical results into a tested v0.5.0 integration.
First preserve recovered E source in Git, regenerate/reverse-check the patch,
and preserve baseline packages before importing upstream source. Continue
Stage E verification and documentation after the upstream refresh, as requested.

Stage E's remaining finish work includes full host/native checks, fresh
bootstrap reproduction, coverage metadata publication, updated STATUS/BUILD/
SAVE_FORMAT/RULES/SOURCES/DEVICE_TESTS records, private matching package and
manifest, baseline hash verification, source audit, commits and source sync.
Stage F is subsequent campaign/packaging work, not acceptance of incomplete E.

## Evidence for this resume

**Source inspected:** blueprint, root AGENTS (the custom recursive tree has
no nested AGENTS files), current saved Stage D status/build/development/feature
documentation and CI, exact refs, complete blob inventories, and upstream
randomizer/build/storage/lock/licence sources.

**Metadata checks:** inventory path uniqueness, counts, category totals and
SHA-1 syntax checked in orchestration JavaScript. This is not a project host test.

**Host tests / native compilation:** not run this resume because execution
is unavailable. **Emulator:** not exercised. **Physical console:** pending;
Derek's “looks good” supplies no new device measurements or test results.

No new compiled output or SD package exists from this resume. Historical
Stage D paths/checksums remain in `STAGE_D_BUILD_OUTPUTS.json`; A/B/C and
visual-fix package records remain intact. No ROM, save, firmware, generated
pack or content-bearing build artifact is committed by this checkpoint.
