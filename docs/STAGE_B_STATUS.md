# Stage B status

Stage A is complete in source, host regression checks and native compilation;
physical-console acceptance remains **PENDING**. Its full findings and exact
commands are preserved in [STAGE_A_STATUS.md](STAGE_A_STATUS.md), with immutable
artifact hashes in [BUILD_OUTPUTS.json](BUILD_OUTPUTS.json).

Before Stage B, verified every recorded Stage A artifact size/SHA-256 and ZIP
CRC, copied the private package and manifest to ignored
`work/baseline-stage-a-48d8096/`, and pushed branch `project/stage-a` and tag
`stage-a-verified-48d8096` at `48d809677b496b029415d1af2e6524c4a08714d8`.
GitHub accepted both; no write blocker. Original upstream history is preserved.
No console results were supplied. Stage B is separate on `project/stage-b`,
using `build/stage-b` and its own SD namespace. Stage A build trees/package
are not used as Stage B output destinations.

## Implemented

- Audited flags, variables, native save structures, serializer and checksums.
  Reserved 52 unused bytes at SaveBlock1 offset `0x988`; no new flags/variables,
  no size/offset changes, no sidecar. See [SAVE_FORMAT.md](SAVE_FORMAT.md).
- Added versioned, little-endian, CRC-protected run configuration, bound to
  the initialized trainer ID and containing an independent run ID, seed,
  mode/options/difficulty, algorithm version and content-rules identifier.
- Added native new-game setup before Birch's introduction: mode, difficulty,
  locked customization preview, automatic/manual numeric seed, summary and
  confirmation. Only Standard/Normal can be confirmed; future rules are
  visibly unavailable and rejected by serialization too.
- Draft choices remain in temporary RAM. The native new-game initializer
  consumes confirmed choices exactly once after its destructive resets and
  trainer-ID initialization. Cancellation cannot commit or write a save.
- Continue reads existing rules without generating a seed. A read-only
  Run Settings page opens on physical START in the normal dual-screen field,
  or from RUN SETTINGS in the classic pause menu.
  Corrupt/unsupported records block Continue and all ordinary/full-link save
  entry points before side effects, preserving the record for recovery.
- Expansion runtime paths and launcher metadata identify Stage B separately.
  Existing original-engine builds retain their Stage A path. Graphical options,
  clock behavior, expansion content and renderer remain inherited.
- Engine implementation, including six new files, is in the canonical expansion
  patch. Added safe patch regeneration, Stage B wrapper and private packaging
  support; enhancement regression fixtures can explicitly select the new tree.

## Verification

Production host fixtures pass ASan/UBSan: round trips; seed boundaries; all
416 single-bit record corruptions per edge seed; unsupported schemas,
algorithms/content/rules/bindings; unchanged outputs on rejection; explicit
legacy records; no-op prevention; setup navigation/locked choices/manual entry;
new-game reset and cancellation; the complete production NewGameInitData;
actual save-sector serialization, checksum, loading and older-slot recovery;
actual Continue, ordinary save and full-link save guards.

Native compilation passed in the frozen Stage A SDK. Initial command:
`python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir build/stage-b --make -j4 --python python3`.
A missing `main_menu.h` declaration for CB2_InitMainMenu was diagnosed and
fixed in the engine patch; resumed with
`make -C build/stage-b/3ds_port -j4 PYTHON=python3` (exit 0). The subsequent
START-adapter integration was rebuilt with that same native make command.
`make -C build/stage-b/3ds_port verify PYTHON=python3` passed the existing
clock/settings/input/graphics/voxel/expansion regressions and new production
configuration tests, plus ARM11 hard-float/link audit with **45 required
symbols**, no strong undefined symbols, 17,536 indexed assets and 1,451 pointer
rows. Final `tools/stage_b.sh package` repeated this gate after the START
integration fix and passed (exit 0), including the new access regression.

Additional commands/results:

- `python3 3ds_port/tests/custom_run_test.py --tree build/stage-b`: all
  production harnesses passed ASan/UBSan, including START access and storage
  canaries preserving every byte outside the reservation.
- `EMERALD3DS_EXPANSION_TREE="$PWD/build/stage-b" python3 -m unittest builder.tests.test_expansion_enhancements -v`:
  9 passed against this Stage B tree.
- Same tree selection with `python3 -m unittest discover -s builder/tests -v`:
  95 tests, two existing skips (private follower copy and Spanish source fixture).
- `python3 3ds_port/tests/storage_isolation_test.py`: both original-engine and
  expansion namespaces passed production save/filesystem sentinel tests.
- `python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir work/stage-b-clean`:
  fresh pinned source reproduction; all 269 patched files match the build tree.
  Production run tests also passed on this fresh tree. This is a source/host
  reproduction, not a second full native compilation.
- ARM ELF debugger confirmed sizes 15,536 / 3,884 / 1 and record/flags/vars
  offsets 0x988 / 0x1270 / 0x139C, identical to Stage A.
- Python compilation and owner-run strict source publication audit passed.

Private logs: `work/stage-b-native.log`, `work/stage-b-native-start-access.log`,
`work/stage-b-verify.log`, `work/stage-b-host-run.log`,
`work/stage-b-fresh-tests.log`, `work/stage-b-builder.log`,
`work/stage-b-adapters.log`, `work/stage-b-isolation.log`,
`work/stage-b-save-layout-after.txt`, `work/stage-b-source-audit.log`.
SDK versions are unchanged, recorded again in `work/stage-b-versions.txt`.
Inherited asset-generation probes report absent unlinked alternate-form/FRLG
art; the complete linked asset index passes. Full species/follower coverage
is still a later audit, not claimed by this stage.

Native/private outputs: `build/stage-b/3ds_port/emerald3ds.3dsx` and `.smdh`;
engine-only `build/stage-b/3ds_port/dist/Emerald3DS.3dsx` and `.smdh`;
matching private `build/stage-b/3ds_port/build/emerald3ds.pak`.
Implementation checkpoint: `62d7edce10e4fc35e00b8c629e899bd9bb143390`.
Final `tools/stage_b.sh package` passed: release/pack, full make verify,
9 expansion adapters, strict source audit, every matching pack-entry CRC,
embedded namespace/ABI checks and private package generation. Engine-only
ZIP strict audit passed separately. The final package ZIP CRC and contents
passed inspection: app, metadata, debug marker, manifest and instructions;
no ROM, saves, firmware, separate pack or CIA. Package build source was clean.

| Output | Bytes |
| --- | ---: |
| `build/stage-b/3ds_port/emerald3ds.3dsx` | 54,900,464 |
| `build/stage-b/3ds_port/dist/Emerald3DS.3dsx` | 9397208 |
| `build/stage-b/3ds_port/build/emerald3ds.pak` | 44,765,664 |
| `work/stage-b-private/Emerald3DS-Custom-StageB-private.zip` | 20,502,687 |

Private manifest: `work/stage-b-private/manifest.json`. Recorded sizes/hashes:
[STAGE_B_BUILD_OUTPUTS.json](STAGE_B_BUILD_OUTPUTS.json). ABI `a3b35321`,
17,513 data files / 43,972,689 bytes; all pack CRCs and indexed assets pass.
Private ZIP SHA-256:
`9e52bde5bece05774707e9ac075b4a7e79c8084de2dec6f9de6435d1d7b3efb3`.
The Stage A artifacts and separately preserved ZIP were rehashed after Stage B
compilation and remain unchanged. Stage A ZIP stays at
`work/baseline-stage-a-48d8096/Emerald3DS-Custom-StageA-private.zip`.

Final source reproduction: all 269 engine patch files and 293 canonical overlay
files match `work/stage-b-clean`, reverse application passes, and the final
production host harnesses pass there too. Logs also include
`work/stage-b-package.log` and `work/stage-b-engine-audit.log`.
No new dependency, build or source-publication blocker remains. The generic
builder installer still targets Stage A, the forwarder identity and a public
expansion player-data recipe remain unvalidated, and full art/follower coverage
is deferred. Use the private embedded ZIP for device testing.

## Acceptance and next task

No emulator, physical console or campaign result is claimed. All device
results remain PENDING in [DEVICE_TESTS.md](DEVICE_TESTS.md). Confirm setup,
cancel/Continue/save/restart and UI return paths on the 3DS XL before expanding
rule behavior. After Stage B acceptance, Stage C implements seeded starters,
wild tables and trainer parties; Hard/Custom battle rules remain Stage D.
