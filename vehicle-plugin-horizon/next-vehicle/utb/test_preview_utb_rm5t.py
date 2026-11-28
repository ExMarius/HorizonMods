import json,unittest
from pathlib import Path
import update_utb_body as u
P=u.ASSETS/'preview_rm5t'
class RM5PreviewTest(unittest.TestCase):
    def test_dimensions_and_components(self):
        body=json.loads((P/'body.json').read_text());front=json.loads((P/'front_axle_drawbar.json').read_text())
        u.validate(body);u.validate(front)
        b={e['name']:e for e in body['elements']}; f={e['name']:e for e in front['elements']}
        bed=b['bed floor']
        self.assertAlmostEqual((bed['to'][0]-bed['from'][0])*2/16,2.15)
        self.assertAlmostEqual((bed['to'][2]-bed['from'][2])*2/16,4.10)
        self.assertAlmostEqual(.5+(bed['to'][1]-8)*2/16,1.15)
        self.assertAlmostEqual(.5+(b['left upper gate']['to'][1]-8)*2/16,2.15)
        self.assertEqual(5,sum(n.startswith('ladder step ') for n in b))
        self.assertEqual(2,sum(n.startswith('V drawbar ') for n in f))
        self.assertEqual(4,sum(n.startswith('tow eye ') for n in f))
        self.assertIn('hydraulic ram shaft',b);self.assertIn('front axle',f)
        self.assertTrue(any(n.startswith('turntable upper ') for n in b))
        self.assertTrue(any(n.startswith('turntable lower ') for n in f))
        self.assertAlmostEqual(.5+(f['tow eye front']['to'][1]-8)*2/16,.69)
        self.assertAlmostEqual(1.5+(f['tow eye front']['to'][2]-8)*2/16-(-2.05),5.45)

