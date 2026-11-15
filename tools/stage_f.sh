#!/usr/bin/env bash
# Stage F is separate from the frozen E source/build/ZIP/Dropbox delivery.
set -euo pipefail
cd "$(dirname "$0")/.."
export DEVKITPRO="${DEVKITPRO:-/opt/devkitpro}"
export DEVKITARM="${DEVKITARM:-$DEVKITPRO/devkitARM}"
export PATH="$DEVKITARM/bin:$DEVKITPRO/tools/bin:$PATH"
export EMERALD3DS_EXPANSION_TREE="$PWD/build/stage-f"
case "${1:-build}" in
 build) python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir build/stage-f --make -j"${JOBS:-6}" --python python3 ;;
 test)
  make -C build/stage-f/3ds_port verify PYTHON=python3
  python3 -m unittest discover -s builder/tests -v
  python3 -m unittest builder.tests.test_expansion_enhancements -v
  python3 tools/campaign_audit.py --tree build/stage-f --gdb "$DEVKITARM/bin/arm-none-eabi-gdb" --output work/stage-f-campaign.json
  python3 tools/release_audit.py --repo . --strict
  ;;
 fresh)
  python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir build/stage-f
  python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir work/stage-f-clean
  python3 tools/verify_expansion_bootstrap.py --tree build/stage-f --fresh work/stage-f-clean
  python3 tools/campaign_audit.py --tree work/stage-f-clean
  python3 3ds_port/tests/custom_run_test.py --tree work/stage-f-clean
  python3 3ds_port/tests/custom_difficulty_test.py --tree work/stage-f-clean
  python3 3ds_port/tests/optional_rules_test.py --tree work/stage-f-clean
  ;;
 package)
  tools/stage_f.sh test
  make -C build/stage-f/3ds_port release pak PYTHON=python3
  python3 tools/campaign_audit.py --tree build/stage-f --gdb "$DEVKITARM/bin/arm-none-eabi-gdb" --output work/stage-f-campaign.json
  python3 tools/custom_payload.py recipe --tree build/stage-f --out work/stage-f-source-recipe.json
  python3 tools/custom_payload.py build --recipe work/stage-f-source-recipe.json --romfs build/stage-f/3ds_port/romfs --engine-dir build/stage-f/3ds_port/dist --out work/stage-f-bundle
  python3 3ds_port/tests/custom_pack_test.py --bundle work/stage-f-bundle
  python3 tools/rehearse_custom_install.py --bundle work/stage-f-bundle --output work/stage-f-install-rehearsal.json
  python3 tools/package_stage_f.py --campaign-report work/stage-f-campaign.json
  ;;
 versions) tools/stage_a.sh versions ;;
 *) echo 'Usage: tools/stage_f.sh build|test|fresh|package|versions' >&2;exit 2 ;;
esac
