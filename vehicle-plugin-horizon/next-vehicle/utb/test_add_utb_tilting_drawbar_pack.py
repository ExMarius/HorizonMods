import hashlib,io,json,unittest,zipfile
import add_utb_tilting_drawbar_pack as p
class DrawbarPackTest(unittest.TestCase):
    def test_only_two_models_are_added(self):
        files={'pack.mcmeta':json.dumps({'pack':{'pack_format':46}}).encode(),'other':b'untouched'}
        for name in p.NAMES:
            for ref in json.loads((p.u.ASSETS/(name+'.json')).read_text())['textures'].values():
                ns,tex=ref.split(':');files[f'assets/{ns}/textures/{tex}.png']=b'texture'
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:
            for n,v in files.items():z.writestr(n,v)
        raw=b.getvalue();out=p.build(raw,hashlib.sha1(raw).hexdigest())
        with zipfile.ZipFile(io.BytesIO(out)) as z:
            self.assertEqual(set(files)|{path for n in p.NAMES for path in (p.MODEL(n),p.ITEM(n))},set(z.namelist()))
            for n,v in files.items():self.assertEqual(z.read(n),v)
        with self.assertRaises(ValueError):p.build(raw)
    def test_split_preserves_original_at_level_and_keeps_axle_horizontal(self):
        original=json.loads((p.u.ASSETS/'tractor_trailer_modern_front.json').read_text())
        axle=json.loads((p.u.ASSETS/(p.NAMES[0]+'.json')).read_text())
        bar=json.loads((p.u.ASSETS/(p.NAMES[1]+'.json')).read_text())
        expected={e['name']:e for e in original['elements']}
        result={e['name']:e for e in axle['elements']}
        self.assertIn('front axle',result);self.assertNotIn('front axle',{e['name'] for e in bar['elements']})
        for e in bar['elements']:
            for key in ('from','to'):e[key][1]=round(e[key][1]+.8,5)
            if 'rotation' in e:e['rotation']['origin'][1]=round(e['rotation']['origin'][1]+.8,5)
            result[e['name']]=e
        self.assertEqual(set(result),set(expected))
        # Round the original too; authoring can contain harmless float artefacts.
        for item in expected.values():
            for key in ('from','to'):item[key]=[round(x,5) for x in item[key]]
            if 'rotation' in item:item['rotation']['origin']=[round(x,5) for x in item['rotation']['origin']]
        for item in result.values():
            for key in ('from','to'):item[key]=[round(x,5) for x in item[key]]
            if 'rotation' in item:item['rotation']['origin']=[round(x,5) for x in item['rotation']['origin']]
        self.assertEqual(result,expected)
