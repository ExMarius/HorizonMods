import hashlib,json,math,unittest,itertools
from pathlib import Path
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p,refit_police_logan as q,finish_police_logan as t,detail_police_logan as d,complete_police_logan as u,restore_police_wheels as v
from test_repair_logan_body import archive,overlaps
ROOT=Path(__file__).resolve().parents[2]
def corners(e):
    angle=math.radians(e.get('rotation',{}).get('angle',0));co=math.cos(angle);si=math.sin(angle)
    out=[]
    for x,y,z in itertools.product(*zip(e['from'],e['to'])):
        y-=8;z-=8;out.append((round(x,5),round(8+y*co-z*si,5),round(8+y*si+z*co,5)))
    return sorted(out)
class RestoreTest(unittest.TestCase):
    def setUp(self):
        b=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}',**{n:'{"credit":"source"}' for n in c.PATHS},'other':'untouched'})
        for fn in (c.build,r.repair,f.build,p.build,q.build,t.build,d.build,u.build):b=fn(b,hashlib.sha1(b).hexdigest())
        self.orig=b;self.before=c.readzip(b);self.result=v.build(b,hashlib.sha1(b).hexdigest());self.after=c.readzip(self.result)
        self.models=[json.loads(self.after[n]) for n in c.PATHS];self.e=self.models[0]['elements']
    def test_tire_is_complete_exact_horizon_geometry_and_vanilla_legal(self):
        old=json.loads((ROOT/'content/assets/gokart/models/block/wheel_sports.json').read_text())
        new=json.loads(self.after['assets/daciapolice/models/item/wheel_complete.json'])
        self.assertEqual(len(old['elements']),17);self.assertEqual(len(new['elements']),17)
        for i,(a,b) in enumerate(zip(old['elements'],new['elements'])):
            self.assertEqual(corners(a),corners(b),f'wheel piece {i}')
            if i not in (6,7):self.assertEqual(a,b)
            self.assertIn(b.get('rotation',{}).get('angle',0),(-45,-22.5,0,22.5,45))
        item=json.loads(self.after['assets/daciapolice/items/wheel_complete.json'])
        self.assertEqual(item['model']['model'],'daciapolice:item/wheel_complete')
    def test_horizon_style_steering_has_attached_shaft(self):
        m=json.loads(self.after[t.STEER]);source=json.loads((ROOT/'content/assets/gokart/models/block/go_kart_steering_wheel.json').read_text())
        self.assertEqual(len(m['elements']),len(source['elements'])+1)
        self.assertIn(c.cube([7.35,-2.3,7.35],[8.65,7.5,8.65],'frame'),m['elements'])
        self.assertTrue(all(e.get('rotation',{}).get('angle',0) in (-45,-22.5,0,22.5,45) for e in m['elements']))
    def test_liners_floor_roof_and_sirens(self):
        for x0,x1 in ((-.65,2.44),(13.56,16.65)):
            for a,b in ((-11.1,-2.9),(19.25,28.65)):
                self.assertIn(c.cube([x0,5.20,a],[x1,5.44,b],'trim'),self.e)
            for a,b in ((-11.3,-11.1),(19,19.25),(28.65,28.85)):
                self.assertIn(c.cube([x0,1.35,a],[x1,5.2,b],'trim'),self.e)
        for m in self.models:
            self.assertFalse(overlaps(m['elements']))
            self.assertTrue(all(-16<=v<=32 for e in m['elements'] for k in ('from','to') for v in e[k]))
        for m in self.models[1:]:self.assertEqual(sum(a!=b for a,b in zip(self.e,m['elements'])),1)
    def test_pack_changes_scoped_and_deterministic(self):
        self.assertEqual(set(self.after),set(self.before)|v.NEW)
        for n in self.before:
            if n not in set(c.PATHS)|{t.STEER}:self.assertEqual(self.before[n],self.after[n])
        self.assertEqual(self.result,v.build(self.orig,hashlib.sha1(self.orig).hexdigest()))
        with self.assertRaises(ValueError):v.build(self.orig)
