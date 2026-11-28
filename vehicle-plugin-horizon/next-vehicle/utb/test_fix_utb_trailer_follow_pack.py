import hashlib,io,json,unittest,zipfile,math
import fix_utb_trailer_follow_pack as p
class FollowPackTest(unittest.TestCase):
    def test_only_two_models_change(self):
        q=p.patch;sources={q.MODEL:q.SOURCE,q.BODY:q.BODY_SOURCE}
        files={'pack.mcmeta':json.dumps({'pack':{'pack_format':46}}).encode(),'other':b'untouched',q.MODEL:b'old',q.BODY:b'old'}
        for path in sources.values():
            for ref in json.loads(path.read_bytes())['textures'].values():
                ns,tex=ref.split(':');files[f'assets/{ns}/textures/{tex}.png']=b'texture'
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:
            for n,v in files.items():z.writestr(n,v)
        raw=b.getvalue();result=p.build(raw,hashlib.sha1(raw).hexdigest())
        with zipfile.ZipFile(io.BytesIO(result)) as z:
            self.assertEqual(set(files),set(z.namelist()))
            for n,v in files.items():self.assertEqual(z.read(n),sources[n].read_bytes() if n in sources else v)
        with self.assertRaises(ValueError):p.build(raw)
    def test_front_links_join_axle_to_v_arms(self):
        q=p.patch;m=json.loads(q.SOURCE.read_text());q.u.validate(m);e={x['name']:x for x in m['elements']}
        for side,sign in [('left',1),('right',-1)]:
            link=e[side+' narrow drawbar axle link'];arm=e[f'V drawbar {sign} coupling slope 0'];axis=e['front axle']
            for i in range(3):self.assertLessEqual(max(link['from'][i],axis['from'][i]),min(link['to'][i],axis['to'][i]))
            a=math.radians(arm['rotation']['angle']);pivot=arm['rotation']['origin'];z=arm['from'][2]-pivot[2]
            center_x=pivot[0]+z*math.sin(a);center_z=pivot[2]+z*math.cos(a)
            self.assertGreater(center_x+0.5,link['from'][0]);self.assertLess(center_x-0.5,link['to'][0])
            self.assertGreater(center_z+0.2,link['from'][2]);self.assertLess(center_z-0.2,link['to'][2])
            self.assertLessEqual(max(link['from'][1],arm['from'][1]),min(link['to'][1],arm['to'][1]))
