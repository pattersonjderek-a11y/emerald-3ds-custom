#!/usr/bin/env bash
# Combined v0.5.0 + Stage E workflow; historical branches/packages remain separate.
set -euo pipefail
cd "$(dirname "$0")/.."
export DEVKITPRO="${DEVKITPRO:-/opt/devkitpro}"
export DEVKITARM="${DEVKITARM:-$DEVKITPRO/devkitARM}"
export PATH="$DEVKITARM/bin:$DEVKITPRO/tools/bin:$PATH"
export EMERALD3DS_EXPANSION_TREE="$PWD/build/stage-e"
case "${1:-build}" in
 build) python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir build/stage-e --make -j"${JOBS:-6}" --python python3 ;;
 test)
  make -C build/stage-e/3ds_port verify PYTHON=python3
  python3 -m unittest builder.tests.test_expansion_enhancements -v
  python3 -m unittest discover -s builder/tests -v
  python3 tools/release_audit.py --repo . --strict
  ;;
 package)
  make -C build/stage-e/3ds_port release pak PYTHON=python3
  python3 tools/private_smoke_package.py --stage E --tree build/stage-e
  ;;
 versions) tools/stage_a.sh versions ;;
 *) echo 'Usage: tools/stage_e.sh build|test|package|versions' >&2;exit 2 ;;
esac
