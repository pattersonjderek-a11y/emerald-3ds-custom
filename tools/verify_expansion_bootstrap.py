#!/usr/bin/env python3
"""Compare a fresh bootstrap with the build tree and canonical source overlays."""
import argparse,configparser,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tree',type=Path,default=ROOT/'build/stage-e');p.add_argument('--fresh',type=Path,default=ROOT/'work/stage-e-clean');a=p.parse_args()
lock=configparser.ConfigParser();lock.read(ROOT/'upstream.lock');pin=lock['pokeemerald-expansion']['commit'].strip('"')
for tree in (a.tree,a.fresh):
 assert subprocess.check_output(['git','-C',str(tree),'rev-parse','HEAD'],text=True).strip()==pin
paths=re.findall(r'^\+\+\+ w/(.+)$',(ROOT/'patches/pokeemerald-expansion/0001-port.patch').read_text(),re.M)
for name in paths:assert (a.tree/name).read_bytes()==(a.fresh/name).read_bytes(),name
count=0
for folder in ('3ds_port','builder','tools'):
 for src in (ROOT/folder).rglob('*'):
  rel=src.relative_to(ROOT)
  if not src.is_file() or any(x in ('__pycache__','build','dist') for x in rel.parts) or src.suffix=='.pyc':continue
  assert (a.fresh/rel).read_bytes()==src.read_bytes(),str(rel)
  count+=1
assert (a.tree/'.emerald3ds-patches').read_text()==(a.fresh/'.emerald3ds-patches').read_text()
print(f'Fresh source reproduction PASS: pin {pin}, {len(paths)} engine paths, {count} canonical overlay files (no compilation claimed).')
