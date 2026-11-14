"""Inventory linked expansion data and indexed art; metadata is not visual acceptance.

Reads PROGBITS gamedata_image.elf using ARM GDB (no ARM execution). Reports
source-name matches, shared art, Substitute fallback and missing assets separately.
"""
import argparse,csv,hashlib,json,re,subprocess,tempfile
from collections import Counter
from pathlib import Path

SCRIPT=r'''
set pagination off
set confirm off
set width 0
set $i=1
while $i<NUM_SPECIES
 set $p=&gSpeciesInfo[$i]
 if $p->natDexNum && $p->baseHP
  set $b=$i
  if $p->formSpeciesIdTable
   set $b=$p->formSpeciesIdTable[0]
  end
  printf "NAME,%u,",$i
  output (enum Species)$i
  printf "\n"
  printf "MON,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u\n",$i,$p->natDexNum,$b,$p->baseHP,$p->frontPic,$p->backPic,$p->iconSprite,$p->palette,$p->shinyPalette,$p->cryId,$p->levelUpLearnset,$p->evolutions,$p->formChangeTable
  printf "OW,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u\n",$i,$p->overworldData.images,$p->overworldData.oam,$p->overworldData.anims,$p->overworldData.paletteTag,$p->overworldPalette,$p->overworldShinyPalette,$p->overworldDataFemale.images,$p->overworldDataFemale.paletteTag,$p->overworldPaletteFemale,$p->overworldShinyPaletteFemale,$p->abilities[0],$p->teachableLearnset
 end
 set $i=$i+1
end
printf "FRAME_SIZE,%u\n",sizeof(struct SpriteFrameImage)
'''

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tree',type=Path,required=True);p.add_argument('--gdb',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 port=a.tree.resolve()/'3ds_port';elf=port/'build/gamedata_image.elf'
 def gdb(script):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'audit.gdb';f.write_text(script)
   return subprocess.check_output([a.gdb,'--batch',str(elf),'-x',str(f)],text=True)
 assets={};aliases={}
 for line in (port/'romfs/assets/asset_map.txt').read_text().splitlines():
  if line and not line.startswith('#'):
   addr,size,path=line.split(maxsplit=2);assets[int(addr,16)]=(int(size,16),path)
 for line in (port/'romfs/assets/asset_ptr_map.txt').read_text().splitlines():
  if line and not line.startswith('#'):
   ptr,base,offset=map(lambda v:int(v,16),line.split());aliases[ptr]=(base,offset)
 def asset(ptr):
  base,off=aliases.get(ptr,(ptr,0));size,path=assets.get(base,(0,''));return max(0,size-off),path,off
 raw=gdb(SCRIPT);names={};mons={};ows={};frame_size=0
 for line in raw.splitlines():
  if line.startswith('NAME,'):
   _,sid,name=line.split(',',2);names[int(sid)]=name.removeprefix('SPECIES_')
  if line.startswith(('MON,','OW,')):
   k,*nums=line.split(',');vals=list(map(int,nums));(mons if k=='MON' else ows)[vals[0]]=vals[1:]
  if line.startswith('FRAME_SIZE,'):frame_size=int(line.split(',')[1])
 nm=Path(a.gdb).with_name('arm-none-eabi-nm');symbols={}
 for line in subprocess.check_output([str(nm),'-S','--defined-only',str(elf)],text=True).splitlines():
  fields=line.split()
  if len(fields)==4:
   addr,size,kind,name=fields;symbols[int(addr,16)]=(int(size,16),name)
 image_ptrs={v[i] for v in ows.values() for i in (0,6) if v[i]}
 frames={};commands=['set pagination off','set width 0']
 for ptr in sorted(image_ptrs):
  count=symbols.get(ptr,(0,''))[0]//frame_size
  if not 0<count<=256:continue
  for i in range(count):
   commands.append(f'printf "FRAME,{ptr},{i},%u,%u,%u\\n",((struct SpriteFrameImage*){ptr})[{i}].data,((struct SpriteFrameImage*){ptr})[{i}].size,((struct SpriteFrameImage*){ptr})[{i}].offset')
 for line in gdb('\n'.join(commands)).splitlines():
  if line.startswith('FRAME,'):
   _,ptr,index,data,size,off=map(lambda v:int(v) if v.isdecimal() else v,line.split(','));frames.setdefault(ptr,[]).append((data,size,off))
 def follower(sid,ow,female=False):
  ptr=ow[6] if female and ow[7]==0x1124 else ow[0]
  palette=ow[8] if female and ow[8] else ow[4];shiny=ow[9] if female and ow[9] else ow[5]
  fs=frames.get(ptr,[]);paths=[];valid=bool(ptr and ow[1] and ow[2] and fs)
  for data,size,offset in fs:
   length,path,start=asset(data)
   if size and not length:valid=False
   if path:paths.append(path)
  joined=' '.join(paths).lower();token=names[sid].lower()
  if 'substitute' in joined:kind='fallback'
  elif not valid:kind='fallback_missing_metadata'
  elif token in joined:kind='source_name_match'
  else:kind='shared_or_unmatched'
  return {'kind':kind,'frame_entries':len(fs),'paths':sorted(set(paths)),
          'normal_palette_indexed':bool(asset(palette)[0]),'shiny_palette_indexed':bool(asset(shiny)[0]),
          'female_specific':bool(female and ow[7]==0x1124)}
 entries=[];base=[]
 for sid,v in mons.items():
  nat,b,hp,*rest=v;front,back,icon,pal,shiny,cry,learn,evo,form=rest
  art={key:asset(ptr)[1] for key,ptr in zip(('front','back','icon','normal','shiny'),(front,back,icon,pal,shiny))}
  row={'species_id':sid,'name':names[sid],'national':nat,'base':b,'core_eligible':sid==b and nat<=1025,'hp':hp,
       'art':art,'cry_id':cry,'levelup_present':bool(learn),'teachable_present':bool(ows[sid][11]),
       'evolution_table_present':bool(evo),'form_rules_present':bool(form),'ability_0':ows[sid][10],
       'follower':follower(sid,ows[sid]),'female_follower':follower(sid,ows[sid],True)}
  entries.append(row)
  if row['core_eligible']:base.append(row)
 assert len(base)==1025 and {v['national'] for v in base}==set(range(1,1026)),len(base)
 for row in base:assert all(row['art'].values()) and row['ability_0'] and row['levelup_present'],row['name']
 summary={'evidence':'linked ARM data / indexed files; no ARM, emulator, GPU or console execution',
          'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'enabled_forms':len(entries),'core_base_species':len(base),
          'generation_9_base_species':sum(v['national']>=906 for v in base),
          'base_followers':dict(Counter(v['follower']['kind'] for v in base)),
          'all_form_followers':dict(Counter(v['follower']['kind'] for v in entries)),
          'limits':['source_name_match does not certify exact artwork or animation',
                    'shared_or_unmatched requires human visual review; no attribution invented',
                    'cry/learnset/evolution/ability pointers do not certify complete mechanics',
                    'terminal species may legitimately have no evolution or form table']}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps({'summary':summary,'entries':entries},indent=2)+'\n')
 a.output.with_suffix('.summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 with a.output.with_suffix('.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['species_id','name','national','core_base','front','back','icon','normal','shiny','cry','levelup','teachable','evolution_table','form_rules','ability_0','follower_kind','frames','follower_assets','female_specific'])
  for v in entries:w.writerow([v['species_id'],v['name'],v['national'],v['core_eligible'],*v['art'].values(),v['cry_id'],v['levelup_present'],v['teachable_present'],v['evolution_table_present'],v['form_rules_present'],v['ability_0'],v['follower']['kind'],v['follower']['frame_entries'],';'.join(v['follower']['paths']),v['female_follower']['female_specific']])
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
