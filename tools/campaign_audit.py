#!/usr/bin/env python3
"""Audit the fixed Hoenn roster against Stage E and the linked ARM data.

Only metadata is written. GDB inspects PROGBITS, without running ARM code.
"""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def canonical_sha(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def audit_source(tree, spec):
    data = json.loads((tree / 'src/data/wild_encounters.json').read_text())
    restored = copy.deepcopy(data)
    entries = {e['base_label']: e for g in restored['wild_encounter_groups'] for e in g['encounters']}
    timed = {(f'MAP_{m}', int(i)) for m, i in re.findall(
        r'RULE\((\w+),\s*(\d+),', (ROOT / '3ds_port/src/3ds_encounter_tables.c').read_text())}
    seen = set()
    for row in spec['placements']:
        key = row['base_label'], row['method'], row['slot']
        assert key not in seen, key
        seen.add(key)
        assert (row['map'], row['slot']) not in timed, 'upstream timed slot overlap'
        entry = entries[row['base_label']]
        assert entry['map'] == row['map']
        mon = entry[row['method']]['mons'][row['slot']]
        expected = {**row['before'], 'species': row['species']}
        assert mon == expected, (key, mon, expected)
        mon.update(row['before'])
    assert canonical_sha(restored) == spec['baseline_canonical_sha256'], 'unexpected level/rate/table edits'
    # Keep each existing species available in its original local method.
    after = {e['base_label']: e for g in data['wild_encounter_groups'] for e in g['encounters']}
    for label, entry in entries.items():
        for method, table in entry.items():
            if isinstance(table, dict) and 'mons' in table:
                original = {m['species'] for m in table['mons']}
                current = {m['species'] for m in after[label][method]['mons']}
                assert original <= current, (label, method, original - current)
    return data


def audit_linked(tree, spec, gdb):
    elf = tree / '3ds_port/build/gamedata_image.elf'
    nm = str(Path(gdb).with_name('arm-none-eabi-nm'))
    symbol = next(line.split() for line in subprocess.check_output(
        [nm, '-S', '--defined-only', str(elf)], text=True).splitlines() if line.endswith(' gWildMonHeaders'))
    header_bytes = int(symbol[1], 16)
    lines = ['set pagination off', 'set confirm off', 'set width 0']
    # Read the actual header that the production encounter reader consumes,
    # then the slot, species, legal level-up attacks and all indexed pictures.
    for n, row in enumerate(spec['placements']):
        m = row['map']
        lines += ['set $i=0', 'set $h=0',
                  'while gWildMonHeaders[$i].mapGroup != 255',
                  f' if gWildMonHeaders[$i].mapGroup == {m}_GROUP && gWildMonHeaders[$i].mapNum == {m}_NUM',
                  '  set $h=&gWildMonHeaders[$i]', '  loop_break', ' end', ' set $i=$i+1', 'end',
                  'if !$h', f' printf "MISSING,{n}\\n"', 'else',
                  f' set $w=$h->encounterTypes[0].landMonsInfo->wildPokemon[{row["slot"]}]',
                  ' set $p=&gSpeciesInfo[$w.species]',
                  f' printf "ROW,{n},%u,%u,%u,%u,%u,%u,%u,%u,%u,%u\\n",$w.species,{row["species"]},$w.minLevel,$w.maxLevel,$p->natDexNum,$p->baseHP,$p->frontPic,$p->backPic,$p->iconSprite,$p->palette',
                  ' set $l=$p->levelUpLearnset', ' set $j=0', ' set $attacks=0',
                  ' while $l[$j].move != 65535 && $j<512',
                  '  set $move=$l[$j].move',
                  '  if $l[$j].level <= $w.minLevel && gMovesInfo[$move].power > 0 && $move != MOVE_SNORE && $move != MOVE_DREAM_EATER && $move != MOVE_LAST_RESORT && $move != MOVE_EXPLOSION && $move != MOVE_SELF_DESTRUCT',
                  '   set $attacks=$attacks+1', '  end', '  set $j=$j+1', ' end',
                  f' printf "ATTACKS,{n},%u\\n",$attacks', 'end']
    lines += ['set $i=0', 'set $headers=0',
              f'while $i < {header_bytes}/sizeof(struct WildPokemonHeader) && gWildMonHeaders[$i].mapGroup != 255',
              ' set $headers=$headers+1', ' set $t=0',
              ' while $t<TIMES_OF_DAY_COUNT',
              '  set $land=gWildMonHeaders[$i].encounterTypes[$t].landMonsInfo',
              '  if $land', '   set $s=0', '   while $s<12',
              '    set $species=$land->wildPokemon[$s].species',
              '    printf "LAND_DEX,%u\\n",gSpeciesInfo[$species].natDexNum',
              '    set $s=$s+1', '   end', '  end', '  set $t=$t+1', ' end',
              ' set $i=$i+1', 'end', 'printf "HEADERS,%u\\n",$headers']
    # GDB knows enum species but map macros need concrete values from generated header.
    maps = (tree / 'include/constants/map_groups.h').read_text()
    for i, line in enumerate(lines):
        if '_GROUP' in line:
            name = re.search(r'(MAP_\w+)_GROUP', line)[1]
            match = re.search(r'\b' + name + r'\s*=\s*\(?(\d+)\s*\|\s*\((\d+)\s*<<\s*8\)', maps)
            if not match:
                raise AssertionError(f'cannot resolve map {name}')
            number, group = map(int, match.groups())
            lines[i] = line.replace(name + '_GROUP', str(group)).replace(name + '_NUM', str(number))
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / 'campaign.gdb'
        script.write_text('\n'.join(lines) + '\n')
        proc = subprocess.run([gdb, '--batch', str(elf), '-x', str(script)], text=True, capture_output=True)
        if proc.returncode:
            debug = ROOT / 'work/campaign-audit-failure.gdb'
            debug.parent.mkdir(exist_ok=True)
            debug.write_text(script.read_text())
            raise RuntimeError(f'GDB data audit failed: {proc.stderr}; script: {debug}; last output: {proc.stdout[-1000:]}')
        raw = proc.stdout
    assets = {}
    for line in (tree / '3ds_port/romfs/assets/asset_map.txt').read_text().splitlines():
        if line and not line.startswith('#'):
            ptr, size, path = line.split(maxsplit=2)
            assets[int(ptr, 16)] = int(size, 16)
    for line in (tree / '3ds_port/romfs/assets/asset_ptr_map.txt').read_text().splitlines():
        if line and not line.startswith('#'):
            ptr, base, offset = (int(x, 16) for x in line.split())
            assets[ptr] = max(0, assets.get(base, 0) - offset)
    rows, attacks, land_dex = {}, {}, set()
    headers = 0
    for line in raw.splitlines():
        if line.startswith('ROW,'):
            _, index, *fields = line.split(',')
            rows[int(index)] = list(map(int, fields))
        if line.startswith('ATTACKS,'):
            _, index, count = line.split(',')
            attacks[int(index)] = int(count)
        if line.startswith('LAND_DEX,'):
            land_dex.add(int(line.split(',')[1]))
        if line.startswith('HEADERS,'):
            headers = int(line.split(',')[1])
    assert len(rows) == len(spec['placements']), raw
    result = []
    for i, row in enumerate(spec['placements']):
        sid, expected, lo, hi, national, hp, *pics = rows[i]
        assert sid == expected and hp and 1 <= national <= 1025, row
        assert (lo, hi) == (row['before']['min_level'], row['before']['max_level']), row
        assert attacks[i] > 0, f'no legal early attack: {row}'
        assert all(assets.get(ptr, 0) > 1 for ptr in pics), f'unindexed art: {row}'
        generation = next(g for g, end in enumerate((151, 251, 386, 493, 649, 721, 809, 905, 1025), 1) if national <= end)
        result.append({**row, 'national': national, 'generation': generation, 'legal_attacks': attacks[i]})
    land_generations = Counter(next(g for g,end in enumerate((151,251,386,493,649,721,809,905,1025),1) if n<=end) for n in land_dex)
    assert set(land_generations) == set(range(1,10)), land_generations
    return {'image_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
            'native_header_count': headers, 'native_fixed_land_unique_dex': len(land_dex),
            'native_fixed_land_generations': dict(sorted(land_generations.items())),
            'generations_added': dict(Counter(r['generation'] for r in result)), 'placements': result}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--tree', type=Path, default=ROOT / 'build/stage-f')
    ap.add_argument('--gdb')
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    spec = json.loads((ROOT / 'tools/campaign_f.json').read_text())
    audit_source(args.tree, spec)
    report = {'revision': spec['revision'], 'source_audit': 'passed',
              'native_data_audit': 'pending', 'hardware': 'pending', 'campaign_playthrough': 'pending'}
    if args.gdb:
        report.update(audit_linked(args.tree, spec, args.gdb))
        report['native_data_audit'] = 'passed'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(f'Campaign audit PASS: {len(spec["placements"])} fixed slots; levels/rates/local species/timed rules preserved; linked data {report["native_data_audit"]}. Hardware pending.')


if __name__ == '__main__':
    main()
