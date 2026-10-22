# Stage C status

Stage C is implemented on `project/stage-c`, based on Stage B `ba750f8`.
The pinned engine and frozen Stage A SDK are unchanged. Native compilation
and production host fixtures pass; exact evidence is recorded below. **No emulator, physical-console or campaign result is claimed.**
All device acceptance remains PENDING.

## Preserved baseline

Stage A source/checkpoint/tag, compiled tree and private ZIP remain intact;
see [STAGE_A_STATUS.md](STAGE_A_STATUS.md) and [BUILD_OUTPUTS.json](BUILD_OUTPUTS.json).
Stage B source, native results and hashes are preserved in
[STAGE_B_STATUS.md](STAGE_B_STATUS.md) and
[STAGE_B_BUILD_OUTPUTS.json](STAGE_B_BUILD_OUTPUTS.json).
Its ZIP was rehashed and copied separately to
`work/baseline-stage-b-ba750f8/Emerald3DS-Custom-StageB-private.zip` before C.
The original B package is also privately uploaded to Dropbox at
`/Emerald3DS-Custom-StageB-private.zip`; no shared link was created.
Stage C uses its own `build/stage-c`, private package and
`/3ds/emerald3ds-custom-stage-c/` runtime directory. No save import occurs.

## Implemented

- Saved-seed algorithm 1, content rules `0x00020001`; independent numeric
  starter, wild, trainer and trainer-generation keys. No pointer addresses,
  frame time, trainer ID seed substitution or global battle RNG dependency.
- Randomized/Normal now works. Starters, wild and trainers default ON and can
  be toggled independently; at least one stays ON. Generation 1–9 filters,
  optional no-legendaries and similar-strength restrictions are implemented.
  Abilities/field items/held-item randomization and Hard/Custom difficulty stay
  visibly locked and are rejected by the codec.
- Three distinct, usable level-5 starters share the real name/sprite/cry/gift
  resolver. Wild tables are stable per map/time/method/slot, retaining native
  slot probabilities, encounter rates and levels. Overworld identity is
  resolved before display and retained into battle. DexNav, Pokédex area and
  match-call table readers use the same mapping.
- Campaign trainers, bosses and rematches use the actual party factory after
  native template selection. Preserve levels, size, IV/EV intent; regenerate
  legal level-up moves and native ability/gender. Handle incompatible signature
  items and retain Mega/Primal compatibility where the selected pool permits.
  Local party/pool seeds are stable. Rival starter family follows the chosen
  replacement, including ordinary eligible level evolution and starters-only
  randomization. Partner/facility/link/recorded/special logic is protected.
- Pool validation checks actual indexed front/back/icon/normal/shiny assets,
  enabled data, native ability, level-up attack and stable forms. Invalid,
  battle-only and unsupported alternate forms are excluded. Standard returns
  original tables/templates. Exact exclusions/fallbacks are in [RULES.md](RULES.md).
- Existing 52-byte save allocation, schema 1 and native checksums remain
  unchanged. Continue/save reject invalid/unsupported records or an unusable
  selected pool; cancellation and new-save initialization retain Stage B's
  transaction behavior. No new flag/variable conflicts or sidecar.
- All engine changes, including four new C/header files, are captured in the
  canonical expansion patch. Canonical test/build/package tools remain at the
  repository root. A/B wrappers refuse rebuilding those baselines from C's patch.

## Verification record

Commands were run inside `emerald-stage-a`, as UID/GID 1000, using the frozen
SDK described in BUILD.md (Python 3.11.2 / host GCC 12.2 / devkitARM r68).
Host-only standalone/fresh fixtures also passed with host Python 3.12/GCC 14.2.

- `tools/stage_c.sh build`: PASS. Expands to
  `python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir build/stage-c --make -j4 --python python3`.
  Full native compilation began from a separate fresh C tree, then incremental
  rebuilds incorporated fixes. First compile rejected a read-only header member;
  corrected the cloneable encounter-header qualifier without changing layout.
- `tools/stage_c.sh test`: PASS: `make -C build/stage-c/3ds_port verify PYTHON=python3`,
  9 expansion adapters, 95 builder tests (2 existing skips), strict source audit.
  Host fixtures exercise real core/menu/save adapters and production starter gift,
  map lookup and campaign party factory. Pokémon construction and synthetic
  engine tables are fixture boundaries; actual console battles were not executed.
- ASan/UBSan: 10,000 core seeds, fixed golden keys, bounded selection, distinctness,
  generation/legend/level filters, empty pools and finite BST fallback; native
  cache/reload/global-RNG independence, Standard pointer/template identity,
  wild methods/TOD/levels/rates, starter gift and legal attacks, native trainer
  party size/doubles/IV intent, compatible Mega item and protected contexts.
  Additional production tests cover rival level evolution/pool exclusion,
  trainers-only rival continuity and `CR_POOL` failure without output mutation.
- Updated production run tests preserve B round trips, bit-corruption/version/
  rules/binding rejection, complete NewGameInitData, cancellation/reset,
  actual save-sector/checksum/older-slot recovery and Continue/save guards.
  Randomized records and category/generation/balance UI now round-trip too.
- Linked ARM species/asset audit: **1,072 eligible species/forms**, with per-generation
  counts 147 / 99 / 133 / 107 / 156 / 71 / 104 / 131 / 124. Excluded 489 unsupported
  forms and 10 entries without a usable level-up attack. Each generation has at
  least three nonlegendary level-5 choices. Gen 9 starters and Ogerpon/Terapagos/
  Pecharunt pass. Summary: [STAGE_C_POOL_AUDIT.json](STAGE_C_POOL_AUDIT.json).
  This is data inspection, not ARM execution or a complete follower/cry audit.
- The linked-pool audit exposed an overly strict palette-size assumption;
  valid indexed Sprigatito/Quaxly palettes are shorter than 32 bytes. Corrected
  the runtime filter and audit together. Map metadata scans now read original
  header identities without generating unrelated tables; production lookup
  fixtures verify no randomizer-cache work occurs during that scan.
- Host seed preview using actual C core + linked pool: seed 42, Gen 9 only,
  balance OFF → Toedscruel / Tatsugiri Curly / Meowscarada. Seed 43 → Pawmot /
  Iron Moth / Wo-Chien. Compare on hardware using DEVICE_TESTS.md.
- `python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir work/stage-c-clean`:
  277 engine patch files and 300 canonical overlay/lock files match; reverse
  application passes. Both production run/randomizer suites pass there too.
  This is fresh source/host reproduction, not a second full native build.
- The versions wrapper exposed an inherited `head`/`pipefail` SIGPIPE (exit 141);
  changed first-line display to consume complete tool output, then reran it.
- Python byte compilation and shell syntax checks pass. Actual native static
  assertions keep SaveBlock1/2/3 sizes and reservation/flags/vars offsets unchanged.
  Production filesystem sentinels protect original, A and B namespaces.
- All 14 recorded A/B artifact sizes/hashes and both preserved baseline ZIPs
  were rechecked after C compilation and remain unchanged.

Private logs: `work/stage-c-native.log`, `work/stage-c-build-workflow.log`,
`work/stage-c-verify.log`, `work/stage-c-test-workflow.log`,
`work/stage-c-random-tests.log`, `work/stage-c-run-tests.log`,
`work/stage-c-fresh-bootstrap.log`, `work/stage-c-fresh-random-tests.log`,
`work/stage-c-fresh-run-tests.log`. Full linked pool metadata:
`build/stage-c/3ds_port/build/randomizer-pool.json` and `.csv`.

Native outputs: `build/stage-c/3ds_port/emerald3ds.3dsx`, `.smdh`, `.elf`;
engine-only `build/stage-c/3ds_port/dist/Emerald3DS.3dsx` and `.smdh`;
matching private `build/stage-c/3ds_port/build/emerald3ds.pak`.
Final package metadata is recorded after the packaging gate in
STAGE_C_BUILD_OUTPUTS.json. Content-bearing outputs stay ignored/private.

## Limitations and next task

Native compilation is distinct from running on an ARM11. No boot, UI display,
SD/FAT recovery, double-battle playthrough, frame rate or campaign stability is
claimed from host fixtures. [DEVICE_TESTS.md](DEVICE_TESTS.md) contains the
pending console checks. Gen 1–9 eligibility is not a complete species/follower
asset certification, nor a guarantee every species is catchable in every seed.

Special scripted encounters, gifts/eggs, roamers/outbreaks/Feebas, partner and
facility battles remain inherited/protected; the fixed campaign roster and
full art/follower inventory remain later stages. Public player-data recipe,
generic installer namespace and CIA forwarder are still unvalidated. Do not
use another build's data pack or migrate its save into Stage C.

Next: Derek tests Stage C's starter identity, seed/reload, visible wild identity,
rival and representative boss/double battles while retaining the A/B backups.
Stage D implements independent Normal/Hard/Custom difficulty composition; Stage E
handles optional abilities/items and full follower coverage. No actual difficulty
battle changes or optional item/ability randomization were added in Stage C.
