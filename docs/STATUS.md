# Stage A status

Work started 21 October 2026 (America/Los_Angeles), on clean `work` at
`a30828a`, with candidate baseline `8ebb7355742ce43bbb10528044f9a175fc990a64`
as its parent. Work continues on local branch `project/stage-a`. The
root `PROJECT_BLUEPRINT.md` is the current specification. No donor merges,
engine dependency upgrades, randomizer, difficulty, or save-layout changes.

## Completed implementation

- Frozen the existing official CI SDK image by digest; added
  `tools/stage_a.Dockerfile` with observed host-package pins and
  `tools/stage_a.sh build|test|versions`. Built the documented SDK image.
- Repaired two fresh-build prerequisite failures in canonical
  `3ds_port/full.mk`: generated makefile directory ordering and the intro
  graphics prerequisite. Preserved rendering and existing expansion systems.
- Centralized custom storage in `3ds_paths.h`, redirected mutable paths,
  packs, loose-data markers, logs and diagnostic/scenario paths; removed
  automatic legacy-save migration. Launcher title identifies the custom app.
- Updated installer/uploader paths and added production filesystem/save
  isolation checks to `make verify`. Settings and clock tests retain their
  production-code coverage. No engine-side edits or patch regeneration needed.
- Added private smoke packaging with ABI/data CRC, asset-table, application
  path and hash checks. No public publication or SD-card write was performed.
- Recorded build setup, source provenance, installation audit and pending
  hardware checklist in `BUILD.md`, `SOURCES.md`, `DEVICE_TESTS.md`.
  Historical development/installation instructions are retained with a custom
  build pointer. Extended existing `AGENTS.md` without replacing its gotchas.

## Checks and evidence

Private full logs and package manifests live under ignored `work/`.

| Evidence | Command / result |
| --- | --- |
| Source inspected | Blueprint, all applicable AGENTS instructions, upstream.lock, development/feature docs and CI read; pins unchanged |
| First host bootstrap | Failed at `png.h`: host lacked libpng headers; moved build to official SDK container |
| Container tools | Initial host-generated binaries required newer GLIBC/GLIBCXX; fixed with `make -C build/expansion clean-tools` in container |
| Fresh make ordering | Reproduced `open: build/port_art.mk: No such file or directory` and missing intro `.4bpp` rule; canonical fixes applied |
| Expansion adapters | `python3 -m unittest builder.tests.test_expansion_enhancements -v`: 9 passed |
| Builder suite | `python3 -m unittest discover -s builder/tests -v`: 95 tests, 2 existing skips in initial host/container runs |
| Storage isolation | `python3 3ds_port/tests/storage_isolation_test.py`: passed production initialization/write/reload and legacy sentinels |
| Python compilation | `python3 -m compileall -q builder tools 3ds_port/scripts 3ds_port/tests`: passed |
| Source publication audit | `python3 tools/release_audit.py --repo . --strict`: passed during implementation; final results below |
| Fresh expansion source | `python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir work/fresh-expansion`: passed; canonical files match; reverse patch check passed in both expansion trees |
| Native expansion | `tools/stage_a.sh build` passed; `make verify` passed with 38 required symbols, no strong undefined symbols, all 17,536 indexed assets and 1,451 pointer rows verified |
| Emulator | Not run; Azahar/Citra not installed |
| Physical 3DS XL | PENDING Derek; console variant not yet supplied |
| Campaign | Not exercised |

## Remaining acceptance

Native expansion and original-engine compilation and full `make verify` passed.
The finalized owner-run `tools/stage_a.sh test` passed, including 9 adapter
tests, 95 builder tests (2 existing skips), and the strict source audit.
Engine-only release audit passed; all 17,513 pack entries passed CRC checks
and matched engine ABI `8efc02d7`. Private ZIP generation is the remaining
local packaging step. Generation attempted absent alternate-form paths, but
reported no missing linked asset symbols; this is not a full species audit.

Physical acceptance remains with Derek using `DEVICE_TESTS.md`. The custom
CIA forwarder identity and the final expansion player-ROM recipe are not
validated; use Homebrew Launcher and the private embedded build. Local
wireless remains outside this expansion milestone. An all-species/form/follower
inventory is later Stage E work.

Next task after build evidence: Derek's isolated console smoke test. Resolve
any baseline failures before active new gameplay changes; Stage B follows with
save-namespace/flag audit and saved run-configuration design, without reusing
flags 0x20–0x2C. No new run rules are present in Stage A.
