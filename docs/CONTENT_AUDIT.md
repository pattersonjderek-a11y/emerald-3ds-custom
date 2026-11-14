# Stage E linked content and follower audit

Generated with `tools/stage_e.sh audit` from the compiled PROGBITS
`3ds_port/build/gamedata_image.elf` and matching asset/pointer indices.
`STAGE_E_CONTENT.csv` is metadata only; no pixel, sound or game-data payload
is committed. The full JSON stays ignored in `work/stage-e-content.json`.
`STAGE_E_CONTENT_SUMMARY.json` identifies the exact image hash. Re-run after
relinking; counts alone do not establish matching engine/data outputs.

- **1,025** National Dex base species, including **120** Gen 9 species, have
  native stats/ability/learnset data and indexed front/back/icon/normal/shiny art. Stats/types and all three native ability slots are recorded.
  Twenty-seven base species have palettes shorter than 16 colors; the native
  UI now reads their actual length and zero-pads unused entries, rather than
  resolving an oversized request back to an INCGFX stub. Production picture,
  bag, palette and Dex paths have ASan/UBSan coverage for this case.
- All 1,025 reference nonempty cry samples; **1,024** distinct wave pointers
  are referenced. This proves data presence, not audible playback or uniqueness.
- **1,571** enabled species/form entries were inspected. The authoritative
  v0.5.0 core permutation uses the 1,025 base species. Additional forms are
  retained by the native engine but are not extra entries in that permutation.
- Base followers: **962 source-name matches**, **63 shared/unmatched names**,
  no missing metadata. Names such as CASTFORM_NORMAL legitimately use a shorter
  CASTFORM path. Source-name matching does not certify exact artwork.
- All forms: 962 name matches, **490 shared/unmatched**, **119 incomplete raw
  mappings**. Those incomplete mappings follow the native Substitute fallback
  where available. They are not complete species artwork. No new art was
  downloaded, invented, or attributed to an unverified donor.

Each follower record lists resolved image assets, frame-table entry count,
normal/shiny palette presence and female-specific metadata. A relative-frame
sheet can have one frame-table entry covering several animation frames; that
entry count is not the count of animated pictures. Linked animation-table
validation and production compressed-sheet/palette tests are separate checks.
No visual or movement acceptance is implied. A terminal species may legitimately
have no evolution/form table. Complete ability/move mechanics, every form,
female art, campaign progression and final follower artwork remain unaudited
beyond these explicit fields and the production tests.

`STAGE_E_ABILITY_ACCESS.json` inventories 313 accessor references and seven
explained raw species references. The central GetSpeciesAbility resolver handles
summary/field/AI/battle reads. Trainer and facility constructors deliberately
convert native template ability IDs to stored slots; they must not resolve a
randomized ability twice. Dynamic battle changes such as Trace remain native.
The audit rejects new unexplained raw species paths. Resolver consistency,
protected signatures, empty/alias slots, battle snapshots and context safeguards
are tested under ASan/UBSan; that is host evidence, not a battle playthrough.

Generated voxel verification inspected 188 interior layouts with no failures
and 77 existing upstream allowances. The generator explicitly reports zero
console-approved interiors in this build. Expansion art mismatches use the
existing `--allow-art-mismatch` adapter. FRLG uses native 32-bit attributes and
its own border dimensions; the new extra tileset-bank extension is restricted
to compatible Hoenn layouts. FRLG visuals still need console review.

Historical `custom_random_pool_test.py` additionally checks the stricter old C
art/attack/form subset (1,072 species/forms). That is retained coverage evidence,
not the eligibility rule of the new v0.5.0 base-species permutation. Gen 9 proof
on device is described in DEVICE_TESTS.md: seed 1 maps Torchic's ball to
Floragato (#907), as predicted by the production resolver.
