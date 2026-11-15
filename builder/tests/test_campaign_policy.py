"""Validate the production campaign audit against real source and mutations."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
import campaign_audit


class CampaignPolicyTests(unittest.TestCase):
    def setUp(self):
        tree = Path(os.environ.get('EMERALD3DS_EXPANSION_TREE', ROOT/'build/stage-f'))
        source = tree/'src/data/wild_encounters.json'
        if not source.is_file():
            self.skipTest('bootstrap the expansion to audit real campaign tables')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tree = Path(self.tmp.name)
        self.source = self.tree/'src/data/wild_encounters.json'
        self.source.parent.mkdir(parents=True)
        self.data = json.loads(source.read_text())
        self.spec = json.loads((ROOT/'tools/campaign_f.json').read_text())
        self.source.write_text(json.dumps(self.data))

    def test_current_source_has_no_unlisted_table_level_or_rate_edits(self):
        campaign_audit.audit_source(self.tree,self.spec)

    def test_unlisted_rate_and_level_changes_fail(self):
        for mutate in ('rate','level'):
            data=copy.deepcopy(self.data)
            table=data['wild_encounter_groups'][0]['encounters'][0]['land_mons']
            if mutate=='rate':table['encounter_rate']+=1
            else:table['mons'][0]['max_level']+=1
            self.source.write_text(json.dumps(data))
            with self.subTest(mutate=mutate),self.assertRaises(AssertionError):
                campaign_audit.audit_source(self.tree,self.spec)

    def test_overwriting_upstream_timed_slot_fails(self):
        self.spec['placements'][0]['slot']=2
        with self.assertRaisesRegex(AssertionError,'timed slot'):
            campaign_audit.audit_source(self.tree,self.spec)

    def test_replacing_last_original_local_species_fails(self):
        # The mutation is listed, with a matching baseline receipt; the
        # independent local-species preservation rule must still reject it.
        entries=self.data['wild_encounter_groups'][0]['encounters']
        entry=next(e for e in entries if e['map']=='MAP_ROUTE102')
        old=dict(entry['land_mons']['mons'][9]);entry['land_mons']['mons'][9]['species']='SPECIES_PAWMI'
        self.spec['placements'].append({'map':entry['map'],'base_label':entry['base_label'],
            'method':'land_mons','slot':9,'before':old,'species':'SPECIES_PAWMI'})
        self.source.write_text(json.dumps(self.data))
        with self.assertRaises(AssertionError):campaign_audit.audit_source(self.tree,self.spec)


if __name__=='__main__':unittest.main()
