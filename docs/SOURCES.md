# Sources and attribution

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
Exalted Emerald and ahunter references. They were not imported, fetched for
reuse, or treated as this task's build baseline. Later code reuse must record
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
