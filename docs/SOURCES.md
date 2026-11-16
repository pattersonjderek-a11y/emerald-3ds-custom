# Stage F original-XL boot/graphics repair

No pins, dependency versions, donor projects or art sources change. Native
compression routing is restored from this same pinned expansion's menu.c and
title_screen.c at dfb0f84374230f4d462191601179b742f9f077df, retaining all upstream
codec implementation/credits. Root platform changes provide padded external
inputs, constrained-heap cache policy, actual held-icon paths and readable fatal
messages. New host regressions reuse this native production codec and compare
local build inputs, rather than embedding game assets in tests or Git.

Derek's uploaded port.log and photographs are private diagnostic input, not
source instructions, assets or release content. Only non-content findings and
hash metadata are recorded. The new private repair ZIP is separate from frozen
E/F/InstallerFix files. Source and engine-only publication gates still exclude
ROMs, saves, firmware, generated game data and content-bearing applications.
Existing notices, expanded-content limitations and the unresolved public
retail-ROM-only recipe requirement remain applicable.

---

# Stage F release-validation follow-up (historical)

The native engine, expansion patch, v0.5.0 graphics pin and generated game pack
are unchanged from verified F. Changes are project Python installer/packaging
code and synthetic host tests; no new dependency, donor, asset or license source
is introduced. All seven native output hashes are checked when reusing them.
The updated campaign metadata reads the final existing linked image; no content
is replaced. Original private E/F artifacts remain frozen and separate.

---

# Stage F additions

Graphics remains Emerald 3DS v0.5.0 bcae4b70dac61419fc933084084469f6cfbe344b;
expansion remains dfb0f84374230f4d462191601179b742f9f077df. upstream.lock and
the frozen toolchain are unchanged. No donor merge or new art/audio asset source
was added. The 51 fixed Hoenn placements are original project metadata selecting
existing native expansion species; existing attribution/license notices apply.
The expanded species/cry/follower limitations in CONTENT_AUDIT.md still apply.

custom_package.py, custom_payload.py, campaign_audit.py and the portable installer
are project code reusing the upstream pack writer/reader and staging ABI. They
build a private local-source-data bundle with a hash-only recipe. They do not
establish a retail-ROM-only expansion extraction recipe or a right to publish
generated Pokémon content. No ROM, save or firmware was obtained or committed.
Source and engine-only publication audits remain separate from private test ZIPs.
The Stage E private Dropbox delivery is preserved and is not replaced by F work.

---

# Sources and attribution

## Stage D provenance

Stage D builds on this repository's `fix/stage-c-visuals` checkpoint `45d3796`.
Pins, SDK and existing Gen 1–9 assets are unchanged. New runtime difficulty and
host/data checks are project code. Native cap machinery, AI flag policies,
Difficulty: Hard trainer parser and existing trainer definitions are adapted
from the **same pinned expansion integration**, not donor merges. New Hard
`.party` entries derive from that integration's Normal bosses; preserve its
existing notices. No new art, ROM, save, firmware, game-data pack or embedded
application is committed. Historical attribution and component terms follow.

Stage A inspection: 21 October 2026 (America/Los_Angeles). No donor merge,
engine pin update, ROM, save, or firmware was used.

| Component | Exact source/revision | Purpose and changes | Terms / credits |
| --- | --- | --- | --- |
| Project checkout | https://github.com/pattersonjderek-a11y/emerald-3ds-custom at `a30828a` | Existing clean `work` branch; blueprint upload above baseline; history preserved | Preserve repository notices |
| Candidate integration | https://github.com/jmurth1234/pokeemerald-expansion-3Ds-dualscreen at `8ebb7355742ce43bbb10528044f9a175fc990a64` | Existing renderer, dual screen, visuals, QoL, expansion patch and tests; Stage A changes canonical platform paths/build ordering only | `LICENSE-PORT.md`, `NOTICE.md`, per-file notices; Zallax and contributors; upstream game material excluded from MIT scope |
| Expansion engine | https://github.com/rh-hideout/pokeemerald-expansion at `dfb0f84374230f4d462191601179b742f9f077df` | Existing expanded Gen 1–9 integration; fetched by bootstrap, existing `patches/pokeemerald-expansion/0001-port.patch`; no new engine edits | Preserve upstream credits and each asset's terms; no blanket relicensing or completeness claim |
| Original engine | https://github.com/pret/pokeemerald at `76463dac15cad36aca5e2b3f6366abf9e53f814f` | Existing alternate build recipe, unchanged pin | Upstream does not state a general license; game rights remain with their owners |
| Official SDK | https://github.com/devkitPro ; Docker Hub `devkitpro/devkitarm@sha256:116afba8df8453961de2936ffab20dd441edf4d682856c1ec8b0e53d7ed0bbf5` | Existing CI toolchain now frozen; versions in `BUILD.md` and private manifest | GCC/newlib respective terms; libctru/Citro2D/Citro3D zlib; MPL 2.0 for derived linker script |
| Python / Pillow | Python 3.11.2 / Pillow 9.4.0 inside SDK | Existing build/generator dependencies, no vendoring | PSF / MIT-CMU and HPND; preserve component terms |

Other inherited sources are detailed in `NOTICE.md` and
`3ds_port/src/voxel/NOTICE.md`, including gradenGnostic's MIT voxel renderer
at `db1cab3d2dc9f0e0a9f4a3d67983e5acf30a9a46`, the devkitARM linker script,
and Nintendo/Game Freak/Creatures content. Existing follower-fetch source
pins and hashes remain in `builder/emerald3ds_builder/followers_sources.py`.
Do not interpret those notices as granting distribution rights to generated
content. The expansion's own follower substitutions and missing art must be
audited before claiming every species has exact follower artwork.

The blueprint lists original-port, newer-expansion, Tertu, Modern Emerald,
Exalted Emerald and ahunter references. During Stage A they were not imported, fetched for
reuse, or treated as its build baseline. Later code reuse must record
exact paths, authors, terms and modifications here before integration.

The source-ROM SHA-1 in `upstream.lock` is an input identifier, not a ROM
included in this repository. Public source and engine-only packages and
private content-bearing build outputs are separate products.

Stage A implementation is committed locally as
`c73ea2a28e7050be1f31dfd63fa478fe4cc9e5ae`. Final artifact metadata and
hardware-pending records are subsequent documentation only. The SDK/package
manifest and output hashes are in `TOOLCHAIN_PACKAGES.txt` and
`BUILD_OUTPUTS.json`; content-bearing artifacts remain outside source control.

Stage B builds on the preserved Stage A checkpoint `48d8096`, now synced to
remote branch `project/stage-a` and tag `stage-a-verified-48d8096`. All engine
and SDK pins remain unchanged. The run-record codec, setup state machine,
native UI/save adapters, synthetic host fixtures and workflow additions are
new project code written for this stage; no donor files or algorithms were
imported. Engine additions and modifications are captured in the existing
canonical expansion patch (including six new engine files). Existing notices,
credits, generated asset pipeline and source-ownership rules remain applicable.
Schema/content-rules provenance is documented in SAVE_FORMAT.md. Private
Stage B output remains under ignored build/work paths, never source history.

## Stage C provenance

Stage C starts from `ba750f84b9d361e730ec03e54da0d2ee1893e973` on a separate
`project/stage-c` branch. `upstream.lock`, SDK image and inherited asset sources
remain unchanged. No donor branch was merged and no assets were added.

Inspected the pinned Tertu reference
https://github.com/Zetraphes/pokeemerald-expansion at
`1ad60617c8c17da5e6d380371cfa9429ce9b9a4e`, specifically `src/randomizer.c`,
`include/randomizer.h`, `include/config/randomizer.h` and `CREDITS.md`.
Purpose: compare runtime resolver boundaries, starter distinctness and wild/trainer
identities against the current engine. Its older flags 0x20–0x26 and trainer-ID
seed assumptions were not adopted. No Tertu source text or art was copied;
the numeric core, validation, save/UI integration and native adapters are new
project implementation against the existing pinned expansion interfaces. Public
source visibility was not treated as a reuse license. Original credits/reuse
terms remain with that donor; no relicensing claim is made. The inspection checkout
and notes stay in ignored `work/donor-tertu*`, outside source/build inputs.

New engine files: `include/custom_random_core.h`, `src/custom_random_core.c`,
`include/custom_random.h`, `src/custom_random.c`, all captured in the canonical
expansion patch. Modified native starter/wild/trainer/pool/menu adapters reuse
this repository's existing expansion code and retain its notices. New root host
fixtures and linked-pool/seed-preview tooling contain synthetic state or metadata,
not copied game-content packages. Normal/shiny art, learnsets and form/item tables
remain inherited generated inputs; the pool audit does not grant distribution rights.

Stage C algorithm/content-rules provenance and exclusions: RULES.md and
SAVE_FORMAT.md. Optional difficulty/ability/item stages were not imported from
Modern/Exalted/ahunter references. Renderer, visual effects, follower systems and
native expanded Gen 1–9 content remain the existing integration.

## Stage C visual fixes

The follow-up starts at `aa0a291` on `fix/stage-c-visuals`, retaining all engine,
SDK and asset pins. The border format is the pinned engine's existing
Hoenn/FRLG distinction (`GetBorderBlockAt`, mapjson output); no donor import.
Compression/blank-frame handling and scenic scheduling fixes plus their host
fixtures are new project code applied to existing integration paths. Torchic's
six-frame sheet and palettes were inspected in the actual linked asset index;
no sprite/art was downloaded, replaced or added. Full follower coverage remains
a later audit. Original C source/build/package and Dropbox file remain preserved.


## Requested v0.5.0 refresh: inspection only

Inspected on 13 November 2026 (America/Los_Angeles):
[ZallaxDev/emerald-3ds v0.5.0](https://github.com/ZallaxDev/emerald-3ds/releases/tag/v0.5.0),
tag object `1561e874dc5ef7922b5e2758c73a282f31e8ae89`, commit
`bcae4b70dac61419fc933084084469f6cfbe344b`. Current main resolves to that
same commit. The expansion integration main remains the candidate
`8ebb7355742ce43bbb10528044f9a175fc990a64`.

[UPSTREAM_REFRESH.json](UPSTREAM_REFRESH.json) records complete path/blob
metadata relative to the blueprint original-port reference and saved custom D.
Inspected upstream randomizer documentation/header, Makefiles, bridge,
compatibility, settings/data runtime, source lock, release notes and notices.
No v0.5.0 source/art has been imported; execution failure blocks integration.

Upstream changed the terms for its original port contributions from v0.5.0 to
CC BY-NC-SA 4.0 (`LICENSE-PORT.md`), crediting “Emerald 3DS by Zallax and
contributors”. Earlier published MIT copies and separately licensed third-party
code retain their notices. Record exact imported paths, credits, terms and
modifications when integration is actually performed; this inspection does
not relicense existing project or game material. The current lock and existing
notices remain unchanged. See [UPSTREAM_REFRESH.md](UPSTREAM_REFRESH.md) for
source findings, version differences and the unverified local Stage E handoff.


## Stage E + v0.5.0 source integration (13 November 2026)

User-authorized precedence: original Emerald 3DS v0.5.0 features override any
clashing implemented/planned custom features, now and in future work. Source:
https://github.com/ZallaxDev/emerald-3ds at
`bcae4b70dac61419fc933084084469f6cfbe344b` (tag v0.5.0).
Full upstream history is merged; platform/build/builder/tools/art authored for
the port are reused with their notices. Native expansion APIs, compression,
font/palette paths, IDs and isolated runtime storage are adapted. Its own
species randomizer is retained and its National Dex range is extended to
Gen 1–9 through the existing expansion converters. Optional E ability/item
resolvers and host fixtures are new project work. No donor engine merge,
ROM, save or firmware. The pinned expansion data remains the same integration.

`LICENSE-PORT.md` and `NOTICE.md` now preserve upstream v0.5.0's CC BY-NC-SA 4.0
terms and attribution to **Emerald 3DS by Zallax and contributors**, including
the credited UI, renderer, model, builder and randomizer contributors in the
upstream changelog. New modified port contributions follow those terms;
previous published MIT versions retain their original licence. Separately
licensed components and game material retain their own notices/rights.
No missing follower artwork was downloaded or represented as complete art.

Engine platform hooks adapted from the same upstream revision are captured in
`patches/pokeemerald-expansion/0001-port.patch`; native battle/species/save
formats and expansion-specific gameplay interfaces are retained. Current
integration limitations and actual validation state are in STATUS.md.

## Stage E follow-through — 14 November 2026

Native API/compression/enum adapters reconcile the full graphics v0.5.0 merge
with the unchanged expansion pin. New optional resolvers, palette/context
regressions, fresh-source guards and audit tools are project implementation.
No donor engine merge or new external asset download was performed. All
species/follower pointers reported by the content audit come from the pinned
expansion source and generated asset index; shared/fallback art is not claimed
as new or complete artwork. Preserve the upstream CC BY-NC-SA/MIT notices and
component credits. The earlier upstream-refresh audit is historical; Derek
subsequently authorized rebuilding from the preserved D source and explicit
v0.5.0 precedence. Python/Pillow generator versions were updated explicitly;
the ARM SDK and engine pins were retained.
