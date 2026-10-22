#!/usr/bin/env bash
# Run inside the documented SDK container, or an equivalent installed SDK.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p work
export DEVKITPRO="${DEVKITPRO:-/opt/devkitpro}"
export DEVKITARM="${DEVKITARM:-$DEVKITPRO/devkitARM}"
export PATH="$DEVKITARM/bin:$DEVKITPRO/tools/bin:$PATH"
for stage_a_tool in python3 gcc g++ make git arm-none-eabi-gcc 3dsxtool picasso; do
  command -v "$stage_a_tool" >/dev/null || {
    echo "Missing $stage_a_tool; use the SDK setup in docs/BUILD.md" >&2
    exit 1
  }
done
python3 -c 'import sys, PIL; assert sys.version_info >= (3, 11), "Python 3.11+ required"'
case "${1:-build}" in
  build)
    # Bootstrap is intentionally not --clean: inspect/protect engine work first.
    python3 tools/bootstrap.py --upstream pokeemerald-expansion --dir build/expansion --make -j"${JOBS:-4}" --python python3
    ;;
  test)
    make -C build/expansion/3ds_port verify PYTHON=python3
    python3 -m unittest builder.tests.test_expansion_enhancements -v
    python3 -m unittest discover -s builder/tests -v
    python3 tools/release_audit.py --repo . --strict
    ;;
  package)
    make -C build/expansion/3ds_port release pak PYTHON=python3
    python3 tools/private_smoke_package.py
    ;;
  versions)
    python3 --version
    python3 -c 'import PIL; print("Pillow", PIL.__version__)'
    gcc --version | head -1
    make --version | head -1
    git --version
    "$DEVKITARM/bin/arm-none-eabi-gcc" --version | head -1
    "$DEVKITPRO/pacman/bin/pacman" -Q
    dpkg-query -W build-essential g++ libpng-dev python3 python3-pil git
    ;;
  *) echo 'Usage: tools/stage_a.sh build|test|versions|package' >&2; exit 2 ;;
esac
