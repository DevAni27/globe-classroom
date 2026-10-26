import copy
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import lesson_engine as e

class SubmissionFlowTests(unittest.TestCase):
 def setUp(self):
  self.path=Path(__file__).resolve().parents[1]/'references/river-civilizations-reviewed.json'
  self.plan=e.load_plan(self.path);self.state=e.initial(self.plan,self.path)
  self.feedback=dict(learner_summary='Extra food supports other work.',feedback='You connected farming to people doing other work.',next_question='Say next to examine how water reached crops.',narration='You connected farming to people doing other work. Say next to examine how water reached crops.')
 def test_adaptation_then_all_beats_then_transfer_and_recap(self):
  s=e.transition(self.state,self.plan,'assess','partial','Only drinking water mentioned.',self.feedback)
  self.assertEqual(s['phase'],'partial');self.assertEqual(s['index'],0)
  with self.assertRaises(ValueError):e.transition(s,self.plan,'next')
  s=e.transition(s,self.plan,'assess','correct','Explained irrigation, extra food and other work.',self.feedback)
  self.assertEqual(s['phase'],'feedback')
  for beat in range(3):
   s=e.transition(s,self.plan,'next')
   self.assertEqual(s['beat_index'],beat);self.assertEqual(s['index'],0)
  s=e.transition(s,self.plan,'next');self.assertEqual(s['index'],1);self.assertEqual(s['phase'],'question')
  self.assertIn('too little',e.content(self.plan,s)[2])
  with self.assertRaises(ValueError):e.transition(s,self.plan,'next')
  s=e.transition(s,self.plan,'assess','correct','Applies water to crops and food dependence.',self.feedback)
  for _ in range(3):s=e.transition(s,self.plan,'next')
  self.assertEqual(s['phase'],'recap')
 def test_legacy_correct_feedback_does_not_skip_beat_zero(self):
  s=e.transition(self.state,self.plan,'assess','correct','Causal reasoning.',self.feedback)
  s['phase']='explain' # persisted v0.2.1 compatibility
  s=e.transition(s,self.plan,'next');self.assertEqual(s['beat_index'],0)
 def test_reviewed_lesson_panels_and_xml_at_every_beat(self):
  with tempfile.TemporaryDirectory() as d:
   for idx,step in enumerate(self.plan['steps']):
    for phase in ['question','partial','hint','explain','recap']:
     for beat in range(len(step['explanation'])):
      s={**self.state,'index':idx,'phase':phase,'beat_index':beat}
      dest=Path(d)/str(idx)/phase/str(beat);e.render(self.plan,s,dest)
      ET.fromstring((dest/'scene.kml').read_bytes())
 def test_labels_do_not_reveal_hidden_geometry(self):
  data=e.geometry(self.plan['steps'][0],self.state)
  self.assertFalse(ET.fromstring(data).findall('.//{'+e.c.K+'}Polygon'))
  s=e.transition(self.state,self.plan,'assess','correct','Explained mechanism.')
  self.assertTrue(ET.fromstring(e.geometry(self.plan['steps'][0],s)).findall('.//{'+e.c.K+'}Polygon'))

if __name__=='__main__':unittest.main()
