import hashlib
import importlib.util
import io
import unittest
import zipfile
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'deploy/falix_install_horizon.py'
spec = importlib.util.spec_from_file_location('install_horizon', p)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
URL='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-123/HorizonOffRoader-1.21.4.zip'
CONFIG=('resource-pack:\n  url: "https://example.test/MrCrayfishVehiclePlugin-resource-pack-1.21.4-r39.zip"\n'
        '  sha1: "'+m.OLD_PACK+'"\n  resend-on-join: false\nphysics:\n  global-speed-limit: 100\n').encode()
def pack():
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z:
        z.writestr('pack.mcmeta','{"pack":{"pack_format":46}}')
        z.writestr('assets/horizonvehicles/items/off_roader_body_part_00.json','{}')
    return b.getvalue()

class Fake:
    def __init__(self):
        self.files={'/plugins/'+m.f.NAME:b'old jar','/server.properties':b'properties'}
        for name in m.NAMES: self.files['/plugins/MrCrayfishVehiclePlugin/'+name]=CONFIG if name=='config.yml' else name.encode()
        self.props={'resource-pack':'old-url','resource-pack-sha1':m.OLD_PACK,'resource-pack-id':'old-id','require-resource-pack':'true'}
        self.fail_new_jar=False
    def status(self): return 'offline'
    def download(self,path): return self.files[path]
    def upload(self,directory,name,content):
        path=directory.rstrip('/')+'/'+name
        if self.fail_new_jar and path=='/plugins/'+m.f.NAME and content==b'new jar': raise RuntimeError('simulated upload failure')
        self.files[path]=content
    def api(self,path,data=None,method=None):
        if path.startswith('/files?directory=%2Fversions'): return [{'name':'1.21.4'}]
        if path.startswith('/files?'): return [{'name':n} for n in m.NAMES]
        if path=='/properties' and method=='PUT': self.props.update(data['properties']); return None
        if path=='/properties': return [{'key':k,'value':v} for k,v in self.props.items()]
        raise AssertionError(path)

class DeployTest(unittest.TestCase):
    def setUp(self):
        self.old=m.OLD_JAR; m.OLD_JAR=hashlib.sha256(b'old jar').hexdigest()
        self.api=Fake()
    def tearDown(self): m.OLD_JAR=self.old
    def test_config_preserves_other_settings(self):
        result=m.replace_pack(CONFIG,URL,'a'*40)
        self.assertIn(b'  resend-on-join: false',result)
        self.assertIn(b'physics:\n  global-speed-limit: 100',result)
        self.assertIn(URL.encode(),result)
    def test_rejects_unexpected_pack(self):
        with self.assertRaises(ValueError): m.replace_pack(CONFIG.replace(b'r39.zip',b'r41.zip'),URL,'a'*40)
    def test_deploy_backups_before_changes(self):
        m.deploy(self.api,b'new jar',pack(),URL,'123')
        self.assertEqual(self.api.files['/plugins/'+m.f.NAME],b'new jar')
        self.assertEqual(self.api.files['/mcv-before-horizon-123-plugin.jar.bak'],b'old jar')
        self.assertEqual(self.api.files['/mcv-before-horizon-123-config.yml.bak'],CONFIG)
        self.assertEqual(self.api.props['resource-pack'],URL)
    def test_garage_data_backed_up_and_unchanged(self):
        old_names=m.NAMES
        try:
            m.NAMES=old_names | {'garages.yml'}
            api=Fake()
            original=api.files['/plugins/MrCrayfishVehiclePlugin/garages.yml']
            m.deploy(api,b'new jar',pack(),URL,'124')
            self.assertEqual(api.files['/mcv-before-horizon-124-garages.yml.bak'],original)
            self.assertEqual(api.files['/plugins/MrCrayfishVehiclePlugin/garages.yml'],original)
        finally:
            m.NAMES=old_names

    def test_failed_upload_rolls_back_all_three(self):
        self.api.fail_new_jar=True
        with self.assertRaises(RuntimeError): m.deploy(self.api,b'new jar',pack(),URL,'123')
        self.assertEqual(self.api.files['/plugins/'+m.f.NAME],b'old jar')
        self.assertEqual(self.api.files['/plugins/MrCrayfishVehiclePlugin/config.yml'],CONFIG)
        self.assertEqual(self.api.props['resource-pack-sha1'],m.OLD_PACK)
        self.assertEqual(self.api.props['resource-pack'],'old-url')

if __name__=='__main__': unittest.main()
