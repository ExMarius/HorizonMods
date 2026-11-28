import copy, hashlib, io, json, unittest, zipfile
import custom_logan_body as c, install_user_logan_body as edit

class UserLoganTest(unittest.TestCase):
    def test_upload_geometry_phases_and_pack_scope(self):
        user=json.loads(edit.INPUT.read_text()); files={p:b'old' for p in c.PATHS}
        for name in list(user['textures'].values())+['daciapolice:item/siren_red_dim','daciapolice:item/horizon_siren_blue']:
            files['assets/daciapolice/textures/item/'+name.split('/')[-1]+'.png']=b'texture'
        files['untouched']=b'unchanged'; stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as z:
            for k,v in files.items():z.writestr(k,v)
        data=stream.getvalue(); output=edit.build(data,hashlib.sha1(data).hexdigest()); after=c.readzip(output)
        for k in files:
            if k not in c.PATHS:self.assertEqual(after[k],files[k])
        models=[json.loads(after[p]) for p in c.PATHS]
        for model in models:
            self.assertEqual(len(model['elements']),len(user['elements']))
            for a,b in zip(model['elements'],user['elements']):
                for key in ('from','to'):self.assertEqual(a.get(key),b.get(key))
                self.assertEqual(a.get('rotation'),None if b.get('rotation',{}).get('angle')==0 else b.get('rotation'))
        for model,colors in zip(models,(('#blue_dim','#red_dim'),('#blue','#red_dim'),('#blue_dim','#red'))):
            for bound,color in zip((edit.BLUE,edit.RED),colors):
                e=next(e for e in model['elements'] if (tuple(e['from']),tuple(e['to']))==bound)
                self.assertEqual({f['texture'] for f in e['faces'].values()},{color})
        self.assertEqual(edit.build(data,hashlib.sha1(data).hexdigest()),output)
        with self.assertRaises(ValueError):edit.build(data)
    def test_missing_texture_fails_before_install(self):
        with self.assertRaises(ValueError):edit.variants(json.loads(edit.INPUT.read_text()),{})
