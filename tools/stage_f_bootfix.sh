#!/usr/bin/env bash
# Compatible F repair; never replace frozen E/F/InstallerFix builds or ZIPs.
set -euo pipefail
cd "$(dirname "$0")/.."
export DEVKITPRO="${DEVKITPRO:-/opt/devkitpro}"
export DEVKITARM="${DEVKITARM:-$DEVKITPRO/devkitARM}"
export PATH="$DEVKITARM/bin:$DEVKITPRO/tools/bin:$PATH"
export EMERALD3DS_EXPANSION_TREE="$PWD/build/stage-f-boot"
tree=build/stage-f-boot
evidence=work/intro-boot
bundle=work/stage-f-boot-bundle
mkdir -p "$evidence"
case "${1:-build}" in
 build)
  python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir "$tree" --make -j"${JOBS:-6}" --python python3
  ;;
 test)
  make -C "$tree/3ds_port" verify PYTHON=python3
  python3 -m unittest discover -s builder/tests -v
  python3 3ds_port/tests/asset_memory_test.py
  make -C "$tree/3ds_port" release pak PYTHON=python3
  python3 3ds_port/tests/intro_asset_decode_test.py --tree "$tree" --pak "$tree/3ds_port/build/emerald3ds.pak"
  python3 tools/campaign_audit.py --tree "$tree" --gdb "$DEVKITARM/bin/arm-none-eabi-gdb" --output "$evidence/campaign.json"
  python3 tools/release_audit.py --repo . --strict
  ;;
 fresh)
  python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir "$tree"
  python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir work/stage-f-boot-clean
  python3 tools/verify_expansion_bootstrap.py --tree "$tree" --fresh work/stage-f-boot-clean
  python3 3ds_port/tests/custom_run_test.py --tree work/stage-f-boot-clean
  python3 3ds_port/tests/custom_difficulty_test.py --tree work/stage-f-boot-clean
  python3 3ds_port/tests/optional_rules_test.py --tree work/stage-f-boot-clean
  python3 3ds_port/tests/intro_asset_decode_test.py --tree "$tree" --code-tree work/stage-f-boot-clean --pak "$tree/3ds_port/build/emerald3ds.pak"
  ;;
 package)
  # Run test/fresh, inspect results and checkpoint source before this command.
  python3 tools/campaign_audit.py --tree "$tree" --gdb "$DEVKITARM/bin/arm-none-eabi-gdb" --output "$evidence/campaign.json"
  python3 tools/custom_payload.py recipe --tree "$tree" --out "$evidence/source-recipe.json"
  python3 tools/custom_payload.py build --recipe "$evidence/source-recipe.json" --romfs "$tree/3ds_port/romfs" --engine-dir "$tree/3ds_port/dist" --out "$bundle"
  python3 3ds_port/tests/custom_pack_test.py --bundle "$bundle"
  python3 tools/rehearse_custom_install.py --bundle "$bundle" --baseline-zip work/stage-f-private/Emerald3DS-Custom-StageF-private.zip --output "$evidence/install-rehearsal.json"
  python3 tools/package_stage_f.py --tree "$tree" --bundle "$bundle" --campaign-report "$evidence/campaign.json" --native-recompiled --rehearsal-report "$evidence/install-rehearsal.json" --output work/stage-f-bootfix-private/Emerald3DS-Custom-StageF-BootFix-private.zip
  ;;
 versions) tools/stage_a.sh versions ;;
 *) echo 'Usage: tools/stage_f_bootfix.sh build|test|fresh|package|versions' >&2;exit 2 ;;
esac
