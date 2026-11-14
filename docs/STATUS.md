# Stage E + Emerald 3DS v0.5.0 (implementation in progress)

Branch: `project/stage-e-v050`, based on saved Stage D `b2e8116` plus the
upstream audit checkpoint. Derek explicitly requested rebuilding from D and
making v0.5.0 authoritative over clashing implemented/planned/future features.
The previous local E implementation and build artifacts were absent in the
restored workspace; E is being implemented again. Historical D evidence is in
[STAGE_D_STATUS.md](STAGE_D_STATUS.md). Historical packages are not present on
this restored machine and cannot be claimed hash-verified here.

The full upstream source/history at `bcae4b70dac61419fc933084084469f6cfbe344b`
(v0.5.0) is merged. Its menus, renderer, editable global core randomizer and
Nuzlocke tracker win feature conflicts. Existing expansion engine pins/data
remain. Expansion C/API/graphics/save adapters are being reconciled with the
new platform. Upstream's species permutation is extended to the 1,025 National
Dex range with native ID converters; its SplitMix64/Fisher-Yates policy,
editable global settings and 31-bit seed remain authoritative. Prior custom
per-area/per-trainer core rules and generation/BST filters are superseded.

New E code: independent ability/field/held domains, conservative native ability
and item pools, form/progression protections, actual native ability accessors,
field/hidden item acquisition hooks and wild/trainer held-item hooks. Optional
choices are appended to the upstream randomizer page and default OFF. Native
follower bounds, palette identity and allocation safety fixes are included.
New runtime namespace: `/3ds/emerald3ds-custom-stage-e-v050/`; no save import.

Host production optional-rule and follower-palette suites pass ASan/UBSan
(`work/optional-host.log`, `work/follower-host.log`). **Native compilation is
not complete**: iterative builds are resolving original-engine versus expansion
API differences. Logs are `work/native-build*.log`. No emulator/device result
and no new SD package are claimed. Original-XL hardware acceptance remains
pending for Derek. Source checkpoints during development are not releases.

The ARM SDK image is unchanged. The rebuild now separately uses upstream's
Python 3.13.17/Pillow 12.3.0 generator environment (`tools/stage_e.Dockerfile`).
Build setup succeeded; SDK logs are `work/sdk-build.log`, `work/sdk-e-build.log`.
All engine changes are captured in the canonical expansion patch (currently
310 paths), reverse-checked. Fresh bootstrap/full regression/native/output
checks, roster/follower audit, final documentation, private packaging and source
sync remain finish work. No ROM/save/firmware/generated game-data artifact is
committed. See SOURCES.md and the amended blueprint for precedence/provenance.

## 14 November checkpoint (not a release)

Production configuration/sector recovery, difficulty/factory composition,
optional rules, follower palette/bounds and 1,025-entry upstream randomizer host
checks pass under ASan/UBSan. Native compilation reached final linking; API
reconciliation continues (logs through work/native-build-35.log). No playable
Stage E artifact or hardware result is claimed at this checkpoint. Canonical
expansion patch includes the engine fixes; new platform adapters are tracked.
The v0.5.0 physical/special split switch now drives the native category accessor.
Next: finish native output, complete linked content/follower inventory, fresh
bootstrap and regression checks, then prepare a separate private test package.
