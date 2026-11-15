#!/usr/bin/env python3
"""Install/recover the private custom bundle on a laptop using Python 3.11+."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'builder'))
from emerald3ds_builder.custom_package import APP, PackageError, install_bundle, recover, validate_bundle
from emerald3ds_builder.pak import PakError


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bundle', type=Path, default=ROOT / '3ds' / APP)
    ap.add_argument('--sd', type=Path, help='SD card root, such as E:\\ or /Volumes/SDCARD')
    choice = ap.add_mutually_exclusive_group()
    choice.add_argument('--verify', action='store_true', help='check package without changing the SD card')
    choice.add_argument('--recover', action='store_true', help='roll back an interrupted installation')
    args = ap.parse_args()
    if args.verify:
        meta = validate_bundle(args.bundle)
        print(f'Package verified: {meta["data_files"]} entries, ABI {meta["engine_abi"]:08x}')
    elif not args.sd:
        ap.error('--sd is required to install or recover')
    elif args.recover:
        print('Interrupted update rolled back.' if recover(args.sd) else 'No interrupted update.')
    else:
        print(json.dumps(install_bundle(args.sd, args.bundle), indent=2))


if __name__ == '__main__':
    try:
        main()
    except (PackageError, PakError, OSError, ValueError) as exc:
        print('Stopped: ' + str(exc), file=sys.stderr)
        sys.exit(1)
