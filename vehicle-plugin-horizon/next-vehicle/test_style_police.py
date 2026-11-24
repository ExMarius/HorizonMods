import hashlib, io, json, unittest, zipfile
from pathlib import Path
import prepare_police, style_police
ROOT=Path(__file__).resolve().parents[2]
def archive(files):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z:
        for n,v in files.items():z.writestr(n,v)
    return b.getvalue()
class StyleTest(unittest.TestCase):
    def test_style_and_compatibility(self):
        base=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}','assets/unchanged':'preserve'})
        source=(ROOT/'paper-vehicles/transfer/vehicle-reference/vehicle-fara-mentiune.zip').read_bytes()
        previous=prepare_police.prepare(base,source,hashlib.sha1(base).hexdigest())
        result=style_police.style(previous,hashlib.sha1(previous).hexdigest())
        before=prepare_police.readzip(previous); after=prepare_police.readzip(result)
        for k,v in before.items():
            if k not in (style_police.BODY,style_police.SOUNDS):self.assertEqual(v,after[k],k)
        old=json.loads(before[style_police.BODY]);new=json.loads(after[style_police.BODY])
        self.assertEqual(old['elements'],new['elements'][:268]);self.assertEqual(len(new['elements']),271)
        for phase in (0,1):
            variant=json.loads(after[f'assets/daciapolice/models/item/body_flash_{phase}.json'])
            for index in range(271):
                if index not in (224,227):self.assertEqual(new['elements'][index],variant['elements'][index])
        sounds=json.loads(after[style_police.SOUNDS]);self.assertTrue(all(f'sirena_{i}' in sounds for i in range(16)))
        self.assertEqual(result,style_police.style(previous,hashlib.sha1(previous).hexdigest()))
        with self.assertRaises(ValueError):style_police.style(previous)
