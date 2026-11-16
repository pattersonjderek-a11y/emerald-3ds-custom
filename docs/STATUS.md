# Stage F boot/graphics repair — implementation verified on host; device retest pending

Current branch: `fix/stage-f-intro-boot`; separate tree `build/stage-f-boot`.
Derek supplied actual original-3DS-XL failures from the InstallerFix package:
intermittent intro `[FS]` fatal errors, noisy logo/intro sprite boxes, missing
map textures in both 2D and voxel, and ineffective voxel toggles. One later
launch reached gameplay and exited cleanly; this is not a passing visual test.
The private uploaded log identifies Old 3DS XL, matching engine/pack ABI
9ef120da, repeated rejected SMOL headers in LZ-only loaders, and failed voxel
atlas scratch allocation. Its heap room fell from 1,421 KiB to 280 KiB with
1,491 KiB of cached assets. No short-read/CRC failure is present in that session;
the earlier photographed boot fatal was not reproduced by this supplied log.

The repair restores native expansion compression dispatch in the shared heap
loader and title logo, adds owned zero-word padding for SMOL/tANS lookahead,
and limits speculative caching on constrained heaps. Mandatory bundles/UI are
loaded before selecting warm-up policy; low-memory launches use a demand cache
of at most 256 KiB while reserving 1 MiB where reclaimable. The eight-frame
pointer grace and upstream high-memory cache ceiling remain. Held-item icons
use their actual native raw paths. Fatal messages now wrap the asset path.

Native ARM11 compilation passed in the frozen SDK. Actual packed graphics pass
176 production codec/heap-loader comparisons with native raw inputs under host
ASan/UBSan, including intro/title, all compressed tilesets and representative
Gen 1–9 art. Production allocation/cache tests pass using the observed XL heap
values. Existing `make verify` and 286 builder tests pass (four inherited skips).
Fresh bootstrap compares 307 engine paths and 883 canonical overlay files;
production save/difficulty/optional-rule and actual-asset codec fixtures pass
against that fresh engine source. This is not GPU execution, a successful
console boot or a second clean native build. The production console pack parser
passes all 17,511 real payloads on the host. The original-installer upgrade,
whole-folder backup and interrupted-recovery rehearsal passes with 11 synthetic
state files; the extracted portable installer verifies on Python 3.12.14.

Frozen repair source: `a327ca6dff9549ad8b803ad26e90886def351c84`, pushed to
`fix/stage-f-intro-boot`. Native engine/pack ABI **a62520cf**. Private package:
`work/stage-f-bootfix-private/Emerald3DS-Custom-StageF-BootFix-private.zip`,
22,030,047 bytes, SHA-256
`d38b205034baa9755bc208e1cf8c63216ba6cdf622ddf752aad753a7add0785f`.
Archive read-back and every entry's source hash pass. Native output paths,
hashes, actual commands and evidence are in STAGE_F_BOOTFIX_OUTPUTS.json and
STAGE_F_BOOTFIX_REHEARSAL.json. Source and engine-only publication audits pass;
the content-bearing private ZIP is not committed or uploaded to GitHub/CI.
Metadata follow-up commits do not replace this frozen ZIP. Device retesting is
the next task; no emulator or physical SD test was performed here. The public
retail-ROM-only expanded-content recipe remains a separate release blocker.

Same F namespace/schema/rules; preserve existing F progress/settings with the
checked installer. No new gameplay rules, dependency pins, donor content or save
migration. Original E/F/InstallerFix outputs remain frozen. InstallerFix was
delivered privately to Dropbox; it is the build that supplied these failures.
Historical stage/checkpoint reports below describe their evidence at that time.

---

# Stage F release validation — historical InstallerFix checkpoint

The current blueprint defines A–F and has no next stage letter. This follow-up
finishes independent release engineering on `fix/stage-f-release-validation`,
preserving the frozen F baseline and all prior E source/build/Dropbox artifacts.
No new gameplay, renderer, settings, roster or difficulty behavior is introduced.
The seven native F outputs match their verified b2cd7f6 baseline hashes; they are
reused, not newly compiled. The F namespace/schema/rules remain unchanged.

Three production failures were reproduced with synthetic data: same-length
corruption of copied settings was accepted; compressed pack entries passed the
Python installer although the console rejects them; and interruption while
recursively removing a failed app could strand recovery. Fixes now read back all
user state, validate pack layout/compression/ranges before writes, and recover
using directory renames while preserving failed copies for inspection. Fault
tests cover interruption of recovery itself and repeat recovery.

The previous campaign audit referenced image 07640000 from before the final
verification relink. Re-auditing actual final image 0c7d088f passes with identical
51 placements / 155 fixed land species / 124 headers. Packaging now requires an
audit matching the current compiled image, and optional native reuse requires
all seven recorded binary hashes. No native game data was changed to fix this.

Verified follow-up checks: 286 host/builder tests passed with the same four
inherited skips, including 28 package/installer/evidence tests. Fresh source
comparison passes for 307 engine paths and 880 canonical overlay files. The
actual original F portable installer was used to create a host installation;
the hardened update, preservation of 11 synthetic state files, interrupted
recovery, repeated recovery and original/E sentinels all pass. The production
console C parser passes all 17,511 actual pack payloads on the host under
ASan/UBSan. Seven native baseline hashes match; no native compile was rerun.
Frozen follow-up source: c36f1a01b6e0e9f00d165cf9d672a3c2d4872f45; reused native
source: b2cd7f6. New private ZIP:
`work/stage-f-installer-fix-private/Emerald3DS-Custom-StageF-InstallerFix-private.zip`,
22,029,491 bytes, SHA-256
`d1c77fcb150e02ac5ce9b5671e4293dafe532bef8cf7bf958ee01eb5265e610d`.
All archive entries were read back, and the extracted portable installer verifies
using host Python 3.12.14. It contains current campaign, native-baseline and host
rehearsal metadata. New-package native hashes equal original F; original E/F ZIP
hashes remain unchanged. See STAGE_F_INSTALLER_FIX_OUTPUTS.json and
STAGE_F_INSTALLER_FIX_REHEARSAL.json. Metadata follow-up commits do not replace
this frozen ZIP. No Dropbox upload or public package publication was performed. Physical console, campaign and public ROM-only recipe gates are
still pending. There is no supplied E/F device result and no emulator result.

---

# Stage F — private campaign/package build ready; device acceptance pending

Worktree `/workspace/emerald-3ds-stage-f`, branch `project/stage-f-campaign`.
Stage E source, compiled outputs and frozen ZIP remain in their separate worktree;
its private Dropbox delivery succeeded. No E or F device results have been supplied.

F adds 51 fixed wild slots in 22 Hoenn areas (Gen 4–9 plus Murkrow), retaining
all original local species, levels, rates, slot weights and v0.5.0 timed slots.
The native data audit reads actual compiled headers and confirms the placements,
legal attacks at minimum levels and indexed pictures. Standard trainers, all
progression scripts/rewards/HMs, rematches and postgame structures are retained.
See STAGE_F_CAMPAIGN.md and the generated metadata report.

New `/3ds/emerald3ds-custom-stage-f-v050/` namespace; no old-stage save import.
Save schema remains 1 / 52 bytes, rules ID `0x00050050`. No flags or variables
allocated. v0.5.0 global seed/settings policy remains authoritative.

A production private source-data recipe builder and laptop installer are added.
They verify executable RomFS ABI + pack CRCs/hashes, keep a complete old-folder
backup including settings/sidecars, and roll back interrupted updates. The portable
installer needs Python 3.11+ only. This is distinct from the upstream retail-ROM
recipe; a public ROM-only expansion content supply/recipe is still unresolved.

Final verified source/package checkpoint: `b2cd7f67eea112eec2e5cdd86cc85aebfabeace3`.
Native ARM11 compilation and full `make verify` passed: 60 required symbols,
no strong undefined symbols, 17,534 linked assets / 1,451 aliases. Full builder
suite: 278 tests, four inherited skips; all nine enhancement adapters executed.
24 focused campaign/installer tests pass. Fresh bootstrap compares 307 engine
paths and 878 canonical overlay files; production save/difficulty/optional-rule
fixtures pass there. This is not a second fresh native build.

Engine-only release + matching pack use ABI `9ef120da`, 17,511 data files.
The actual pack passes the production console C parser on the host under
ASan/UBSan, including every payload CRC and wrong ABI/profile rejection. The
actual-bundle host rehearsal passes first install, compatible update, complete
backup and interrupted-commit recovery with 11 synthetic state files. Legacy/E
sentinels remain unchanged. The extracted portable installer passes `--verify`
with host Python 3.12.14. No mounted physical SD card or real player save was used.
Source and engine-only ZIP publication audits pass. Generated voxel validation
reports 188 interiors, zero failures, 77 inherited allowances and zero device
approvals. Full commands/logs/hashes: STAGE_F_BUILD_OUTPUTS.json.

Frozen PRIVATE test ZIP: `work/stage-f-private/Emerald3DS-Custom-StageF-private.zip`
(22,022,981 bytes), SHA-256
`c2043807e6b2bbc78125e18886348bd681237397d05654e5cdb8c198a8bda86a`.
Read-back CRC and all archive-entry hashes pass. It includes the paired engine,
pack, install receipt, portable installer and instructions/licenses. It has not
been uploaded to Dropbox or GitHub. The E Dropbox file remains unchanged.
Metadata follow-up commits do not rebuild or replace this frozen F ZIP.

Original-XL boot, rendering, progression through Champion and representative
postgame, actual SD recovery and performance remain PENDING. No emulator used.
Stage F cannot be called accepted until those device results are supplied.
The other final-release blocker is a validated retail-ROM-only expanded-content
recipe: audit/attribute its additional asset inputs, then implement parity-tested
extraction/build without a content-bearing literal pool. The working private
source-build pipeline does not establish that public release route.
Next action: use STAGE_F_INSTALL.md and the F campaign/device checklist; fix
reported regressions in a separate checkpoint/package, preserving this baseline.

---

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
