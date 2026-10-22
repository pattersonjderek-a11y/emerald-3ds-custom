# Stage C visual regression follow-up

Work is on `fix/stage-c-visuals`, based on `aa0a291` / implementation `66fc31d`.
Stage D is paused until these regressions are retested. No randomizer/difficulty
rule, save-layout, engine pin or SDK upgrade is part of this fix.
Prior complete C engineering results are preserved in [STAGE_C_STATUS.md](STAGE_C_STATUS.md).

## Actual device report

Derek reports Stage C is tested and working in general, with three visual
failures on an **original 3DS XL**: black map boundaries in voxel mode; a
flickering/invisible follower that sometimes resembles a golden Poochyena
instead of Torchic in Littleroot; stock-background wild battles on the early
routes despite scenic battles being enabled. This is a user-reported baseline
smoke result, not complete randomizer/campaign acceptance. The exact 2D follower
behavior, performance and full save/boss/double checklist remain unreported.
No emulator was exercised by Codex. Fix-build hardware results are PENDING.

## Diagnosed and implemented

- Hoenn border dimensions are implicitly 2x2; expansion layout bytes are zero
  unless the layout is FRLG. The camera adapter treated zeros as no border,
  compared zero bytes when deciding shared phase, and skipped its tile checks.
  Use effective dimensions for sampling, drawable checks and phase sharing,
  retaining native negative-coordinate phase and explicit FRLG dimensions.
  The canonical voxel atlas now visits every entry of rectangular FRLG borders.
- Torchic's real six-frame SMOL sheet and normal/shiny palettes are present.
  Native `IsCompressedData` read the linked zero-filled INCGFX stub instead of
  its actual header, taking the raw single-frame path. Resolve it before
  detecting compression. The actual OBJ sheet loader now clears the reserved
  transparent frame so reused tiles cannot flash a previous Pokémon under
  Torchic's palette. Add null/allocation-failure handling to the template loader.
  No follower art was imported or substituted; full later-generation/follower
  coverage remains Stage E.
- Scenic battle preparation must keep building the map view while the normal
  compositor temporarily draws the fallback. Previously the post-submit build
  slices required an already drawable battle, so a pending view could never
  progress. Schedule work when preparation ran, independently of draw success;
  preserve native intro, move-background and forced-blank fallbacks. Existing
  map-based scene/camera selection remains in use, without a renderer rewrite.

## Evidence and preservation

New ASan/UBSan fixtures execute production camera/voxel-border functions,
compression detection/template/sheet allocation and blank-frame writes, plus
scenic preparation and post-submit dispatch. All three pass on corrected
sources. Each corresponding preserved C test fails at a runtime assertion
before the fix (logs `work/visual-{border,follower,battle}-before.log`). These
are controlled host memory/GPU boundaries, not console rendering tests.
`make verify` now includes `verify-expansion-visuals` for expansion builds.

Engine changes are captured in the canonical expansion patch; platform/voxel
changes and tests remain in canonical root files.

Actual commands/results in the unchanged frozen SDK, container
`emerald-visual-fixes` (UID/GID 1000):

- `tools/stage_c_visuals.sh build`: PASS; actual native ARM11 compilation and
  3DSX output, starting from a separate copy of C's cached generated build tree.
- `tools/stage_c_visuals.sh test`: PASS; full `make verify`, 9 expansion adapters,
  95 builder tests (2 existing skips), strict source publication audit.
  Native audit: 51 required symbols, ARM11 hard-float, no strong undefined
  symbols, all 17,536 assets and 1,451 pointer rows verified. The make gate
  includes the new visual fixtures and existing production run/randomizer/
  save/recovery, graphics/voxel/clock/storage regressions.
- Fresh pinned-source worktree + documented bootstrap: PASS. All 277 engine
  patch files and 305 canonical overlay/lock files match, reverse apply passes,
  and visual/run/randomizer production host fixtures pass there. This is
  fresh source/host reproduction, not a second full native compilation.
- The **entire** audited linked randomizer pool equals C's baseline JSON:
  same 1,072 entries, generation/legend flags, BSTs, usable levels and graphics
  paths. No option/algorithm/content-rules change or intended seed reroll.
- Python byte compilation and shell syntax checks pass. All recorded A/B/C
  artifact sizes/hashes were rechecked and remain unchanged.

Private logs: `work/visual-native-build.log`, `work/visual-test-workflow.log`,
`work/visual-regressions.log`, `work/visual-fresh-bootstrap.log`,
`work/visual-fresh-tests.log`, and the three `work/visual-*-before.log` failures.
Final private package audit/hash metadata follows the packaging gate.

Use `tools/stage_c_visuals.sh build|test|package`; it uses the frozen SDK and
separate `build/stage-c-visuals` tree. Original C wrapper refuses the fix patch.
Baseline C tree/ZIP and its Dropbox file remain unchanged. A separate copy of
that ZIP/manifest is preserved in `work/baseline-stage-c-aa0a291/`.

The upgrade intentionally retains `/3ds/emerald3ds-custom-stage-c/`, schema 1,
52-byte record, algorithm 1 and rules `00020001`. Existing C saves/settings
stay in that same directory; back it up, then replace only the matching app
and metadata. No automatic migration, new settings or reroll is introduced.
Matching engine/data hashes, pool equality and baseline preservation are checked
before packaging. A/B/original namespaces remain protected.

## Retest / next task

Retest Littleroot borders, Torchic in both 2D/voxel, hide/show and map/menu/battle
returns, and scenic wild battles at different early-route locations on the
original XL. Keep the unmodified C package for rollback. Detailed instructions:
[DEVICE_TESTS.md](DEVICE_TESTS.md). Do not label these visuals fixed on hardware
until Derek supplies results. After these fixes pass console acceptance,
Stage D can add independent difficulty rules.
