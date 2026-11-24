#!/usr/bin/env python3
"""Apply the user's four Go-Kart fin edits to the installed Horizon pack."""
import argparse,copy,hashlib,io,json,tempfile,zipfile
from pathlib import Path
import add_horizon_kart_pack as k
ROOT=k.ROOT
BASE_SHA1='17f288e0a4abd966c161150fd10edf2502249272'
USER=ROOT/'vehicle-plugin-horizon/next-vehicle/assets/user-edits/go_kart_body.json'
PARTS=(3,4,6,7)

def models(source):
    k.converter.PARTS=('go_kart_body',);k.converter.MODEL_OVERRIDES={} if source is None else {'go_kart_body':source}
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp);desc=k.converter.build(root)
        result={}
        for i in PARTS:
            path=root/f'assets/horizonvehicles/models/item/go_kart_body_part_{i:02}.json'
            model=json.loads(path.read_text())
            for e in model['elements']:
                for face in e['faces'].values():
                    if face['texture']=='#body':face['tintindex']=0
            result[f'assets/horizonvehicles/models/item/go_kart_body_part_{i:02}.json']=model
        return result,json.loads(json.dumps(desc['parts']['go_kart_body']))

def validate_upload():
    original=json.loads((ROOT/'content/assets/gokart/models/block/go_kart_body.json').read_text())
    edited=json.loads(USER.read_text())
    if original['textures']!=edited['textures'] or len(original['elements'])!=len(edited['elements']):raise ValueError('unexpected user textures or model length')
    changes=[i for i,(a,b) in enumerate(zip(original['elements'],edited['elements'])) if a!=b]
    if changes!=[17,18,20,21]:raise ValueError('unexpected source model modifications')
    for i in changes:
        a,b=original['elements'][i],edited['elements'][i]
        if a['faces']!=b['faces'] or a['rotation']['axis']!=b['rotation']['axis'] or a['rotation']['angle']!=b['rotation']['angle']:raise ValueError('unexpected face or rotation')
        if any(not -16<=v<=32 for key in ('from','to') for v in b[key]):raise ValueError('out of bounds')
    return edited

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected installed pack')
    validate_upload();old,old_desc=models(None);new,new_desc=models(USER)
    expected_desc=json.loads((ROOT/'vehicle-plugin-horizon/paper-plugin/src/main/resources/horizon/off_roader_parts.json').read_text())['parts']['go_kart_body']
    if new_desc!=expected_desc:raise ValueError('edited group pivots do not match plugin')
    for i,(a,b) in enumerate(zip(old_desc,new_desc)):
        if i not in PARTS and a!=b:raise ValueError('unexpected group change')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip() or len(z.namelist())!=len(set(z.namelist())):raise ValueError('invalid pack')
        files={name:z.read(name) for name in z.namelist()}
    for name,old_model in old.items():
        if name not in files or json.loads(files[name])!=old_model:raise ValueError('unexpected old kart group '+name)
        files[name]=json.dumps(new[name],separators=(',',':')).encode()
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
