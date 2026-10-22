# Stage D difficulty implementation

Work is on `project/stage-d`, based on visual-fix checkpoint `45d3796`.
Derek explicitly requested Stage D before supplying visual-fix device results.
The original C and VisualFixes builds/packages remain unchanged. No native
engine pin, SDK update, donor merge or optional ability/item randomization.
Historical evidence: [Stage A](BUILD_OUTPUTS.json), [Stage B](STAGE_B_STATUS.md),
[Stage C](STAGE_C_STATUS.md), [visual follow-up](STAGE_C_VISUAL_FIXES_STATUS.md).

## Implemented

- Independent Standard/Randomized with Normal/Hard/Custom difficulty. Controller
  setup, readable rule confirmation (LEFT/RIGHT), and read-only in-play rules
  (START, then A) use the existing native interface. No boss rosters are shown.
- Reuse the existing 52-byte, CRC-protected, trainer-bound save record. Allocate
  no flags, variables or sidecar. Hard/Custom are validated, immutable per run;
  new-game drafts commit after initialization. New rules ID `00030001`, same
  schema 1 / randomizer algorithm 1. Historical C Normal keys remain supported
  by the codec; no cross-install import/migration is performed.
- Hard: progression hard caps, forced Set, no player bag healing/revives/PP or
  X-items/stat boosts during campaign trainer battles; deliberate tactical AI
  without omniscient/prediction/hidden-party flags; 49 native prepared boss
  variants (238 Pokémon). Boss levels, party sizes and battle types are retained.
  Variants have 31 IVs, 64 EVs in each stat, compatible berries or existing held
  items; Roxanne gains Aron coverage and Brawly's unsupported Focus Punch plan
  becomes Confusion. Existing curated fixed moves otherwise remain.
- Templates are chosen before seeded species substitution. Prepared randomized
  bosses receive legal damaging level-up moves with type coverage plus one
  available native status move. No fixed-species restoration after randomizing.
- Custom selects off/hard/soft cap, Set/player-choice style, separate healing and
  boost restrictions, native/tactical AI, native/prepared bosses. EXP multipliers
  remain unavailable; below-cap EXP is unchanged. Balls, wild battles, mandatory
  catch/intro tutorials, scripted/key actions and existing special facilities
  retain their native item behavior. Allies retain their native templates/AI.
- Hard caps apply to battle EXP (after multipliers), Rare/EXP Candies and daycare.
  Over-cap gifts are preserved; daycare level/cost subtraction cannot underflow.
  Caps: 15/19/24/29/31/33/42/46; 58 for the whole League including Champion;
  100 after first Champion, including rematches/postgame. Soft reduces battle
  EXP above the threshold, without a level/candy/daycare ceiling.

Exact policy and exclusions: [RULES.md](RULES.md). Save bytes: [SAVE_FORMAT.md](SAVE_FORMAT.md).

## Verification evidence

- **Host:** production codec/menu/new-game/save-sector recovery and guards pass
  ASan/UBSan. New difficulty suite executes production cap/reward, native AI
  dispatcher, native trainer selection and party factory composed with the real
  randomizer, native item validator/party callback and Rare/EXP Candy fragment,
  plus daycare level/cost calculation. It covers all gym/League/postgame caps,
  overflow, over-cap gifts, cancellation, unsupported policies, independent
  Custom choices, fixed/randomized bosses, doubles, reset stability and allies.
- **Native compilation:** `tools/stage_d.sh build` passes in the frozen SDK,
  container `emerald-visual-fixes`. Compiled application:
  `build/stage-d/3ds_port/emerald3ds.3dsx`; symbols:
  `build/stage-d/3ds_port/emerald3ds.elf`; linked-data image:
  `build/stage-d/3ds_port/build/gamedata_image.elf`.
- `tools/stage_d.sh test`: full make verification, 9 enhancement adapters,
  95 builder checks (2 existing private-asset/Spanish skips), strict source audit.
  Link verification requires 56 game symbols, ARM11 hard-float, no strong
  undefined symbols; 17,536 assets and 1,451 pointer rows verified.
- **Native linked data inspected:** all 49 Hard variants / 238 party entries
  retain native levels/size/battle type and contain intended IVs/EVs/items, with
  no omniscient variant. This GDB audit reads data; it does not execute ARM code.
  The complete 1,072-entry species pool is identical to the visual-fix baseline,
  including 124 eligible Gen 9 entries. No new species assets were imported.
- **Fresh source/host reproduction:** clean pinned worktree, normal bootstrap,
  283 engine and 309 canonical overlay/lock file byte comparisons, reverse patch check and production difficulty,
  run/save/randomizer/visual fixtures. All implementation lives in canonical
  root platform/tests/tools or the 283-file expansion patch, including new files.
- **Emulator:** not exercised. **Physical console:** Stage D and visual fixes
  PENDING; no campaign/balance/performance acceptance is claimed. Derek previously
  reported general C play on an original 3DS XL and the three visual failures.

Build log: `work/stage-d-build-final.log`; full checks: `work/stage-d-test-final.log`;
focused host log: `work/stage-d-difficulty-host.log`; fresh reproduction:
`work/stage-d-fresh-final.log`, `work/stage-d-fresh-tests-final.log`.
An initial in-progress link saw a stale object after the new clamp helper was
added; explicitly rebuilding affected objects resolved it. On-demand asset
conversion also prints inherited missing optional art diagnostics; the complete
asset/pointer and pool audits pass. Full follower/form-art coverage remains E.
The first fresh-source attempt used a host-absolute worktree path inside Docker;
running source bootstrap on the host resolved that path mismatch without changing
source pins or disabling certificate validation.

## Private deployment / next task

Stage D exclusively uses `/3ds/emerald3ds-custom-stage-d/` for saves/backups,
clock, settings, logs and optional data. Production filesystem tests protect
original/A/B/C sentinel installs. Keep the C and VisualFixes packages/directories
for rollback. Start a new D save; do not copy existing saves or unrelated packs.

Private output destination: `work/stage-d-private/Emerald3DS-Custom-StageD-private.zip`.
Matching native release and data: `build/stage-d/3ds_port/dist/Emerald3DS.3dsx`
and `build/stage-d/3ds_port/build/emerald3ds.pak`; never publish the latter or
embedded app. Final manifest/hashes are recorded after packaging.

Next: original-XL D smoke/balance testing and visual-fix retest using
[DEVICE_TESTS.md](DEVICE_TESTS.md). Then Stage E can address optional abilities/
items and the comprehensive follower/art audit. Hardware/campaign acceptance
remains separate from completed engineering checks.

## Final checkpoint and package

Implementation/source checkpoint: `ece640577c1f2a001c880eb94b174ae62187ba23`, pushed to
[project/stage-d](https://github.com/pattersonjderek-a11y/emerald-3ds-custom/tree/project/stage-d).
No GitHub write blocker. `tools/stage_d.sh build`, `tools/stage_d.sh test` and
`tools/stage_d.sh package` all passed. The private package was made from a clean
source checkpoint; all package CRCs/hashes and the separate engine-only ZIP
strict publication audit passed. All 30 recorded A/B/C/visual output hashes are
unchanged. No ROM/save/firmware/content build artifact is committed or published.

| Output | Bytes |
| --- | ---: |
| `build/stage-d/3ds_port/emerald3ds.3dsx` | 54,925,412 |
| `build/stage-d/3ds_port/dist/Emerald3DS.3dsx` | 9,410,988 |
| `build/stage-d/3ds_port/build/emerald3ds.pak` | 44,776,832 |
| `work/stage-d-private/Emerald3DS-Custom-StageD-private.zip` | 20,518,236 |

ZIP SHA-256: `79ef411c6116bd3db39a451523b0f2a7885de0de8ee33ed936e5805c50f727e2`. Matching engine/data 9e27eb83 `9e27eb83`; 17,513 data entries /
43,983,857 bytes. Exact paths/hashes: [STAGE_D_BUILD_OUTPUTS.json](STAGE_D_BUILD_OUTPUTS.json).
Manifest: `work/stage-d-private/manifest.json`. Package log:
`work/stage-d-package.log`; engine-only audit: `work/stage-d-engine-audit.log`.

No unresolved build/dependency/publication blocker remains. Stage D balance,
visual-fix acceptance, save/Continue and performance on the original XL remain
pending. No emulator or physical-console execution was performed by Codex.
