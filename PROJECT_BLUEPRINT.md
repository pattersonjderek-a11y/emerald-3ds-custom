# Emerald 3DS Custom — development blueprint and Codex handoff

Prepared for Derek • 21 October 2026 • Initial specification, not a playable release

## 1. Decision and how to use this document

Build a native Nintendo 3DS homebrew game based on **Emerald 3DS with pokeemerald-expansion**, retaining Hoenn's adventure. Preserve its pixel-art presentation, optional voxel scenery, tilt-shift blur, richer colors, lighting, particles, dual-screen interface, and existing quality-of-life settings. Add an optional, customizable in-game randomizer and difficulty controls. Keep Pokémon followers and audit their expanded-species coverage.

This is suitable work for Codex in a persistent Git repository with a working native build environment. It is a sequence of engineering tasks, not a one-prompt conversion or a stack of ROM patches. Codex can implement, compile, investigate failures, and run automated checks; Derek must test the actual 3DS. A working demo is not proof of complete campaign stability.

**To start:** save this document in the project as `docs/PROJECT_BLUEPRINT.md`, give Codex repository access, and paste the first-task prompt in section 12. If starting without a repository, provide this document and the candidate repository URL; have Codex prepare a local checkout first. Remote creation/publishing is a separate action. No API integration belongs inside the game.

The first deliverable is **a reproducible expanded native build and a device smoke-test package**, not every requested feature at once. After that, use section 13 to continue one milestone at a time.

## 2. Player-facing requirements

### Required product behavior

| Area | Requirement |
| --- | --- |
| Platform | Native ARM11 `.3dsx` application, launched through Homebrew Launcher on a modded 3DS XL. Identify original XL versus New XL before choosing performance defaults. |
| Campaign | Retain Emerald's Hoenn story, maps, progression, and major battles. No Johto conversion. |
| Visuals | Preserve the existing Emerald 3DS renderer and its available 2D/voxel, camera, blur, color, lighting, and atmosphere behavior. Do not promise new 3D modeling for unfinished areas. |
| Pokémon | Gen 1–9 eligible species, including supported Scarlet/Violet DLC species, available to the expanded game/randomizer. Generate an inventory of actual data and assets; do not equate enabled species with complete implementation. |
| Followers | Optional lead-Pokémon follower in 2D and voxel scenes. Audit each eligible species' art and behavior; report fallbacks explicitly. |
| Standard mode | Randomization off; fixed encounters and trainer teams. Existing port/expansion QoL features remain available. This means an expanded fixed campaign, not bit-identical cartridge mechanics. |
| Randomized mode | New-game setup defaults to random starters, wild Pokémon, and enemy trainer Pokémon. Each category is independently configurable in Custom. |
| Optional randomization | Separate switches for abilities, field/hidden items, and held items. Abilities and items default off. |
| Difficulty | Independent of randomization: Normal, Hard, and Custom presets, with explicit rules. A randomized run need not be hard; a fixed run can be hard. |
| Persistence | Confirm rules once before play. Seed, algorithm version, options, and difficulty survive save/load, restart, and Continue. New Game creates new run state. |
| Main purpose | Surprise and replayability, particularly Gym Leaders and Elite Four. Catching every species in every seed is not a requirement. |

### Proposed new-game sequence

1. New Game → Standard or Randomized.
2. Choose Normal, Hard, or Custom difficulty.
3. In Randomized, accept the core preset or edit categories, eligible generations, and optional balance restrictions.
4. Generate a seed, or enter a numeric seed.
5. Show a readable summary → Confirm → continue the normal introduction.

Resolve the precise introduction hook from source. Keep proposed options in temporary memory until the game's new-save initialization has run; then commit them exactly once. Cancelling setup must not alter an existing save. After starting, gameplay rules are read-only for that run in the first release; graphical and convenience settings remain adjustable. A read-only Run Settings page shows seed and rules without exposing randomized boss rosters.

Use controller buttons for every setup function; touchscreen support is an enhancement to the same actions. Do not build a separate web app or desktop randomizer instead of this in-game flow.

## 3. Repositories and what to reuse

These sources were investigated on 21 October 2026. Freeze a known revision for the first build; inspect newer upstream changes separately rather than silently upgrading the engine mid-integration.

| Source | Role | What to take / limitation |
| --- | --- | --- |
| [jmurth1234/pokeemerald-expansion-3Ds-dualscreen](https://github.com/jmurth1234/pokeemerald-expansion-3Ds-dualscreen) | **Candidate project base** | Existing alternate expansion target, shared 3DS renderer, gameplay adapters, tests, and build notes. Still needs reproduced native compilation and physical-console acceptance. |
| [ZallaxDev/emerald-3ds](https://github.com/ZallaxDev/emerald-3ds) | Original graphics/platform upstream | Rendering, audio, touch UI, visual reference, upstream fixes. Its public web builder does not automatically build our custom game. |
| [rh-hideout/pokeemerald-expansion](https://github.com/rh-hideout/pokeemerald-expansion) | Pokémon/battle engine | Later-generation data, mechanics, follower infrastructure, advanced AI, level-cap machinery, and difficulty-dependent trainer variants. Use the candidate fork's pinned engine initially. |
| [Zetraphes/pokeemerald-expansion — tertu-randomizer](https://github.com/Zetraphes/pokeemerald-expansion/tree/tertu-randomizer) | Runtime randomizer donor | Seeded species/item/ability resolvers and starter/wild/trainer hook examples. Based on an older expansion version; selectively adapt interfaces, not the entire branch. |
| [Modern Emerald — resetes12/pokeemerald](https://github.com/resetes12/pokeemerald) | Difficulty/menu design reference | Documents Easy/Normal/Hard, caps, EXP, battle-item restrictions, IV/EV controls, and modular randomizer setup. README examined; code-level compatibility is not yet established. |
| [Exalted Emerald — segabl/exalted-emerald](https://github.com/segabl/exalted-emerald) | Alternative difficulty reference | Documents difficulty, stronger AI, scaled levels, and optional randomizer. Inspect only useful pieces; do not import the entire campaign. |
| [ahunter86/pokemon-emerald-romhack](https://github.com/ahunter86/pokemon-emerald-romhack) | Secondary randomizer examples | Per-save seeds, rival continuity, per-location items, level caps. Its fresh-per-encounter wild behavior, unchanged trainer movesets, and always-on challenge choices are not our default design. |

### Revisions to record

Candidate base: `8ebb7355742ce43bbb10528044f9a175fc990a64`.

Its `upstream.lock` pins expansion to **`dfb0f84374230f4d462191601179b742f9f077df`**. This is the engine revision for initial integration. The separately inspected newer expansion checkout below is reference material, not a replacement pin.

| Reference | Revision inspected / resolved |
| --- | --- |
| Original Emerald 3DS | `b198c08defb94081ae995796cf75ab8cdb51f2d0` |
| Separate expansion reference | `f4dc700a130330fd2f9325a17bbb1e2d91dbf091` |
| Tertu randomizer branch | `1ad60617c8c17da5e6d380371cfa9429ce9b9a4e` |
| ahunter randomizer | `30731dd401fc142188fe694e2b1f6d06a3d09fc1` |
| Modern Emerald default branch | `37e437f1a80e5ccd3ba50933e5f113344c5db64e` — README-level assessment |
| Exalted Emerald default branch | `b459df3f31b13df83a3baa78413145c302ed122d` — README-level assessment |

For any reused code/art, record the source URL, exact revision/path, author/credits, license or reuse terms, purpose, and modifications in `docs/SOURCES.md`. Public source availability is not itself a blanket reuse license. Preserve the original port's MIT notice and each component's separate terms. Prefer existing compatible engine mechanisms over bringing in another implementation of the same feature.

## 4. What is proven, and what remains unproven

Previous investigation successfully assembled the candidate fork's pinned expansion tree and applied its patch. Nine expansion gameplay-adapter tests and eight additional host regression suites passed. Four sanitizer suites required leak detection disabled because this environment could not support LeakSanitizer; address/undefined-behavior checks remained enabled.

This blueprint does **not** claim a native build, emulator boot, device frame rate, installer readiness, or completed playthrough. The earlier environment lacked the 3DS toolchain. Re-run checks in the actual project environment; historical passing results are not a substitute for current results.

The candidate's `docs/EXPANSION_FEATURES.md` documents shared settings wired to native expansion systems. It explicitly says follower species without art use a substitute fallback. Its native expansion physical/special split is always on, rather than a reversible vanilla-style toggle. The original port's local-wireless adapter is not enabled for the alternate expansion engine. Multiplayer is outside the initial milestone scope.

Full Gen 1–9 support must be broken into separate audit fields: species/stats/types, front/back graphics, icons, shiny palettes, cries, learnsets, evolution/form rules, ability/move implementation, and follower art. Report gaps instead of calling every asset complete. Optional battle gimmicks beyond those already working in the fork are not automatically part of this project.

## 5. Where and how to build

### Recommended working arrangement

Keep the project in a dedicated Git repository derived from the candidate base. Use Codex with access to that checkout and a **Linux build environment**. A cloud environment is a good first choice if local installation is inconvenient: configure the repository, toolchain, dependency downloads, and persistent instructions there. A local Linux machine or Windows WSL2 with the same SDK is a valid alternative and useful for emulator work. macOS can use the SDK with host-specific setup if preferred.

Codex needs more than read-only GitHub browsing: it needs a terminal, editable files, compilers, permitted package/source downloads, and enough task persistence to continue the same repository. Configure exact dependency hosts if the environment restricts networking. Typical needs include GitHub/raw asset hosts, the selected Linux package mirror, Python packages, and devkitPro package servers. Determine actual destinations from documented installs and download logs; do not weaken unrelated machine policy.

The candidate already has a GitHub Actions build matrix using `devkitpro/devkitarm:latest`. Reuse that workflow as the initial reference, then record installed package versions and pin a tested container digest or package manifest for repeatability. Do not assume the default Codex environment includes this specialist SDK, or that Docker is available inside every cloud task. Install the official SDK in the environment when a container is unavailable. A host-only test environment is useful but cannot satisfy the native-build gate.

### Required tools

- devkitPro/devkitARM, libctru, Citro2D, Citro3D, 3dstools, and the Picasso shader assembler.
- Native C/C++ compiler, Make, Git, and libpng development support.
- Python 3.11 or newer and Pillow.
- Optional: a supported 3DS emulator such as Azahar for diagnosis. An emulator is not required to compile and cannot replace console testing.
- An SD-card transfer method and Homebrew Launcher on Derek's console. Follow the port's documented DSP/audio setup; do not bundle device firmware in the repository.

Use the current official devkitPro installation instructions rather than an invented apt package for Citro3D. The port documents `pacman -S --needed libctru citro2d citro3d 3dstools` **inside an already configured devkitPro package environment**. That line alone does not install/configure the entire toolchain.

### Initial build commands

These commands reflect the candidate's documented interface. They have not been executed as a native build during this blueprint task. Use a clean project directory; if a checkout already exists, inspect its branch and worktree rather than overwriting it.

```sh
git clone https://github.com/jmurth1234/pokeemerald-expansion-3Ds-dualscreen.git emerald-3ds-custom
cd emerald-3ds-custom
git switch -c project/start 8ebb7355742ce43bbb10528044f9a175fc990a64

# After installing/configuring the toolchain:
python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir build/expansion --make -j4 --python python3
make -C build/expansion/3ds_port verify PYTHON=python3
python3 -m unittest builder.tests.test_expansion_enhancements -v
```

Expected development application: `build/expansion/3ds_port/emerald3ds.3dsx`. It embeds development data and is for private testing. The engine-only release path is different:

```sh
make -C build/expansion/3ds_port release PYTHON=python3
make -C build/expansion/3ds_port pak PYTHON=python3
```

The documented outputs are `dist/Emerald3DS.3dsx` and `build/emerald3ds.pak` underneath that `3ds_port` build directory. Verify actual output paths, sizes, assets, and matching engine/data ABI. Never pair a custom engine with an unrelated pack downloaded from another release.

The end-user builder uses the player's supported Emerald dump; the locked English source-ROM SHA-1 is `f3ae088181bf583e55daf962a92bb46f4f1d07b7`. Check the custom recipe and later asset sources before claiming that a clean base ROM is sufficient for our complete final installer. Source-build outputs and the end-user ROM-extraction recipe are distinct paths. Investigate packaging rather than assuming the original website can generate this fork.

### Source ownership: a critical detail

The repository's canonical platform files are `3ds_port/`, `tools/`, and `builder/`. Bootstrap copies them into generated build trees. Edit those canonical platform files, then sync the changed files to the build tree or bootstrap safely.

Game-engine edits are developed in `build/expansion/` and must be captured into `patches/pokeemerald-expansion/0001-port.patch`, following the candidate's **AGENTS.md**. Keep new game-side files when regenerating that patch; ordinary `git diff` omits untracked additions. Verify clean apply and reverse apply. A fresh bootstrap must reproduce the change. Never leave the only implementation in an ignored/generated directory.

Bootstrap may reset the generated game tree when pins or patch digests change. Preserve game-side edits before rerunning it; do not reset a dirty tree blindly. Shared-header changes may require deleting affected object files because game translation units lack header-dependency tracking. The AGENTS.md also documents a parallel asset-generation race: inspect the asset map and diagnose serial regeneration if necessary; never ship an empty asset table.

## 6. Architecture and save design

Implement one central run-configuration service shared by menu, gameplay hooks, and diagnostics. Proposed modules below are responsibilities, not claims that matching files already exist:

| Responsibility | Boundary |
| --- | --- |
| Run configuration | Mode, seed, option bits, species filters, difficulty rules, configuration/algorithm versions, and content-rules identifier. |
| Save integration | Validated serialization, initialization/migration, active-save binding, backup/error handling, and read-only access during play. |
| Randomizer | Pure deterministic resolvers for starters, encounter slots, trainers, abilities, and eligible items. |
| Difficulty | Caps, trainer variants/AI, battle-item rules, EXP policy. Separate from randomizer selection. |
| Setup UI | Temporary choices, confirmation, Run Settings display, and clear explanations. |
| Content audit | Valid species/form/ability/item pools, asset coverage, fixed-mode placement, and protected progression cases. |

Use a saved 32-bit seed initially if it fits the adapted implementation, but do not rely on trainer ID alone. Record a stable algorithm version and rules identifier. Reproduction means **same seed + same options + same algorithm/content rules**, not seed alone across arbitrary future releases. Avoid dependence on the global battle RNG, frame timing, process addresses, host-language randomized hashes, or the order menus happen to open.

Derive independent streams or keys for starter slots, wild slots, trainers, abilities, and items. Turning item randomization on must not unexpectedly regenerate all trainer teams. Trainer keys should include trainer ID and party slot; encounter keys include map, method, and slot. Use unbiased bounded selection and finite fallback rules.

**Save-storage conflict already found:** the older Tertu defaults use flags `0x20–0x26`; the candidate uses `0x20` for expansion EXP Share and `0x21–0x2B` for Mega rewards. Do not copy those assignments. Audit event flags, variables, save structures, checksums, and serializers before allocating storage. Record reservations centrally.

Prefer storing critical run state in the same validated save transaction as game progress. If a sidecar is necessary, bind it to the exact save/run identity, version it, write atomically with recovery, and define failure behavior. A missing randomizer sidecar must not silently turn an existing randomized save into Standard or generate a new seed. Keep new-game settings out of the port's global visual-settings file: copying another SD card's display preferences must not change a run.

Initial compatibility policy: separate installation/save namespace; new saves recommended. Do not claim transparent compatibility with vanilla Emerald, another expansion hack, or previous custom save layouts without explicit migration tests. Never modify Derek's existing save in place during development.

## 7. Randomizer behavior and balancing

### First playable randomizer

| Category | Required rules |
| --- | --- |
| Starters | Three valid distinct choices; displayed name/sprite matches received species. Each has a usable damaging move. Rival relationship is coherent and persists through rematches. |
| Wild | Default to seeded per-area/per-method/per-slot replacements. Repeated encounters can use normal slot selection, but tables survive reload. All eligible generations can participate; no per-seed complete-Dex guarantee. |
| Trainers | Seeded party substitutions, including major bosses. Preserve intended levels and party size initially; generate usable species-appropriate moves instead of blindly inheriting the original species' moves. |
| Species/forms | Exclude empty IDs, eggs, disabled species, invalid/battle-only forms, and unsupported forms. Deliberately handle regional forms and any form with item/ability dependencies. |
| Visible encounters | Resolve identity before displaying the overworld Pokémon; preserve species, form, and shiny identity into the battle. Avoid double randomization. |
| Protected encounters | Explicit exceptions for tutorials, scripted partners, and special battle logic until supported. Document each exception. Most Gym/Elite Four teams must not remain protected merely for convenience. |

Default core species selection is unrestricted among valid eligible species. Provide optional similar-strength and legendary restrictions as Custom settings, not hidden rules. Fresh-per-encounter wild rerolls can be a later optional mode; do not import that donor behavior accidentally. Derek's main requirement is unpredictability, particularly boss opponents, not collection coverage.

Difficulty and randomization must compose in a defined order: choose difficulty's trainer template and levels/party size → select randomized species → generate valid moves/items/ability → validate special battle requirements. Hard mode must not restore fixed boss species after randomization. Same trainer/seed/rules must not reroll because the player resets before a battle.

### Optional abilities and items

Abilities should initially map consistently per species and ability slot within a run. Audit the battle engine, summary, AI, field effects, and direct species-table reads. Handle form-changing/signature abilities and severe balance exceptions explicitly; a battle-only accessor is insufficient.

Field and hidden items use location-aware keys. Protect key items, HMs, and mandatory progression rewards. Held items use their own pool and switch. Signature items, Mega Stones, form items, and battle-gimmick dependencies need compatibility rules when the species changes. Shops, moves, types, base stats, evolution randomization, and link trading are not initial requirements.

## 8. Difficulty implementation

Use native expansion infrastructure first:

- `include/config/caps.h`: hard/soft EXP caps and cap progression mechanisms.
- `include/config/battle.h`: `B_VAR_DIFFICULTY` and the documented initialization requirement for `Script_SetDifficulty`.
- `include/constants/battle_ai.h` and native AI code: trainer decision policies and switching.

These hooks are not a complete finished difficulty menu. Some switches are compile-time macros; implementing per-save choices may require runtime adapters. Do not merely display options that gameplay never reads.

Proposed presets are design defaults, not already-implemented behavior:

| Rule | Normal | Hard | Custom |
| --- | --- | --- | --- |
| Level caps | Off | Gym/League progression cap | Off / soft / hard |
| Battle style | Player choice | Set | Choice |
| Bag healing/X-items in trainer battles | Allowed | Restricted | Configurable |
| Trainer AI | Native baseline | More capable policy | Selectable |
| Major boss preparation | Existing fixed template | Better moves/items/team composition | Defined options |
| EXP | Existing behavior | Normal rate initially; no artificial grind penalty | Optional multiplier later |

Keep ball throwing, mandatory tutorials, and required scripted actions functional when restricting battle items. Do not apply unrestricted omniscient AI just because the engine's SMART preset includes it: inspect flags and select a policy intentionally. Start with clear move evaluation and sensible switching. Cap values must be a documented progression table, with explicit Elite Four/Champion behavior and tests for rematches/postgame.

Use Modern Emerald and Exalted Emerald as targeted references for menus and policy. Their documentation supports feasibility; it does not prove a clean merge into this native port. Balance through actual battles, including randomized teams, rather than simply raising every opponent's level.

## 9. Followers and visual acceptance

Retain the expansion's native follower system and the port's existing toggle. Do not layer a second follower implementation on top. Build an audit listing valid overworld sprite/frame/palette mappings for every eligible species and form. Mark exact art, deliberate shared art, fallback, and missing separately. Substitute sprites can keep an early build functional but do not satisfy the final all-species-art claim.

Test followers at doors, map connections, stairs, elevation changes, interiors, surfing, biking, party reorder, fainted lead/egg handling, save/reload, and battle transitions. Check both 2D and voxel modes. Restrict map contexts according to existing engine behavior before expanding them.

Preserve current colors, tilt-shift, bloom, lighting, motes, and camera options. Avoid renderer rewrites while stabilizing gameplay. Measure actual frame pacing and memory on the exact console model in busy towns, routes, interiors, battle transitions, and follower scenes. Establish the baseline first; report subsequent regressions numerically and provide lower-cost settings when required. Do not promise stereoscopic performance on an unidentified original versus New XL.

## 10. Milestones and acceptance evidence

| Stage | Work | Exit evidence |
| --- | --- | --- |
| A — Baseline | Pin sources, configure SDK, reproduce native expansion build, run supplied checks, audit outputs and install paths. | Exact commands/tool versions, checksums, passing checks or precise blockers, private smoke package, device checklist. No new gameplay features yet. |
| B — Run settings | Save allocation, schema/version, initialization, Standard/Randomized choice, seed entry, difficulty selection, Run Settings page. | Cancel does not overwrite; save/restart round trip; Standard identity behavior; rejected unknown/corrupt config; no reserved-flag overlap. |
| C — Core randomizer | Starters, wild, trainers, pool validation, visible encounters, rival handling, and representative boss/double battles. | Same seed/rules reproduce, different seeds vary, no invalid forms/empty pools, names/sprites/battles match, movesets valid. |
| D — Difficulty | Normal/Hard/Custom rules, caps, trainer variants, AI, item restrictions. | Native rules are actually applied; fixed and randomized runs tested; boss randomization survives difficulty selection; no softlocks. |
| E — Optional rules/assets | Abilities, field/hidden/held items, follower coverage and fixes, expanded roster audit. | Summary/battle/AI consistency; protected progression items; audited art/data gaps and fixes; follower regressions pass. |
| F — Campaign/package | Fixed-mode encounter design, progression and postgame regression, separate installer namespace, matching engine/pack, update path. | Device playthrough through Champion plus representative postgame; save recovery/update rehearsal; release audit; installation instructions from clean inputs. |

Device confirmation gates acceptance claims, not all independent engineering. While Derek tests a build, Codex can prepare the next stage's design and isolated host tests, but should not stack unverified gameplay changes into the baseline test package.

### Minimum physical-console smoke test

Record console model, source revision, build/data hashes, settings, pass/fail, and relevant logs for each run:

- Boot, New Game, intro/starter choice, first battle, walking and map transition.
- 2D/voxel switch, camera/blur, sound, follower on/off.
- Catch a later-generation test Pokémon, inspect summary/moves, deposit/withdraw, evolve, save, restart, Continue. Developer test grants are clearly marked and separate from normal gameplay.
- One single trainer battle, rival, double battle/partner, Gym Leader, Elite Four representative; exercise relevant Mega behavior already in the base.
- Confirm Continue preserves identity/options; starting a separate new run changes seed without modifying the previous backup.

Automated checks should cover deterministic resolvers, empty pools, flags/storage conflicts, actual production adapters, save round trips, trainer legality, and progression-item exclusions. Do not add only tests that restate constants or test an independent mock implementation while the real hooks remain untested. Use the existing host regression/link/asset audits and a fresh-bootstrap reproduction test for engine-patch changes.

Keep evidence labels separate: **source inspected**, **host checks passed**, **native compiled**, **emulator exercised**, **hardware exercised**, **campaign completed**. Never upgrade one label into another.

## 11. Packaging and ongoing project records

Before deployment, audit every runtime path, including save/backups, global settings, clock sidecars, debug logs, loose-data markers, and packs. Proposed project namespace: `/3ds/emerald3ds-custom/`. Merely renaming the application folder is insufficient if hard-coded paths still point at `/3ds/emerald3ds/`; change and test those paths. Keep Derek's original installation intact.

Maintain these project records as implementation progresses:

- `docs/PROJECT_BLUEPRINT.md` — this specification.
- `docs/STATUS.md` — completed stage, exact checks, known blockers, next concrete task.
- `docs/SOURCES.md` — upstream pins, copied/adapted features, license/credit inventory.
- `docs/SAVE_FORMAT.md` — storage reservations, versions, migration/recovery policy.
- `docs/RULES.md` — exact presets, randomizer exclusions, order of operations.
- `docs/BUILD.md` and `docs/DEVICE_TESTS.md` — reproducible setup and real device results.
- An asset/feature audit generated by tooling, not a handwritten assertion of completeness.

Extend the existing AGENTS.md with concise project-specific rules; preserve its build/patch gotchas. Put the full blueprint in docs rather than consuming the whole agent instruction budget. Store implementation in source control with focused commits. Do not depend on this conversation or a temporary workspace as the only copy.

Use private development artifacts. Keep ROM dumps, saves, firmware, generated game-data packs, and embedded-content builds out of public source/CI artifacts. Follow the port's engine-only release audit and derive player data through a validated custom recipe. The MIT license covers the port's original contributions, not every Pokémon asset or upstream component.

## 12. Copy-ready first Codex task

Paste the following with this document attached or saved at `docs/PROJECT_BLUEPRINT.md`:

```text
Implement Stage A of the attached Emerald 3DS Custom blueprint. Treat the
blueprint as the product specification. Begin work, not just another plan.

Goal: reproduce the existing native Nintendo 3DS expansion build and leave
a repeatable development workflow plus an isolated device smoke-test package.
Do not implement the randomizer or difficulty changes in this first task.

Candidate base:
https://github.com/jmurth1234/pokeemerald-expansion-3Ds-dualscreen
Baseline revision: 8ebb7355742ce43bbb10528044f9a175fc990a64
Pinned expansion: dfb0f84374230f4d462191601179b742f9f077df

1. Inspect the current workspace and applicable AGENTS.md files. If no project
   checkout exists, create one from the candidate in a clean directory. If one
   exists, inspect its changes and work without overwriting unrelated work.
   Preserve upstream history and use a project branch. Do not silently update
   the engine pin or merge donor projects. No remote publication is required.

2. Read upstream.lock, AGENTS.md, docs/DEVELOPMENT.md,
   docs/EXPANSION_FEATURES.md, the CI workflow, and relevant build files.
   Check the baseline SHA and record source/tool versions and current status.

3. Configure the official devkitPro/devkitARM 3DS toolchain and host dependencies
   in this environment. Use the existing CI container/workflow as a reference;
   do not assume nested Docker exists or that a generic ARM compiler is enough.
   Add a reproducible setup/build entry point and concise environment guidance.
   Diagnose dependency/network failures. If permissions or access prevent a
   necessary step, report the exact failure and missing prerequisite while
   completing independent source/setup work. Never claim compilation from
   host fixtures alone.

4. Run the documented bootstrap for pokeemerald-expansion, compile the native
   3DSX, run make verify and the expansion enhancement adapter tests. Repair
   reproducible baseline build failures in small focused changes if necessary;
   preserve the existing renderer, gameplay, and both build recipes where
   applicable. Regenerate the expansion patch correctly for any engine edits,
   including new files, and prove a clean bootstrap reproduces those edits.

5. Inspect generated asset tables and native-link/release audits. Record build
   outputs, sizes, hashes, and exact commands. Keep generated game data private.
   If release packaging needs a player-supplied ROM, document the exact input
   and local extraction path rather than obtaining or committing a ROM.

6. Before copying anything to an SD card, audit hard-coded save/settings/clock/
   data/log paths. Implement and verify a separate custom-project namespace
   where practical so this test cannot overwrite the original Emerald 3DS
   installation or save. Package a private development build with clear
   installation/audio instructions; if isolation remains unresolved, label
   the package not ready for deployment and explain the specific path conflict.

7. Create/update docs/STATUS.md, docs/BUILD.md, docs/SOURCES.md, and
   docs/DEVICE_TESTS.md. Preserve and extend the existing AGENTS.md's useful
   instructions. Include the blueprint's smoke checklist and leave device
   results explicitly pending. Identify original 3DS XL versus New XL as a
   hardware fact to collect, not a reason to block compilation.

8. Report what changed, checks actually run and outcomes, artifact paths,
   unresolved blockers, and Derek's next concrete hardware-test steps. Do not
   stop after writing documentation if the native build can be attempted.
   Do not claim a finished expanded game or verified Gen 1–9 assets from a
   successful build. Keep this first task scoped to Stage A.
```

## 13. Follow-on Codex task prompts

Use the same repository and blueprint; each task reads `docs/STATUS.md` first and updates it. Continue routine fixes within the selected task without requesting permission for every edit. A hardware dependency or substantive design conflict should be reported concretely; it should not become an invented claim of completion.

**Stage B:** “Implement saved run configuration and the new-game Standard/Randomized plus Normal/Hard/Custom setup shell. Audit flags/save layouts first, avoid the known 0x20–0x2B collision, commit choices after new-save initialization, and make cancellation/save/restart behavior correct. Rules not yet implemented must be visibly unavailable. Compile and test production save/menu adapters; leave no active no-op setting.”

**Stage C:** “Implement seeded starters, wild slots, and trainer parties using section 7. Adapt the Tertu donor selectively to the pinned engine. Preserve rival continuity, visible encounter identity, valid forms/moves, and tutorial/partner logic. Cover bosses, rematches, doubles, same-seed reload, Standard identity behavior, and fresh-bootstrap patch reproduction. Keep abilities/items off until implemented.”

**Stage D:** “Implement independent Normal/Hard/Custom difficulty using native caps, trainer variants, and deliberate AI/item policies. Follow section 8; do not equate difficulty with reduced EXP. Ensure difficulty composition never disables randomized bosses. Document cap progression and exact preset rules, compile, and exercise production hooks in fixed and randomized configurations.”

**Stage E:** “Add optional ability, field/hidden-item, and held-item randomization with stable save-bound rules. Audit actual ability access paths and protect progression. Generate Gen 1–9/follower coverage reports, fix confirmed gaps with attributed assets, and test 2D/voxel follower contexts. Do not describe fallback sprites as complete species artwork.”

**Stage F:** “Prepare the fixed expanded campaign roster and final custom player-data build/installer. Validate progression, engine/data matching, isolated paths, save backup/recovery, and update behavior. Consolidate hardware regression results and remaining exclusions. Produce source/engine-only distributable outputs and private test packages as appropriate; do not publicly publish content-bearing artifacts.”

## 14. References for the implementing agent

- Candidate [AGENTS.md](https://github.com/jmurth1234/pokeemerald-expansion-3Ds-dualscreen/blob/8ebb7355742ce43bbb10528044f9a175fc990a64/AGENTS.md), [development guide](https://github.com/jmurth1234/pokeemerald-expansion-3Ds-dualscreen/blob/8ebb7355742ce43bbb10528044f9a175fc990a64/docs/DEVELOPMENT.md), [feature audit](https://github.com/jmurth1234/pokeemerald-expansion-3Ds-dualscreen/blob/8ebb7355742ce43bbb10528044f9a175fc990a64/docs/EXPANSION_FEATURES.md), and [CI workflow](https://github.com/jmurth1234/pokeemerald-expansion-3Ds-dualscreen/blob/8ebb7355742ce43bbb10528044f9a175fc990a64/.github/workflows/ci.yml).
- Native expansion [caps](https://github.com/rh-hideout/pokeemerald-expansion/blob/dfb0f84374230f4d462191601179b742f9f077df/include/config/caps.h), [battle configuration](https://github.com/rh-hideout/pokeemerald-expansion/blob/dfb0f84374230f4d462191601179b742f9f077df/include/config/battle.h), and [AI flags](https://github.com/rh-hideout/pokeemerald-expansion/blob/dfb0f84374230f4d462191601179b742f9f077df/include/constants/battle_ai.h).
- Randomizer donor [interface](https://github.com/Zetraphes/pokeemerald-expansion/blob/1ad60617c8c17da5e6d380371cfa9429ce9b9a4e/include/randomizer.h) and [configuration](https://github.com/Zetraphes/pokeemerald-expansion/blob/1ad60617c8c17da5e6d380371cfa9429ce9b9a4e/include/config/randomizer.h).
- Modern Emerald [README](https://github.com/resetes12/pokeemerald/blob/37e437f1a80e5ccd3ba50933e5f113344c5db64e/README.md); Exalted Emerald [README](https://github.com/segabl/exalted-emerald/blob/b459df3f31b13df83a3baa78413145c302ed122d/README.md). Feature descriptions are references; the relevant source still needs compatibility review.
- Emerald 3DS [original port license](https://github.com/ZallaxDev/emerald-3ds/blob/b198c08defb94081ae995796cf75ab8cdb51f2d0/LICENSE-PORT.md) and third-party notices.
- [devkitPro package setup](https://devkitpro.org/wiki/devkitPro_pacman) and [official 3DS examples](https://github.com/devkitPro/3ds-examples). The package wiki was not retrievable by this research browser; use the installed environment's current official instructions.
- OpenAI's current [Cloud environments guide](https://learn.chatgpt.com/docs/environments/cloud-environments) explains repository/tool setup and isolated task workspaces. The [AGENTS.md guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md) explains persistent project instructions. Cloud interface details can change; follow the current guide instead of assuming legacy environment menus.

**First success condition:** a reproducible, isolated expanded Emerald 3DS build that boots and passes the smoke checklist on Derek's actual console. Feature integration follows that evidence.
