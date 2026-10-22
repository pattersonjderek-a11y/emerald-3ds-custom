# Emerald 3DS Custom: reproducible builds

## Stage D (current `project/stage-d`)

Builds on visual-fix checkpoint `45d3796`; uses the same frozen SDK/image and
unchanged upstream.lock. All earlier build trees, branches, private ZIPs and
matching output metadata remain intact. `tools/stage_c_visuals.sh` now refuses
the D patch; use its historical branch to rebuild that package.

Actual commands in the existing SDK container (UID/GID 1000, `/project` bind):

```sh
docker --host=unix:///var/run/docker.sock exec emerald-visual-fixes bash -lc 'tools/stage_d.sh build'
docker --host=unix:///var/run/docker.sock exec emerald-visual-fixes bash -lc 'tools/stage_d.sh test'
docker --host=unix:///var/run/docker.sock exec emerald-visual-fixes bash -lc 'tools/stage_d.sh package'
```

`build` runs `python3 tools/bootstrap.py --upstream pokeemerald-expansion
--dir build/stage-d --make -j4 --python python3`; `test` runs full make verify,
9 enhancement adapters, 95 builder checks (2 existing skips), source audit.
The existing generated-asset cache was copied into a distinct D tree. Changed
native game/platform sources are compiled and linked; no baseline files are
hardlinked or edited. Required D symbols and actual linked trainer variants
are checked by make verify. SDK/host-tool versions remain recorded below.

Focused checks:

```sh
python3 3ds_port/tests/custom_difficulty_test.py --tree build/stage-d
python3 3ds_port/tests/custom_run_test.py --tree build/stage-d
python3 3ds_port/tests/custom_random_test.py --tree build/stage-d
python3 3ds_port/tests/visual_regressions_test.py --tree build/stage-d
python3 3ds_port/tests/custom_difficulty_data_test.py --tree build/stage-d \
  --gdb /opt/devkitpro/devkitARM/bin/arm-none-eabi-gdb \
  --output work/stage-d-trainer-audit.json
```

The first four execute production code in controlled host fixtures under
ASan/UBSan. The last reads the native linked-data image and validates 49 Hard
variants / 238 mons; it is neither emulator execution nor hardware testing.

```sh
python3 tools/regenerate_expansion_patch.py --tree build/stage-d \
  --add include/custom_difficulty.h src/custom_difficulty.c
# On a constrained workspace share pinned Git objects, never mutable build outputs:
git -C build/stage-d worktree add --detach ../../work/stage-d-clean \
  dfb0f84374230f4d462191601179b742f9f077df
python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir work/stage-d-clean
python3 3ds_port/tests/custom_difficulty_test.py --tree work/stage-d-clean
```

Create and bootstrap that worktree on the same side of the Docker bind mount;
host absolute `.git` paths do not resolve inside `/project`. Fresh source/host
reproduction is distinct from the native compilation in `build/stage-d`.
Engine changes are in the canonical 283-file patch; root platform/tests/tools
are copied by bootstrap. No dependency upgrade or source pin change.

Native outputs under `build/stage-d/3ds_port/`: `emerald3ds.3dsx`, `.smdh`,
`.elf`, `build/gamedata_image.elf`, engine-only `dist/Emerald3DS.3dsx` and
`.smdh`, private matching `build/emerald3ds.pak`. Private ZIP/manifest:
`work/stage-d-private/Emerald3DS-Custom-StageD-private.zip` / `manifest.json`.
Packaging reruns checks, checks every pack CRC and embedded ABI/namespace.
Only the separate engine-only audit ZIP may be considered for publication.
Stage D runtime state stays in `/3ds/emerald3ds-custom-stage-d/`.

Exact verified output sizes/hashes and packaged source checkpoint are in
[STAGE_D_BUILD_OUTPUTS.json](STAGE_D_BUILD_OUTPUTS.json). Package log:
`work/stage-d-package.log`; independent engine-only audit:
`work/stage-d-engine-audit.log`.

Historical workflows and tool installation instructions follow.

The product specification is the repository-root `PROJECT_BLUEPRINT.md`.
Do not reset to the blueprint's example clone or fetch newer engine code.
The initial clean `work` branch was `a30828a` (blueprint upload), directly
above candidate baseline `8ebb7355742ce43bbb10528044f9a175fc990a64`.
`upstream.lock` remains unchanged: expansion
`dfb0f84374230f4d462191601179b742f9f077df`, original engine
`76463dac15cad36aca5e2b3f6366abf9e53f814f`.

## Stage C visual fixes (current fix branch)

On `fix/stage-c-visuals`, use `tools/stage_c_visuals.sh build|test|package|versions`
in the same frozen SDK. This uses separate `build/stage-c-visuals` and
`work/stage-c-visuals-private` destinations. The original A/B/C trees, packages
and remote branches are preserved; baseline C is `aa0a291` and its ZIP/manifest
also reside in `work/baseline-stage-c-aa0a291/`. The original C wrapper refuses
this fix patch; check out `project/stage-c` to rebuild the baseline.

Commands actually used in this environment (container uses UID/GID 1000):

```sh
docker --host=unix:///var/run/docker.sock exec emerald-visual-fixes \
  bash -lc 'tools/stage_c_visuals.sh build'
docker --host=unix:///var/run/docker.sock exec emerald-visual-fixes \
  bash -lc 'tools/stage_c_visuals.sh test'
docker --host=unix:///var/run/docker.sock exec emerald-visual-fixes \
  bash -lc 'tools/stage_c_visuals.sh package'
```

The container mounts this repository at `/project`, uses `emerald-stage-a-sdk`,
and has the existing CA trust mount/settings for network fetches. Its default
working directory is `/project`. The starting engine build tree was copied
from C to retain expensive generated assets; changed sources are recompiled.
Fresh source/host patch reproduction is separately checked below; no claim of
an independent second full native compile is made.

Standalone new production regression check:
`python3 3ds_port/tests/visual_regressions_test.py --tree build/stage-c-visuals`.
Use `--case border|follower|battle` and `--port-source build/stage-c/3ds_port`
with `--tree build/stage-c` to reproduce the original assertion failures.
The test runs host ASan/UBSan with synthetic memory/GPU boundaries; it does not
render on hardware. `make verify` includes it as `verify-expansion-visuals`.

Engine patch workflow:

```sh
python3 tools/regenerate_expansion_patch.py --tree build/stage-c-visuals
python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir work/stage-c-visuals-clean
python3 3ds_port/tests/visual_regressions_test.py --tree work/stage-c-visuals-clean
```

On this disk-limited workspace the clean tree can first be made as a detached
Git worktree from the already fetched pinned engine, sharing Git objects; the
normal bootstrap still resets/applies the complete canonical patch and copies
overlays. No engine pin is changed. Preserve the source ownership/patch rules.

Native outputs are `build/stage-c-visuals/3ds_port/emerald3ds.3dsx`, `.smdh`,
`.elf`, engine-only `dist/Emerald3DS.3dsx` / `.smdh`, matching private
`build/emerald3ds.pak`. Private package:
`work/stage-c-visuals-private/Emerald3DS-Custom-StageC-VisualFixes-private.zip`.
Packaging runs `private_smoke_package.py --stage C --variant visual-fixes
--tree build/stage-c-visuals`, retaining C's namespace but writing a new ZIP.
Do not upload content-bearing outputs to source control or public CI.

This fix intentionally keeps `/3ds/emerald3ds-custom-stage-c/`, save layout,
algorithm/content rules and settings. Back up the existing C directory and
replace the embedded app/metadata only; no save import or reroll. See
DEVICE_TESTS.md for actual baseline device reports and pending fix acceptance.

## Stage C workflow (baseline project/stage-c)

A/B are preserved on `project/stage-a` / `project/stage-b`, with frozen private
packages and metadata. Stage B's final checkpoint is `ba750f8`. Use the exact
SDK below, without dependency upgrades, with a separate tree and runtime paths:

```sh
git switch project/stage-c
docker --host=unix:///var/run/docker.sock exec --user 1000:1000 emerald-stage-a \
  bash -lc 'cd /project && tools/stage_c.sh build && tools/stage_c.sh test && tools/stage_c.sh package'
```

The named container already exists in this workspace; on another laptop/host,
build `tools/stage_a.Dockerfile` as documented below and use `docker run --rm`
with the same bind mount/working directory/UID and `tools/stage_c.sh` commands.
`versions` records the unchanged SDK. Actual expanded commands inside it:

```sh
python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir build/stage-c --make -j4 --python python3
make -C build/stage-c/3ds_port verify PYTHON=python3
EMERALD3DS_EXPANSION_TREE="$PWD/build/stage-c" python3 -m unittest builder.tests.test_expansion_enhancements -v
EMERALD3DS_EXPANSION_TREE="$PWD/build/stage-c" python3 -m unittest discover -s builder/tests -v
python3 tools/release_audit.py --repo . --strict
make -C build/stage-c/3ds_port release pak PYTHON=python3
python3 tools/private_smoke_package.py --stage C
```

`make verify` now includes production core/resolver/trainer/starter/map-lookup
host fixtures (ASan/UBSan), the updated save/menu tests and a linked ARM-data
species/graphics audit. The latter uses SDK ARM GDB's built-in command language,
not GDB Python, and writes private `3ds_port/build/randomizer-pool.json` / `.csv`.
This is linked-data inspection, not emulation or a console run. Standalone:

```sh
python3 3ds_port/tests/custom_random_test.py --tree build/stage-c
python3 3ds_port/tests/custom_run_test.py --tree build/stage-c
python3 3ds_port/tests/custom_random_pool_test.py --tree build/stage-c \
  --gdb /opt/devkitpro/devkitARM/bin/arm-none-eabi-gdb \
  --output work/stage-c-pool.json
python3 tools/stage_c_seed_preview.py --tree build/stage-c \
  --pool build/stage-c/3ds_port/build/randomizer-pool.json --seed 42 --generations 0x100
```

The preview executes the real C core using metadata from the exact linked pool;
it is a host prediction to compare on the console. It is not hardware proof.

Native outputs: `build/stage-c/3ds_port/emerald3ds.3dsx` and `.smdh` (embedded),
`emerald3ds.elf` (debug), `dist/Emerald3DS.3dsx` and `.smdh` (engine-only),
matching private `build/emerald3ds.pak`. Private test ZIP/manifest:
`work/stage-c-private/Emerald3DS-Custom-StageC-private.zip` and `manifest.json`.
Never commit these content-bearing outputs or upload them to public CI/releases.
Runtime writes/read overrides are isolated under `/3ds/emerald3ds-custom-stage-c/`;
source and embedded-binary checks protect original/A/B namespaces. The existing
shared DSP input is read-only. Generic builder/install defaults and forwarders
are not validated for C: use the embedded private ZIP, no separate data pack.

Engine patch regeneration and source reproduction (new files must use --add):

```sh
python3 tools/regenerate_expansion_patch.py --tree build/stage-c
python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir work/stage-c-clean
python3 3ds_port/tests/custom_random_test.py --tree work/stage-c-clean
python3 3ds_port/tests/custom_run_test.py --tree work/stage-c-clean
```

The patch tool retains every existing engine path, reverse-checks it and updates
the local digest only after it matches. Compare all patched sources and canonical
overlays after fresh bootstrap. This proves source/host reproduction; the full
native build is performed in the separate Stage C tree. A/B wrappers now refuse
the wrong stage's patch so historical commands require the matching source branch.
All source pins and tool versions remain those below. Exact current results are
in STATUS.md; final artifact metadata is in STAGE_C_BUILD_OUTPUTS.json.

## Historical Stage B workflow (checkout project/stage-b)

Stage A remains frozen on remote `project/stage-a` and tag
`stage-a-verified-48d8096` at `48d809677b496b029415d1af2e6524c4a08714d8`.
Its actual native results/commands remain in `STAGE_A_STATUS.md`, original hashes
in `BUILD_OUTPUTS.json`, and separately preserved private package/manifest in
ignored `work/baseline-stage-a-48d8096/`. No device results have been supplied.
Use a separate branch/tree/package/SD directory for current Stage B work.

Reuse the exact SDK below; no dependency upgrades or donor merges:

```sh
git switch project/stage-b
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/project" -w /project emerald-stage-a-sdk \
  bash -lc 'tools/stage_b.sh build && tools/stage_b.sh test && tools/stage_b.sh package'
```

Equivalent commands inside that SDK (SDK paths exported by the wrapper):

```sh
python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir build/stage-b --make -j4 --python python3
make -C build/stage-b/3ds_port verify PYTHON=python3
EMERALD3DS_EXPANSION_TREE="$PWD/build/stage-b" python3 -m unittest builder.tests.test_expansion_enhancements -v
EMERALD3DS_EXPANSION_TREE="$PWD/build/stage-b" python3 -m unittest discover -s builder/tests -v
python3 tools/release_audit.py --repo . --strict
make -C build/stage-b/3ds_port release pak PYTHON=python3
python3 tools/private_smoke_package.py --stage B
```

The new `verify-custom-run` gate compiles production codec/menu/save adapters,
new-save initialization, Continue/save guards and sector/checksum/recovery
code on the host with ASan/UBSan. It is automatically included in `make verify`
only when the patched expansion run-config header exists. Standalone command:
`python3 3ds_port/tests/custom_run_test.py --tree build/stage-b`.
These are host tests, distinct from the native ARM build and device testing.

Native outputs are under `build/stage-b/3ds_port/`: `emerald3ds.3dsx`,
`emerald3ds.smdh`, engine-only `dist/Emerald3DS.3dsx`, and matching private
`build/emerald3ds.pak`. The audited embedded SD ZIP and manifest go only to
`work/stage-b-private/`, named `Emerald3DS-Custom-StageB-private.zip` and
`manifest.json`. Packaging checks the actual embedded ABI/index and all pack
entry CRCs, checks for the Stage B runtime path and absence of original/Stage A
paths, runs native-build validation plus host tests, and never overwrites the
Stage A ZIP. Do not upload content-bearing outputs to CI or GitHub.

Expansion runtime state is `/3ds/emerald3ds-custom-stage-b/`; original-engine
builds retain `/3ds/emerald3ds-custom/`. The embedded Stage B build needs no
separate data pack. Existing generic builder/install/dev-data defaults still
refer to the Stage A namespace: do not use them to install Stage B. Use its
private ZIP as directed in DEVICE_TESTS.md. Public engine-only packaging remains
subject to the existing release audit and is not a validated player-data recipe.

For source reproduction, regenerate the engine patch before bootstrapping:

```sh
python3 tools/regenerate_expansion_patch.py --tree build/stage-b
python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir work/stage-b-clean
python3 3ds_port/tests/custom_run_test.py --tree work/stage-b-clean
```

The patch tool retains all existing patch paths, including new map scripts and
mapjson sources that broad exclusion globs would lose. For future new engine
files pass each path with `--add`; canonical platform overlays/generated assets
must never enter that patch. Reverse-apply and fresh-bootstrap checks are
required. A fresh source/test bootstrap is not claimed as a second native build.
The full native build here was itself started from a fresh Stage B tree.

## SDK setup

Docker 28.4.0 with its local daemon was available. The Debian 13 host had
GCC 14.2, Make 4.4.1, Git 2.52, Python 3.12.14, Pillow 12.3, but no 3DS SDK
or libpng headers. Use the official SDK container, as existing CI does.
The first pull resolved `devkitpro/devkitarm:latest` to:

```
devkitpro/devkitarm@sha256:116afba8df8453961de2936ffab20dd441edf4d682856c1ec8b0e53d7ed0bbf5
```

Both CI and `tools/stage_a.Dockerfile` now use that immutable digest.
The Dockerfile pins direct host packages to the versions actually installed;
if a mirror removes them, setup fails visibly instead of silently upgrading.
Transitive apt packages still depend on that mirror: preserve the built SDK
image with `docker save` for a completely offline environment reproduction.
Do not run `pacman -Syu` as part of this baseline workflow.

Observed SDK: devkitARM r68-1; GCC 16.1.0-1; binutils 2.46.0-1;
newlib 4.6.0.20260123-5; libctru 2.7.0-1; Citro2D 1.7.0-1;
Citro3D 1.7.1-2; 3dstools 1.3.1-3; Picasso 2.7.2-3.
Container host tools: GCC 12.2.0, Make 4.3, Git 2.39.5, Python 3.11.2,
Pillow 9.4.0, libpng-dev 1.6.39-2+deb12u6.
`tools/stage_a.sh versions` prints the full package manifest; the observed
manifest is checked in as [TOOLCHAIN_PACKAGES.txt](TOOLCHAIN_PACKAGES.txt).

On Linux/WSL2 with Docker, from this repository:

```sh
docker build -f tools/stage_a.Dockerfile -t emerald-stage-a-sdk .
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/project" -w /project emerald-stage-a-sdk \
  bash -lc 'tools/stage_a.sh build && tools/stage_a.sh test'
```

On a managed cloud proxy, keep Docker's configured proxy defaults. Build with
`--secret id=proxy_ca,src="$CODEX_PROXY_CERT"` if necessary. The secret must be
a trusted CA bundle. Mount `/etc/ssl/certs/ca-certificates.crt` read-only at
`/run/host-ca.pem` for runtime fetches and pass `GIT_SSL_CAINFO`,
`SSL_CERT_FILE`, and `REQUESTS_CA_BUNDLE` pointing to that mount. Do not turn
off TLS verification. No devkitPro package-server access was needed because
the official image already contained the SDK.

Use a dedicated build tree per host/container. Our first host bootstrap
created tool executables requiring GLIBC 2.38/GLIBCXX 3.4.32; the Debian 12
container could not execute them. `make -C build/expansion clean-tools`
inside the container fixed this before rebuilding. That removes generated
tool executables, not engine source changes. Files produced as container root
may require a container to clean them up later.

## Commands

The wrapper exports SDK paths and executes the existing documented commands:

```sh
python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir build/expansion --make -j4 --python python3
make -C build/expansion/3ds_port verify PYTHON=python3
python3 -m unittest builder.tests.test_expansion_enhancements -v
python3 -m unittest discover -s builder/tests -v
python3 tools/release_audit.py --repo . --strict
```

`tools/stage_a.sh build` runs bootstrap/build; `tools/stage_a.sh test` runs
all checks above. `JOBS=1 tools/stage_a.sh build` is a serial diagnostic.
Bootstrap copies canonical `3ds_port/`, `tools/`, and `builder/` into the
engine tree. Inspect/protect engine edits before rerunning it: changing pins
or patch digests can reset that tree. Follow `AGENTS.md` for engine patch
regeneration, including new files and mapjson/map scripts. No engine patch
changes were required for the initial storage/build changes.

Reproduced clean-build defects fixed in canonical `3ds_port/full.mk`:

- GNU make expanded `$(file >build/port_art.mk,...)` before its recipe's
  `mkdir`, failing on a fresh build. A directory prerequisite now orders it.
- `leaves.bin` depended on an intro `.4bpp` file without a local rule;
  its rule now waits for the recursive root graphics generator.

Expansion voxel generation retains the baseline `--allow-art-mismatch` setting;
this build does not establish complete visual parity for every map/species.

Native builds emit existing upstream warnings. Do not treat a compile exit
as success: run the host/link/asset audits too. `make verify` includes the
production filesystem/save isolation test and settings/clock recovery checks.

## Private data and packaging

Development output: `build/expansion/3ds_port/emerald3ds.3dsx`, with embedded
game data. Its sibling `.smdh` is launcher metadata. These stay private.
For engine/data separation, from the same tree:

```sh
make -C build/expansion/3ds_port release pak PYTHON=python3
```

Outputs: `build/expansion/3ds_port/dist/Emerald3DS.3dsx`,
`dist/Emerald3DS.smdh`, and `build/emerald3ds.pak` underneath that port tree.
The pack and embedded RomFS must match this engine's `romfs/engine/abi.bin`.
Run `tools/stage_a.sh package` in the same SDK container after `test` passes.
It runs the release/pack targets and `tools/private_smoke_package.py`, which verifies
the generated ABI, nonempty asset index, and built executable before writing
a private ZIP under ignored `work/`. See `STATUS.md` for actual results.

No ROM, save, or firmware was obtained. Source builds use the pinned source
and existing asset generators. The ordinary English player-ROM input is
SHA-1 `f3ae088181bf583e55daf962a92bb46f4f1d07b7`, but this is not evidence
that the original public ROM-extraction recipe supplies all expansion data.
A custom validated player-data recipe/installer remains future work. Do not
use the original website, a stock release pack, or another fork's pack.
Only engine-only artifacts may enter public CI uploads after the strict
release audit. Never upload the private development build or `.pak` there.

CI remains a two-engine matrix. This task's native evidence is recorded
separately from emulator and console testing in `DEVICE_TESTS.md`.

The source publication auditor now stops if Git index access fails. A root-run
container without trust for the owner checkout previously fell back to scanning
ignored build trees and reported 140,571 unrelated findings. The owner-run
command passes; the deliberate untrusted-owner check now fails immediately
with an actionable message. Run the documented container as your host UID.

Stage A outputs and checksums are in [BUILD_OUTPUTS.json](BUILD_OUTPUTS.json);
Stage B outputs are in [STAGE_B_BUILD_OUTPUTS.json](STAGE_B_BUILD_OUTPUTS.json).
Hashes identify this run; embedded build paths and link IDs can change hashes
on a rebuild. Pair each engine with data from that same audited build.
