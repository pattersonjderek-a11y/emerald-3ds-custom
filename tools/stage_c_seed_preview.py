#!/usr/bin/env python3
"""Execute the production C resolver against the audited linked species pool.

This is a host preview, not console evidence. Generate the pool with
custom_random_pool_test.py from the exact matching native build first.
"""
import argparse
import ctypes as C
import json
from pathlib import Path
import re
import subprocess
import tempfile


class Config(C.Structure):
    _fields_ = [(n, C.c_uint32) for n in ('seed','randomOptions','difficultyOptions','contentRules','runId')] + [('algorithm',C.c_uint16),('generations',C.c_uint16)] + [(n,C.c_uint8) for n in ('mode','difficulty','capMode','aiPolicy')] + [('balanceFlags',C.c_uint32)]


class Entry(C.Structure):
    _fields_ = [('species',C.c_uint16),('bst',C.c_uint16),('generation',C.c_uint8),('legendary',C.c_uint8),('firstDamageLevel',C.c_uint8)]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tree',type=Path,required=True)
    p.add_argument('--pool',type=Path,required=True)
    p.add_argument('--seed',type=int,default=42)
    p.add_argument('--generations',type=lambda v:int(v,0),default=0x1FF)
    p.add_argument('--balance',type=int,default=0)
    p.add_argument('--cc',default='cc')
    args=p.parse_args()
    tree=args.tree.resolve()
    assert 0<=args.seed<=0xFFFFFFFF
    data=json.loads(args.pool.read_text())['entries']
    entries=(Entry*len(data))(*(Entry(e['species_id'],e['bst'],e['generation'],e['legendary_or_ultra'],e['first_attack_level']) for e in data))
    names={int(number):name for name,number in re.findall(r'^\s*(SPECIES_\w+) = (\d+),',(tree/'include/constants/species.h').read_text(),re.M)}
    config=Config(seed=args.seed,randomOptions=7,contentRules=0x00020001,algorithm=1,generations=args.generations,mode=1,balanceFlags=args.balance)
    with tempfile.TemporaryDirectory() as temp:
        so=Path(temp)/'resolver.so'
        subprocess.run([args.cc,'-std=c99','-shared','-fPIC','-iquote',str(tree/'include'),str(tree/'src/custom_random_core.c'),'-o',str(so)],check=True)
        library=C.CDLL(str(so))
        pick=library.CRandom_Pick
        pick.argtypes=[C.POINTER(Config),C.POINTER(Entry),C.c_size_t,*([C.c_uint32]*4),C.c_uint16,C.c_uint,C.POINTER(C.c_uint16),C.c_size_t]
        pick.restype=C.c_uint16
        selected=(C.c_uint16*3)()
        for slot in range(3):
            selected[slot]=pick(C.byref(config),entries,len(entries),0x53545254,0,0,slot,310,5,selected,slot)
            assert selected[slot]
            print(f'Seed {args.seed}, slot {slot+1}: {names.get(selected[slot],selected[slot])} (internal {selected[slot]})')


if __name__=='__main__':
    main()
