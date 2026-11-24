import hashlib,json,unittest,struct,zlib,math
from pathlib import Path
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p,refit_police_logan as q
from test_repair_logan_body import archive,overlaps
ROOT=Path(__file__).resolve().parents[2]
class RefitTest(unittest.TestCase):
    def setUp(self):
        b=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}',**{n:'{"credit":"source"}' for n in c.PATHS},'other':'untouched'})
        for fn in (c.build,r.repair,f.build,p.build):b=fn(b,hashlib.sha1(b).hexdigest())
        self.original=b;self.before=c.readzip(b);self.output=q.build(b,hashlib.sha1(b).hexdigest());self.files=c.readzip(self.output)
        self.models=[json.loads(self.files[n]) for n in c.PATHS];self.e=self.models[0]['elements']
    def test_resources_phases_and_coordinates(self):
        self.assertEqual(set(self.files),set(self.before)|q.ADDITIONS)
        for n in self.before:
            if n not in c.PATHS:self.assertEqual(self.before[n],self.files[n])
        self.assertEqual(self.output,q.build(self.original,hashlib.sha1(self.original).hexdigest()))
        with self.assertRaises(ValueError):q.build(self.original)
        for m in self.models[1:]:self.assertEqual(sum(a!=b for a,b in zip(self.e,m['elements'])),1)
        for m in self.models:
            self.assertFalse(overlaps(m['elements']))
            for element in m['elements']:
                for k in ('from','to'):
                    self.assertTrue(all(-16<=v<=32 for v in element[k]))
    def test_static_rear_wheel_clearance_and_floor(self):
        wheel=json.loads((ROOT/'content/assets/gokart/models/block/wheel_sports.json').read_text())
        inner=8-(6.3+1.9)+max(max(abs(a['from'][0]-8),abs(a['to'][0]-8)) for a in wheel['elements'])*.95
        self.assertLess(inner,2.45)
        self.assertIn(c.cube([2.5,1.7,-3.9],[13.5,3.7,1.5],'seat'),self.e)
        self.assertIn(c.cube([2.5,3.7,-5.3],[13.5,8.6,-3.9],'seat'),self.e)
        self.assertIn(c.cube([2.5,0,-10.8],[13.5,1.,27.5],'trim'),self.e)
        self.assertIn(c.cube([2.5,1.35,-8.3],[13.5,1.7,-2.9],'trim'),self.e)
        self.assertIn(c.cube([-.65,1.35,-2.9],[16.65,1.7,17.35],'trim'),self.e)
        self.assertIn(c.cube([-.65,1.699,17.35],[16.65,8.38,18.05],'trim'),self.e)
        for x in (2,4,6,8,10,12,14):self.assertIn(c.cube([x,4.25,3.13],[x+.14,14.65,3.28],'trim'),self.e)
    def test_smoked_windows_are_binary_alpha_with_holes(self):
        png=self.files['assets/daciapolice/textures/item/smoked_glass.png'];self.assertTrue(png.startswith(b'\x89PNG\r\n\x1a\n'))
        off=8;idat=b''
        while off<len(png):
            n=struct.unpack('!I',png[off:off+4])[0];kind=png[off+4:off+8];data=png[off+8:off+8+n];off+=12+n
            if kind==b'IDAT':idat+=data
        raw=zlib.decompress(idat);alpha=[raw[y*65+1+x*4+3] for y in range(16) for x in range(16)]
        self.assertEqual(alpha.count(0),128);self.assertEqual(alpha.count(255),128)
        windows=[e for e in self.e if any(face['texture']=='#smoked' for face in e['faces'].values())]
        self.assertEqual(len(windows),2)
        for w in windows:self.assertEqual(set(w['faces']),{'east','west'})
    def test_custom_animated_steering_and_shaft(self):
        item=json.loads(self.files['assets/vehicle/items/dacia_police_steering.json'])
        self.assertEqual(item['model']['model'],'daciapolice:item/steering')
        model=json.loads(self.files['assets/daciapolice/models/item/steering.json'])
        self.assertIn(c.cube([7.25,.8,7.25],[8.75,7.5,8.75],'trim'),model['elements'])
        # Wheel center at body z=12.8; shaft tip after -65 degree tilt reaches firewall.
        self.assertGreater(12.8 + .73*7.2*math.sin(math.radians(65)),17.35)
        self.assertLess(12.8 + .73*7.2*math.sin(math.radians(65)),18.05)
