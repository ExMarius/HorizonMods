#!/usr/bin/env python3
"""Add only the Horizon kart's own models and textures to a verified pack."""
import argparse,hashlib,importlib.util,io,json,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE_SHA1='db14f4d396fb950567f1ec52ac5d27d417bdb26c'
PARTS=('go_kart_body','engine_iron','engine_gold','engine_diamond')
spec=importlib.util.spec_from_file_location('kart_converter',ROOT/'paper-vehicles/tools/compile_go_kart.py')
converter=importlib.util.module_from_spec(spec);spec.loader.exec_module(converter)

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected installed resource pack')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip():raise ValueError('invalid base pack')
        if len(z.namelist())!=len(set(z.namelist())):raise ValueError('duplicate pack entries')
        files={n:z.read(n) for n in z.namelist()}
    converter.PARTS=PARTS
    converter.MODEL_OVERRIDES={"go_kart_body":ROOT/"vehicle-plugin-horizon/next-vehicle/assets/user-edits/go_kart_body.json"}
    with tempfile.TemporaryDirectory() as td:
        root=Path(td);desc=converter.build(root)
        for path in root.rglob('*'):
            if not path.is_file():continue
            name=path.relative_to(root).as_posix()
            if not name.startswith('assets/horizonvehicles/'):continue
            content=path.read_bytes()
            if name in files:
                if files[name]!=content:raise ValueError('refusing to replace existing asset '+name)
                continue
            if '/models/item/go_kart_body_part_' in name:
                model=json.loads(content)
                # Paint only the Horizon body texture, never seats, rubber, or metal.
                for e in model['elements']:
                    for f in e.get('faces',{}).values():
                        if f['texture']=='#body':f['tintindex']=0
                content=json.dumps(model,separators=(',',':')).encode()
            if '/items/go_kart_body_part_' in name:
                item=json.loads(content);item['model']['tints']=[{'type':'minecraft:dye','default':-1}];content=json.dumps(item,separators=(',',':')).encode()
            files[name]=content
        expected_desc=json.loads((ROOT/'vehicle-plugin-horizon/paper-plugin/src/main/resources/horizon/off_roader_parts.json').read_text())['parts']
        for name in ('go_kart_body','engine_iron'):
            if json.loads(json.dumps(desc['parts'][name]))!=expected_desc[name]:raise ValueError('renderer descriptors mismatch '+name)
        # Motor tiers must share group pivots, to switch model without moving parts.
        for tier in ('engine_gold','engine_diamond'):
            for a,b in zip(desc['parts']['engine_iron'],desc['parts'][tier]):
                if a['rotation']!=b['rotation'] or a['element_count']!=b['element_count']:raise ValueError('engine tier geometry differs')
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for name,value in sorted(files.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,value)
    return out.getvalue()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.base.resolve()==a.output.resolve():p.error('output must differ')
    result=build(a.base.read_bytes());a.output.write_bytes(result);print('SHA-1',hashlib.sha1(result).hexdigest())
if __name__=='__main__':main()
