import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import lesson_engine as e

class TurnFeedbackTests(unittest.TestCase):
    def setUp(self):
        self.path=Path(__file__).resolve().parents[1]/'references/rain-shadow.json'
        self.plan=e.load_plan(self.path)
        self.state=e.initial(self.plan,self.path,True)
        self.feedback=dict(learner_summary='Mountains block clouds.',feedback='You noticed the mountain barrier. Now consider what happens as moist air rises.',next_question='How might rising air change temperature?',narration='You noticed the mountain barrier. Let us connect that to rising air. How might rising air change temperature?')
    def test_persisted_feedback_drives_panel_and_voice(self):
        s=e.transition(self.state,self.plan,'assess','partial','Learner identifies barrier but not cooling.',self.feedback)
        s=json.loads(json.dumps(s))
        content=e.content(self.plan,s)
        self.assertIn(self.feedback['learner_summary'],content[2])
        self.assertIn(self.feedback['feedback'],content[2])
        self.assertEqual(content[3],self.feedback['next_question'])
        self.assertEqual(content[4],self.feedback['narration'])
        self.assertEqual(s['index'],0); self.assertTrue(s['voice'])
        self.assertEqual(s['records']['western-ghats'][0]['feedback'],self.feedback)
        with self.assertRaises(ValueError): e.transition(s,self.plan,'next')
        with tempfile.TemporaryDirectory() as d:
            e.render(self.plan,s,Path(d))
            self.assertEqual((Path(d)/'narration.txt').read_text(),self.feedback['narration'])
    def test_correct_feedback_clears_on_next_beat(self):
        s=e.transition(self.state,self.plan,'assess','correct','Learner explains cooling and condensation.',self.feedback)
        self.assertEqual(s['phase'],'feedback')
        s=e.transition(s,self.plan,'next')
        self.assertEqual(s['beat_index'],0)
        self.assertNotIn('turn_feedback',s)
        self.assertTrue(e.content(self.plan,s)[4].startswith(self.plan['steps'][0]['explanation'][0]['narration']))
    def test_new_assessment_replaces_old_feedback(self):
        s=e.transition(self.state,self.plan,'assess','partial','Incomplete mechanism.',self.feedback)
        s=e.transition(s,self.plan,'assess','correct','Mechanism now explained.')
        self.assertNotIn('turn_feedback',s)
    def test_mismatched_voice_or_oversized_feedback_rejected(self):
        for changes in [dict(narration='An unrelated question?'),dict(feedback='x'*301)]:
            f={**self.feedback,**changes}
            with self.assertRaises(ValueError): e.transition(self.state,self.plan,'assess','partial','Incomplete.',f)
    def test_maximum_feedback_renders_without_clipping(self):
        f=dict(learner_summary=('A reasonable learner idea. '*6)[:140],feedback=('A contextual teaching connection. '*10)[:300],next_question=('What follows from this connection? '*6)[:200],narration='')
        f['narration']='Consider the evidence. '+f['next_question']
        s=e.transition(self.state,self.plan,'assess','partial','Incomplete.',f)
        with tempfile.TemporaryDirectory() as d: e.render(self.plan,s,Path(d))
    def test_old_partial_state_retains_original_question_context(self):
        s=e.transition(self.state,self.plan,'assess','partial','Incomplete.')
        self.assertEqual(e.content(self.plan,s)[2],self.plan['steps'][0]['question'])

if __name__=='__main__': unittest.main()
