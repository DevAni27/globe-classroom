import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import subprocess
import shutil
import os
import xml.etree.ElementTree as ET

spec=importlib.util.spec_from_file_location('classroom',Path(__file__).resolve().parents[1]/'scripts/classroom.py')
c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)

def initial():
    return {'stage':'question','attempts':{'india':0,'transfer':0},'assessments':[]}

class ClassroomTests(unittest.TestCase):
    def test_all_scenes_are_valid_xml_and_camera_is_complete(self):
        for stage in c.STAGES:
            ET.fromstring(c.scene(stage))
            root=ET.fromstring(c.camera(stage))
            self.assertEqual(root.tag,'LookAt')
            self.assertIsNotNone(root.find('longitude'))
            self.assertTrue(c.camera(stage).endswith('</LookAt>'))
            self.assertTrue((c.ROOT/'assets'/(stage+'.png')).exists())
    def test_opening_has_no_airflow_answer_reveal(self):
        root=ET.fromstring(c.scene('question'))
        self.assertEqual(len(root.findall('.//{%s}Placemark'%c.K)),2)
        self.assertGreater(len(ET.fromstring(c.scene('hint')).findall('.//{%s}Placemark'%c.K)),2)
    def test_partial_answer_does_not_advance_to_explanation(self):
        s=c.transition(initial(),'assess','partial','A only')
        self.assertEqual(s['stage'],'partial')
        with self.assertRaises(RuntimeError): c.transition(s,'next')
    def test_wrong_answer_gets_hint_then_correct_can_advance(self):
        s=c.transition(initial(),'assess','incorrect','wrong cause')
        self.assertEqual(s['stage'],'hint')
        s=c.transition(s,'assess','correct','causal explanation')
        self.assertEqual(s['stage'],'explain')
        self.assertEqual(s['attempts']['india'],2)
        self.assertEqual(c.transition(s,'next')['stage'],'transfer')
    def test_transfer_and_recap_require_explanation(self):
        s=initial(); s['stage']='transfer'
        s=c.transition(s,'assess','partial','B only')
        self.assertEqual(s['stage'],'transfer_partial')
        s=c.transition(s,'assess','correct','air lifted on east')
        self.assertEqual(s['stage'],'transfer_explain')
        self.assertEqual(c.transition(s,'next')['stage'],'recap')
    def test_reveal_is_distinct_from_independent_understanding(self):
        s=c.transition(initial(),'reveal')
        self.assertEqual(s['assessments'][-1]['verdict'],'revealed')
        self.assertEqual(s['attempts']['india'],0)
    def test_networklink_refresh_and_escaped_overlay_url(self):
        root=ET.fromstring(c.networklink())
        self.assertEqual(root.find('.//{%s}refreshInterval'%c.K).text,'2')
        url='http://lg1:81/panel.png?a=1&b=2'
        root=ET.fromstring(c.overlay(url))
        self.assertEqual(root.find('.//{%s}href'%c.K).text,url)
    def test_state_roundtrip_is_private(self):
        old=c.STATE
        with tempfile.TemporaryDirectory() as d:
            try:
                c.STATE=Path(d)/'state.json'; c.save_state(initial())
                self.assertEqual(c.read_state(),initial())
                self.assertEqual(c.STATE.stat().st_mode & 0o777,0o600)
            finally: c.STATE=old
    def test_deployment_and_restore_preserve_other_content(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory); web=base/'web'; home=base/'home'
            (web/'kml').mkdir(parents=True); home.mkdir()
            originals={'kmls.txt':b'http://lg1:81/existing.kml\n','kml/slave_2.kml':b'RIGHT BEFORE','kml/slave_3.kml':b'LEFT BEFORE'}
            for filename,data in originals.items(): (web/filename).write_bytes(data)
            class LocalRig:
                def __init__(self,d): self.d=d
                def ssh(self,command,data=None):
                    if command=='hostname': return 'test-lg1'
                    if command=='printf "%s" "$HOME"': return str(home)
                    command=command.replace('/var/www/html',str(web)).replace('/tmp/query.txt',str(base/'query.txt')).replace('sleep 3','true')
                    if data: data=data.replace(b'/var/www/html',str(web).encode())
                    result=subprocess.run(['bash','-c',command],input=data,capture_output=True,check=True)
                    return result.stdout.decode().strip()
                def copy(self,paths):
                    for p in paths: shutil.copyfile(p,web/'kml/globe-classroom'/p.name)
            with patch.object(c,'Rig',LocalRig), patch.object(c,'connection',return_value={'username':'lg','screens':3}), patch.object(c,'STATE',base/'state.json'):
                s=initial(); c.deploy(s)
                self.assertIn('existing.kml',(web/'kmls.txt').read_text())
                self.assertIn('/globe-classroom/live.kml',(web/'kmls.txt').read_text())
                ET.fromstring((web/'kml/globe-classroom/scene.kml').read_bytes())
                ET.fromstring((base/'query.txt').read_text().split('=',1)[1])
                first_backup=s['backup']
                s=c.transition(s,'hint'); c.deploy(s)
                self.assertEqual(s['backup'],first_backup)
                self.assertEqual((web/'kmls.txt').read_text().count('/globe-classroom/live.kml'),1)
                c.restore(s)
                for filename,data in originals.items(): self.assertEqual((web/filename).read_bytes(),data)

if __name__=='__main__': unittest.main()
