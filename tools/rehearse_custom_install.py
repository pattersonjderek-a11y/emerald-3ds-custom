#!/usr/bin/env python3
"""Rehearse the actual private bundle on a temporary host SD-shaped directory.

State bytes are explicitly synthetic. This never accesses a mounted SD card.
"""
import argparse
import json
from pathlib import Path
import platform
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'builder'))
from emerald3ds_builder import custom_package as cp


def snapshot(folder):
    return {p.relative_to(folder).as_posix():cp.sha(p) for p in folder.rglob('*') if p.is_file()}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bundle',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();meta=cp.validate_bundle(a.bundle)
    (ROOT/'work').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='f-host-sd-',dir=ROOT/'work') as tmp:
        sd=Path(tmp)
        protected={}
        for app in ('emerald3ds','pokeemerald','emerald3ds-custom-stage-e-v050'):
            folder=sd/'3ds'/app;folder.mkdir(parents=True)
            for n in ('emerald3ds.sav','settings.txt','emerald3ds.clock','emerald3ds.nuzlocke'):
                p=folder/n;p.write_bytes(b'SYNTHETIC LEGACY STATE: '+app.encode()+n.encode());protected[p]=cp.sha(p)
        first=cp.install_bundle(sd,a.bundle);dest=Path(first['destination'])
        state={}
        for n in ('emerald3ds.sav','settings.txt','settings.txt.tmp','emerald3ds.clock',
                  'emerald3ds.clock.tmp','emerald3ds.clock.bak','emerald3ds.nuzlocke',
                  'emerald3ds.nuzlocke.tmp','emerald3ds.nuzlocke.bak','plates.bin','port.log'):
            p=dest/n;p.write_bytes(b'SYNTHETIC F STATE: '+n.encode());state[n]=cp.sha(p)
        before=snapshot(dest)
        second=cp.install_bundle(sd,a.bundle)
        assert snapshot(Path(second['backup']))==before
        for n,h in state.items():assert cp.sha(dest/n)==h
        pre_interrupt=snapshot(dest)
        replace=cp.os.replace
        class ProcessInterrupted(BaseException):pass
        def interrupt(src,target):
            replace(src,target)
            if str(src).endswith('.staging'):raise ProcessInterrupted()
        try:
            with patch.object(cp.os,'replace',side_effect=interrupt):cp.install_bundle(sd,a.bundle)
        except ProcessInterrupted:
            pass
        else:
            raise AssertionError('interruption did not reach directory commit')
        assert cp.recover(sd)
        assert snapshot(dest)==pre_interrupt
        assert not cp.recover(sd)
        for p,h in protected.items():assert cp.sha(p)==h
    report={'evidence':'host filesystem rehearsal; synthetic state; actual compiled engine/data',
        'host':platform.system(),'source_commit':meta['source_commit'],'engine_abi':meta['engine_abi'],
        'first_install':'passed','compatible_update':'passed','whole_folder_backup':'passed',
        'preserved_state_files':len(state),'interruption_after_directory_commit':'passed',
        'rollback':'passed','repeat_recovery':'no pending transaction',
        'legacy_and_e_sentinels':'unchanged','physical_sd':'pending','hardware':'pending'}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
