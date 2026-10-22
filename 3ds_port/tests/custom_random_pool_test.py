"""Audit eligible species against the actual linked ARM data and asset index.

This is a linked-data audit, not ARM execution or a complete follower audit.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import tempfile

SCRIPT = r'''
set pagination off
set confirm off
set width 0
set $i=1
while $i < NUM_SPECIES
  set $p=&gSpeciesInfo[$i]
  if $p->natDexNum && $p->baseHP
    set $base=$i
    if $p->formSpeciesIdTable
      set $base=$p->formSpeciesIdTable[0]
    end
    set $first=255
    if $p->levelUpLearnset
      set $j=0
      while $j<512 && $p->levelUpLearnset[$j].move!=65535
        set $m=$p->levelUpLearnset[$j].move
        if $m && gMovesInfo[$m].power && $m!=MOVE_SNORE && $m!=MOVE_DREAM_EATER && $m!=MOVE_LAST_RESORT && $m!=MOVE_EXPLOSION && $m!=MOVE_SELF_DESTRUCT
          if $p->levelUpLearnset[$j].level < $first
            set $first=$p->levelUpLearnset[$j].level
          end
        end
        set $j=$j+1
      end
    end
    set $regional=$p->isAlolanForm+2*$p->isGalarianForm+4*$p->isHisuianForm+8*$p->isPaldeanForm
    set $banned=$p->isMegaEvolution+$p->isPrimalReversion+$p->isUltraBurst+$p->isGigantamax+$p->isTeraForm+$p->isTotem
    set $legend=$p->isRestrictedLegendary+$p->isSubLegendary+$p->isMythical+$p->isUltraBeast
    set $bst=$p->baseHP+$p->baseAttack+$p->baseDefense+$p->baseSpeed+$p->baseSpAttack+$p->baseSpDefense
    printf "POOL,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u\n",$i,$p->natDexNum,$base,$regional,$banned,$legend,$first,$p->frontPic,$p->backPic,$p->iconSprite,$p->palette,$p->shinyPalette,$bst,$p->abilities[0]
  end
  set $i=$i+1
end
'''


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--tree', type=Path, required=True)
    p.add_argument('--gdb', required=True)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    tree = args.tree.resolve()
    port = tree / '3ds_port'
    assets = {}
    for line in (port / 'romfs/assets/asset_map.txt').read_text().splitlines():
        if line.startswith('#') or not line.strip():
            continue
        address, size, name = line.split(maxsplit=2)
        assets[int(address, 16)] = (int(size, 16), name)
    pointer_map = {}
    for line in (port / 'romfs/assets/asset_ptr_map.txt').read_text().splitlines():
        if line.startswith('#') or not line.strip():
            continue
        pointer, base, offset = (int(v,16) for v in line.split())
        pointer_map[pointer]=(base,offset)
    def asset(pointer):
        if pointer in assets:
            return assets[pointer]
        base, offset = pointer_map.get(pointer,(0,0))
        size, name = assets.get(base,(0,''))
        return max(0,size-offset), name
    with tempfile.TemporaryDirectory() as temporary:
        commands = Path(temporary) / 'pool.gdb'
        commands.write_text(SCRIPT)
        result = subprocess.run([args.gdb, '--batch', str(port / 'build/gamedata_image.elf'),
                                 '-x', str(commands)], capture_output=True, text=True, check=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.with_suffix('.csv').write_text(result.stdout)
    counts = Counter()
    entries = []
    excluded = Counter()
    for line in result.stdout.splitlines():
        if not line.startswith('POOL,'):
            continue
        species, national, base, regional, banned, legend, first, *rest = map(int, line.split(',')[1:])
        pointers, bst, ability = rest[:5], rest[5], rest[6]
        if not ability:
            excluded['missing_native_ability'] += 1
            continue
        if banned or (species != base and not regional) or species == 1093:
            excluded['unsupported_form'] += 1
            continue
        if first > 100:
            excluded['no_usable_levelup_attack'] += 1
            continue
        sizes = [asset(addr)[0] for addr in pointers]
        if any(n <= limit for n, limit in zip(sizes, (4, 4, 511, 1, 1))):
            excluded['missing_indexed_graphics'] += 1
            continue
        generation = 9 if regional & 8 else 8 if regional & 6 else 7 if regional & 1 else next((g for g, end in enumerate((151,251,386,493,649,721,809,905,1025), 1) if national <= end), 0)
        assert generation, (species, national)
        counts[generation] += 1
        entries.append({'species_id': species, 'national_dex': national, 'generation': generation,
                        'legendary_or_ultra': bool(legend), 'first_attack_level': first, 'bst': bst,
                        'graphics': [asset(addr)[1] for addr in pointers]})
    assert all(counts[g] >= 3 for g in range(1, 10)), counts
    ids = {x['species_id'] for x in entries}
    missing = {1289,1292,1295,1416,1431,1434} - ids
    if missing:
        print('Missing linked-pool examples:',sorted(missing), 'counts',dict(counts), 'exclusions',dict(excluded),flush=True)
    assert not missing, 'Gen 9 starter/DLC examples missing from linked pool'
    for g in range(1, 10):
        assert sum(e['generation']==g and e['first_attack_level']<=5 and not e['legendary_or_ultra'] for e in entries)>=3
    report = {'evidence': 'linked ARM data and indexed graphics; no emulator/console execution',
              'eligible': len(entries), 'by_generation': dict(sorted(counts.items())),
              'excluded': dict(excluded), 'entries': entries}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2)+'\n')
    print('PASS linked species pool:',len(entries),'eligible;',dict(sorted(counts.items())), '; exclusions',dict(excluded))
    print('PASS Gen 9 starters, Ogerpon, Terapagos, Pecharunt and at least three nonlegendary starters per generation')


if __name__ == '__main__':
    main()
