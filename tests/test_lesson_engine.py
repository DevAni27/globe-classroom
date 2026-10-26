import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
import lesson_engine as e

PLAN_PATH=SCRIPTS.parent/'references/rain-shadow.json'

class LessonEngineTests(unittest.TestCase):
    def setUp(self):
        self.plan=e.load_plan(PLAN_PATH)
        self.state=e.initial(self.plan,PLAN_PATH)
    def test_reference_structure_and_no_advance_before_answer(self):
        with self.assertRaises(ValueError): e.transition(self.state,self.plan,'next')
    def test_explanation_is_staged_before_transfer(self):
        s=e.transition(self.state,self.plan,'assess','correct','Moist air rises, cools and condenses on incoming side.')
        self.assertEqual(s['phase'],'explain'); self.assertEqual(s['beat_index'],0)
        s=e.transition(s,self.plan,'next'); self.assertEqual(s['beat_index'],1)
        s=e.transition(s,self.plan,'next'); self.assertEqual(s['beat_index'],2)
        s=e.transition(s,self.plan,'next'); self.assertEqual(s['index'],1); self.assertEqual(s['phase'],'question')
    def test_unclear_does_not_count_as_wrong_or_reveal(self):
        s=e.transition(self.state,self.plan,'assess','unclear','Learner response is ambiguous.')
        self.assertEqual(s['phase'],'partial')
        self.assertEqual(s['records']['western-ghats'][0]['verdict'],'unclear')
    def test_reveal_and_hint_remain_distinct_from_correctness(self):
        s=e.transition(self.state,self.plan,'hint')
        self.assertEqual(s['records']['western-ghats'],[])
        s=e.transition(s,self.plan,'reveal')
        self.assertEqual(s['records']['western-ghats'][0]['verdict'],'revealed')
    def test_invalid_geometry_and_false_source_reference_rejected(self):
        for mutate in [lambda p:p['steps'][0]['camera'].update(latitude=float('nan')),lambda p:p['steps'][0].update(source_ids=['unknown']),lambda p:p['steps'][0]['features'][0].update(coordinates=[400,0])]:
            p=copy.deepcopy(self.plan); mutate(p)
            with self.assertRaises(ValueError): e.validate(p)
    def test_assess_requires_evidence(self):
        with self.assertRaises(ValueError): e.transition(self.state,self.plan,'assess','correct','')
    def test_progressive_geometry_and_complete_camera(self):
        initial=e.geometry(self.plan['steps'][0],self.state)
        s=e.transition(self.state,self.plan,'assess','correct','Causal mechanism understood.')
        reveal=e.geometry(self.plan['steps'][0],s)
        count=lambda data:len(ET.fromstring(data).findall('.//{%s}Placemark'%e.c.K))
        self.assertGreater(count(reveal),count(initial))
        s=e.transition(e.transition(s,self.plan,'next'),self.plan,'next')
        self.assertGreater(count(e.geometry(self.plan['steps'][0],s)),count(reveal))
        self.assertTrue(e.view_xml(self.plan['steps'][0]).endswith('</LookAt>'))
    def test_non_rainfall_vocabulary_and_polygon_supported(self):
        # Structural fixture only: not a factual lesson or learner-facing sample.
        p=copy.deepcopy(self.plan)
        p['topic']='Urban development'; p['title']='A structural compatibility test'
        p['steps'][0]['features']=[dict(type='polygon',label='Schematic study area',color='green',geometry_kind='schematic',show='question',coordinates=[[73,18],[74,18],[74,19],[73,18]])]
        e.validate(p)
        self.assertIsNotNone(ET.fromstring(e.geometry(p['steps'][0],self.state)).find('.//{%s}Polygon'%e.c.K))
    def test_dynamic_panels_render_every_phase(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory:
            for phase in ['question','hint','partial','explain','recap']:
                s=copy.deepcopy(self.state); s['phase']=phase
                e.render(self.plan,s,Path(directory)/phase)
                with Image.open(Path(directory)/phase/'panel.png') as im: self.assertEqual(im.size,(1920,1080))

if __name__=='__main__': unittest.main()
