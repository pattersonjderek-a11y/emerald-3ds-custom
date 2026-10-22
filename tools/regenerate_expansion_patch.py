#!/usr/bin/env python3
"""Regenerate the canonical expansion patch, retaining its existing new files.

Pass each additional engine file with --add. Never stage overlays/generated data.
The upstream pin is read from upstream.lock. The staged engine index is local
build metadata and is not a commit or a change to upstream history.
"""
import argparse
import configparser
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'patches/pokeemerald-expansion/0001-port.patch'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree', type=Path, default=ROOT / 'build/stage-b')
    parser.add_argument('--add', nargs='*', default=[])
    args = parser.parse_args()
    tree = args.tree.resolve()
    lock = configparser.ConfigParser()
    lock.read(ROOT / 'upstream.lock')
    pin = lock['pokeemerald-expansion']['commit'].strip('"')
    head = subprocess.check_output(['git', '-C', str(tree), 'rev-parse', 'HEAD'], text=True).strip()
    if head != pin:
        parser.error(f'engine HEAD {head} does not match locked pin {pin}')
    original = PATCH.read_text()
    paths = list(dict.fromkeys(re.findall(r'^\+\+\+ w/(.+)$', original, re.M) + args.add))
    for name in args.add:
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts or relative.parts[0] in ('3ds_port', 'builder', 'tools', 'build'):
            parser.error(f'not an engine source path: {name}')
        if relative.suffix not in ('.c', '.h', '.inc', '.s', '.json'):
            parser.error(f'not a supported source addition: {name}')
    subprocess.run(['git', '-C', str(tree), 'add', '-f', '--', *paths], check=True)
    staged = subprocess.check_output(['git', '-C', str(tree), 'diff', '--cached', '--name-only', pin], text=True).splitlines()
    unexpected = set(staged) - set(paths)
    if unexpected:
        raise SystemExit(f'Unlisted staged files; inspect the engine index first: {sorted(unexpected)}')
    body = subprocess.check_output(['git', '-C', str(tree), 'diff', '--cached', '--src-prefix=c/', '--dst-prefix=w/', pin], text=True)
    result = '\n'.join(original.splitlines()[:3]) + '\n' + body
    subprocess.run(['git', '-C', str(tree), 'apply', '--check', '--reverse', '-'], input=result, text=True, check=True)
    PATCH.write_text(result)
    print(f'Captured {len(staged)} engine source files; reverse apply passed. Fresh bootstrap still required.')


if __name__ == '__main__':
    main()
