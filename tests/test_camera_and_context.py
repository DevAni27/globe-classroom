from pathlib import Path
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import lesson_engine as e

class CameraContextTests(unittest.TestCase):
 def setUp(self):
  self.path=Path(__file__).resolve().parents[1]/'references/river-civilizations-reviewed.json'
  self.plan=e.load_plan(self.path);self.state=e.initial(self.plan,self.path)
 def test_native_orbit_is_finite_and_returns_to_view(self):
  root=ET.fromstring(e.orbit_kml(self.plan['steps'][0],'ClassroomOrbitTest'))
  flies=root.findall('.//{'+e.GX+'}FlyTo');self.assertEqual(len(flies),14)
  duration=sum(float(f.find('{'+e.GX+'}duration').text) for f in flies)
  self.assertEqual(duration,28)
  self.assertEqual(float(flies[-1].find('.//{'+e.c.K+'}heading').text),self.plan['steps'][0]['camera']['heading'])
  self.assertEqual(float(flies[-1].find('.//{'+e.c.K+'}tilt').text),self.plan['steps'][0]['camera']['tilt'])
  with self.assertRaises(ValueError): e.orbit_kml(self.plan['steps'][0],'bad',float('nan'))
 def test_next_destination_prompts_are_owned_by_engine(self):
  f=dict(learner_summary='Food supports other work.',feedback='You explained the food connection.',next_question='Say next for the recap.',narration='You explained the food connection. Say next for the recap.')
  s=e.transition(self.state,self.plan,'assess','correct','Mechanism understood.',f)
  content=e.content(self.plan,s)
  self.assertIn('explanation 1',content[3]);self.assertTrue(content[4].endswith(content[3]));self.assertNotIn('recap',content[4])
  s=e.transition(s,self.plan,'next')
  for _ in range(2):s=e.transition(s,self.plan,'next')
  self.assertIn('Nile',e.content(self.plan,s)[3])
 def test_context_is_small_and_contains_rubric(self):
  result=e.context(self.plan,self.state)
  self.assertEqual(result['rubric'],self.plan['steps'][0]['rubric'])
  self.assertNotIn('features',result);self.assertLess(len(json.dumps(result)),6000)
 def test_duplicate_question_rejected(self):
  f=dict(learner_summary='Water.',feedback='What about farming?',next_question='How could crops benefit?',narration='Think about farming. How could crops benefit?')
  with self.assertRaises(ValueError):e.validate_feedback(f)
 def test_overlay_preserves_image_aspect(self):
  root=ET.fromstring(e.c.overlay('http://lg1:81/panel.png'))
  size=root.find('.//{'+e.c.K+'}size')
  self.assertEqual(size.attrib['y'],'0');self.assertLess(float(size.attrib['x']),1)
 def test_orbit_stop_cleanup_preserves_lesson_and_other_links(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'kml/globe-classroom').mkdir(parents=True)
   (root/'kmls.txt').write_text('http://lg1:81/other.kml\nhttp://lg1:81/kml/globe-classroom/live.kml\n')
   class LocalRig:
    def __init__(self,unused):pass
    def ssh(self,command,data=None):
     command=command.replace('/var/www/html',str(root)).replace('/tmp/query.txt',str(root/'query.txt'))
     command=command.replace('sleep 4;','true;').replace('sleep 1','true')
     return subprocess.run(['bash','-c',command],input=data,capture_output=True,check=True).stdout.decode().strip()
    def copy(self,paths):
     for p in paths:shutil.copyfile(p,root/'kml/globe-classroom'/p.name)
   with patch.object(e.c,'Rig',LocalRig),patch.object(e.c,'connection',return_value={}),patch.object(e.c,'STATE',root/'state.json'):
    before=copy.deepcopy(self.state)
    e.camera_action(self.plan,self.state,'orbit')
    self.assertTrue((root/'query.txt').read_text().startswith('playtour=ClassroomOrbit'))
    self.assertEqual(self.state['index'],before['index']);self.assertEqual(self.state['records'],before['records'])
    e.camera_action(self.plan,self.state,'stop')
    self.assertEqual((root/'query.txt').read_text().strip(),'exittour=true')
    self.assertNotIn('motion',self.state)
    self.assertEqual((root/'kmls.txt').read_text(),'http://lg1:81/other.kml\nhttp://lg1:81/kml/globe-classroom/live.kml\n')
    e.camera_action(self.plan,self.state,'return-view')
    ET.fromstring((root/'query.txt').read_text().split('=',1)[1])

if __name__=='__main__':unittest.main()
