# Stage E + Emerald 3DS v0.5.0 — engineering implemented; device testing pending

Branch: `project/stage-e-v050` in `/workspace/emerald-3ds-stage-e`.
The original `/workspace/emerald-3ds-custom` work checkout is unchanged.
Graphics history is merged at v0.5.0 `bcae4b70dac61419fc933084084469f6cfbe344b`;
expansion stays at `dfb0f84374230f4d462191601179b742f9f077df`.
Derek explicitly makes v0.5.0 authoritative over overlapping current/future
features. Prior Stage D source/history remains preserved. Historical D evidence
is in STAGE_D_STATUS.md; its private package was absent locally and was not
re-downloaded or hash-verified in this session.

## Blueprint progress

A–D source is carried forward: native build workflow, transactional difficulty
record/new-game setup, core species hooks, caps/AI/item policies and prepared
bosses. Conflicting B/C immutable species settings/generation/BST filters are
superseded by the v0.5.0 global editable randomizer and upstream UI. Difficulty
remains save-bound. The original-XL reports confirmed earlier C general play,
then visual defects; they do not establish D/E hardware acceptance.

E now implements three independent OFF-by-default switches in OPTIONS → MODES
→ OPTIONAL RULES: abilities, ordinary field/hidden items, occupied wild/enemy
held-item slots. Form/signature/progression dependencies are protected. Ability
reads share the native resolver, with battle-entry snapshots; owned abilities
can change after global seed edits outside battle. Global settings semantics,
including their limits, are explicit in SAVE_FORMAT.md and RULES.md.

The v0.5.0 renderer, menus, tracker and global species permutation are retained
with native expansion APIs/compression. The permutation includes all 1,025
National Dex bases, including 120 Gen 9 species. Native encounter methods/times
and previews agree, including timed projections and phase-cache invalidation.
The upstream physical/special split switch now controls actual native categories.
Follower bounds/palette/allocation/slot-pressure protections and native border
adapters are included. Raw/short palette support fixes native UI/Dex/bag decoding.

## Actual evidence

- **Native compilation:** full ARM11 hard-float `.3dsx` produced. Current outputs
  are `build/stage-e/3ds_port/emerald3ds.3dsx`, `emerald3ds.elf` and
  `build/gamedata_image.elf` beneath that port directory. Native commands:
  `make -C build/stage-e/3ds_port -j6 PYTHON=python3`, then `make ... verify`.
  `work/native-build-36.log`, `work/verify-e-3.log` and subsequent final gates
  distinguish compilation from host checks. No strong undefined symbols.
- **Host/data checks:** production save/CRC/two-slot recovery, cancellation,
  new-save initialization, global core/starter resolution, all encounter tables,
  optional rules, follower policy/palettes, native picture/Dex/bag palette paths,
  difficulty, 49 linked boss variants/238 party entries, and existing regressions.
  ASan/UBSan are enabled in production-rule fixtures. Full builder suite:
  254 tests, four skips; nine enhancement tests executed and passed separately.
  Skips: absent optional private follower copy, two Tk GUI tests without libtk,
  and a stock source-language test without its default tree. Stock translation
  hash fixtures remain original-engine-only; expanded gameplay is English.
- **Fresh source:** 306 patched engine files and canonical overlays reproduce
  and compare in a separate clean bootstrap. Production save/difficulty/optional/
  follower checks pass there. This is source reproduction, not a second complete
  fresh native build. A stale container proxy prevented one network fetch;
  the exact locally available pinned object supplied the clean checkout.
- **Assets:** 17,534 linked assets and 1,451 pointer aliases; 698 linked sprite
  animation tables/1,818 valid pointers. Coverage reports are CONTENT_AUDIT.md,
  STAGE_E_CONTENT.csv, STAGE_E_CONTENT_SUMMARY.json and STAGE_E_ABILITY_ACCESS.json.
  Generated voxel checks: 188 interiors, zero failures, 77 upstream allowances,
  zero console approvals. No new artwork is claimed.
- **Storage:** actual filesystem/save tests preserve original/A/B/C/D sentinels;
  mutable state/data paths use `/3ds/emerald3ds-custom-stage-e-v050/`.
  No save migration. The package gate caught and corrected the new plate-cache
  fragment's legacy stat path; `.inc` files are now included in source scanning.
  Source and engine-only publication audits run separately
  from private content-bearing packaging. No ROM/save/firmware/data pack is committed.
- **Emulator / physical console / campaign:** NOT performed for this integration.

## Remaining acceptance and next task

The frozen private ZIP is ready:
`work/stage-e-private/Emerald3DS-Custom-StageE-private.zip` (21,751,803 bytes).
Compiled project source: `4271253e38908a0bb9f44e163cf748773e31b3ac`, clean at
packaging. ZIP SHA-256:
`bfd79203e9832da87512221441c577c2c5e1392a91484e83e879ca9c1a49184a`.
The archive was opened and CRC-checked; its application hashes match the compiled
outputs and manifest. It includes attribution/license notices. Older packages
remain separate. STAGE_E_BUILD_OUTPUTS.json records all output paths/hashes;
the engine-only release audit passes separately. Metadata follow-up commits do
not replace this frozen package.
Use DEVICE_TESTS.md on the original XL. Seed 1 predicts Floragato (#907) in
Torchic's ball, providing an easy Gen 9 device check without a developer grant.

119 extra form mappings use the native fallback because their raw follower
metadata is incomplete; 490 are shared/unmatched by source name. Base art
metadata is present but not visually certified. Expansion local multiplayer/
trade UI, localized expansion builds and full original-engine application build
are outside current verification; some screens retain native pixel controls.
Original-XL frame pacing, memory, scenic/follower transitions and complete campaign
stability remain pending. The next blueprint milestone is Stage F campaign/
packaging acceptance after device feedback; no new Stage F gameplay is implemented.
