#!/usr/bin/env python3
"""Inventory native ability resolution and intentional raw template-ID reads."""
import argparse,json,re
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tree',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
roles={'pokemon.c':'central resolver native input / non-port fallback',
       'custom_random.c':'constructor stores a native ability ID for conversion to slot',
       'trainer_util.c':'converts native trainer template IDs to stored ability slots',
       'battle_frontier.c':'converts protected facility template IDs to stored slots'}
raw=[];calls=[]
for path in sorted((a.tree/'src').rglob('*.c')):
 for i,line in enumerate(path.read_text(errors='replace').splitlines(),1):
  if re.search(r'gSpeciesInfo\[[^]]+\]\.abilities|speciesInfo->abilities',line):
   assert path.name in roles,(path,i,line)
   raw.append({'file':str(path.relative_to(a.tree)),'line':i,'role':roles[path.name],'source':line.strip()})
  for symbol in re.findall(r'\b(GetSpeciesAbility|GetAbilityBySpecies|GetMonAbility|GetBattlerAbility)\s*\(',line):
   calls.append({'file':str(path.relative_to(a.tree)),'line':i,'accessor':symbol})
report={'evidence':'source access-path audit; production resolver tests and native compilation are separate evidence',
        'raw_species_reads':raw,'accessor_calls':calls,
        'notes':['battle ability state can intentionally change through Trace, Skill Swap, etc.',
                 'optional resolver preserves native stored ability slot ABI and protected signature/form species',
                 'this audit does not certify every ability mechanic or a campaign playthrough']}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
print(f'Ability access audit PASS: {len(raw)} explained raw species references, {len(calls)} accessor references; no unexplained raw path.')
