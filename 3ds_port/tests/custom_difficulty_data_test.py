"""Read actual native linked trainer variants via ARM GDB; no ARM execution."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

SCRIPT=r'''
set pagination off
set width 0
set $i=1
while $i < sizeof(gTrainers[0])/sizeof(gTrainers[0][0])
 set $h=&gTrainers[DIFFICULTY_HARD][$i]
 set $n=&gTrainers[DIFFICULTY_NORMAL][$i]
 if $h->party
  printf "TRAINER,%u,%u,%u,%u,%u,%u,%u\n",$i,$h->partySize,$n->partySize,$h->battleType,$n->battleType,$h->aiFlags,$n->aiFlags
  set $j=0
  while $j<$h->partySize
   set $m=&$h->party[$j]
   printf "MON,%u,%u,%u,%u,%u,%u,%u\n",$i,$j,$m->species,$m->lvl,$n->party[$j].lvl,$m->iv,$m->heldItem
   if $m->ev
    printf "EV,%u,%u,%u,%u,%u,%u,%u,%u\n",$i,$j,$m->ev[0],$m->ev[1],$m->ev[2],$m->ev[3],$m->ev[4],$m->ev[5]
   end
   set $j=$j+1
  end
 end
 set $i=$i+1
end
'''

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--tree',type=Path,required=True)
    p.add_argument('--gdb',required=True)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    with tempfile.TemporaryDirectory() as temp:
        commands=Path(temp)/'trainers.gdb';commands.write_text(SCRIPT)
        result=subprocess.run([args.gdb,'-batch','-nx',str(args.tree/'3ds_port/build/gamedata_image.elf'),'-x',str(commands)],text=True,capture_output=True)
        if result.returncode: raise RuntimeError(result.stdout+result.stderr)
    trainers={};mons={};evs={}
    for line in result.stdout.splitlines():
        parts=line.split(',')
        if parts[0] not in ('TRAINER','MON','EV'):continue
        values=list(map(int,parts[1:]));ident=values[0]
        if parts[0]=='TRAINER':
            assert values[1]==values[2] and values[3]==values[4] and values[1]>0,values
            assert values[5]==values[6] and not values[5] & (1<<16),values # native omniscient flag
            trainers[ident]=values[1]
        elif parts[0]=='MON':
            assert values[2]>0 and values[3]==values[4] and values[5]==0x3FFFFFFF and values[6]>0,values
            mons[ident,values[1]]=values
        else:
            assert values[2:]==[64]*6,values
            evs[ident,values[1]]=values
    assert len(trainers)==49 and len(mons)==sum(trainers.values()) and mons.keys()==evs.keys()
    report={'evidence':'native linked data inspected, no ARM execution','prepared_variants':len(trainers),'prepared_party_entries':len(mons),
            'all_levels_sizes_battle_types_retained':True,'all_ivs_31':True,'all_evs_64_each':True,'all_have_held_item':True,'native_ai_preserved_for_independent_custom_choice':True,'no_omniscient_variant':True}
    if args.output:args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))

if __name__=='__main__':main()
