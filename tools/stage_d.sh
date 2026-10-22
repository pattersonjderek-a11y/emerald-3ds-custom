#!/usr/bin/env bash
# Stage D: same pinned SDK; isolated build tree, save namespace and private package.
set -euo pipefail
cd "$(dirname "$0")/.."
export DEVKITPRO="${DEVKITPRO:-/opt/devkitpro}"
export DEVKITARM="${DEVKITARM:-$DEVKITPRO/devkitARM}"
export PATH="$DEVKITARM/bin:$DEVKITPRO/tools/bin:$PATH"
export EMERALD3DS_EXPANSION_TREE="$PWD/build/stage-d"
case "${1:-build}" in
  build)
    python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir build/stage-d --make -j"${JOBS:-4}" --python python3
    ;;
  test)
    make -C build/stage-d/3ds_port verify PYTHON=python3
    python3 -m unittest builder.tests.test_expansion_enhancements -v
    python3 -m unittest discover -s builder/tests -v
    python3 tools/release_audit.py --repo . --strict
    ;;
  package)
    make -C build/stage-d/3ds_port release pak PYTHON=python3
    python3 tools/private_smoke_package.py --stage D --tree build/stage-d
    ;;
  versions) tools/stage_a.sh versions ;;
  *) echo 'Usage: tools/stage_c_visuals.sh build|test|versions|package' >&2; exit 2 ;;
esac
