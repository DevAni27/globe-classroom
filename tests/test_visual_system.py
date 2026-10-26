from pathlib import Path
import copy
import sys
import unittest
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import lesson_engine as e
import visuals

class VisualSystemTests(unittest.TestCase):
 def setUp(self):
  self.path=Path(__file__).resolve().parents[1]/'references/river-civilizations-reviewed.json'
  self.plan=e.load_plan(self.path);self.state=e.initial(self.plan,self.path)
 def test_standard_view_is_north_up_with_explicit_rotation_opt_in(self):
  step=copy.deepcopy(self.plan['steps'][0]);step['camera']['heading']=270
  self.assertEqual(ET.fromstring(e.view_xml(step)).find('heading').text,'0')
  step['camera']['allow_rotation']=True
  self.assertEqual(ET.fromstring(e.view_xml(step)).find('heading').text,'270')
 def test_orbit_headings_remain_distinct_under_north_up_default(self):
  root=ET.fromstring(e.orbit_kml(self.plan['steps'][0],'Test'))
  headings=[v.text for v in root.findall('.//{'+e.c.K+'}heading')]
  self.assertGreater(len(set(headings)),10)
 def test_polygons_use_one_line_style_and_only_locations_have_map_labels(self):
  s=e.transition(self.state,self.plan,'assess','correct','Mechanism explained.')
  root=ET.fromstring(e.geometry(self.plan['steps'][0],s))
  for style in root.findall('.//{'+e.c.K+'}Style'):
   self.assertLessEqual(len(style.findall('{'+e.c.K+'}LineStyle')),1)
  names=root.findall('.//{'+e.c.K+'}name')
  self.assertEqual(len(names),2)
 def test_arrowhead_stays_small_even_for_long_authored_path(self):
  root,doc=e.c.document();visuals.arrow(doc,[(130,35,1000),(143,38,1000)],e.COLORS['cyan'],650000)
  coordinates=root.findall('.//{'+e.c.K+'}coordinates')[-1].text
  points=[[float(v) for v in x.split(',')] for x in coordinates.split()]
  self.assertLess(abs(points[0][0]-points[1][0]),.2)
  self.assertLess(abs(points[0][1]-points[1][1]),.2)

if __name__=='__main__':unittest.main()
