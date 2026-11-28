#!/usr/bin/env python3
"""Install user's Logan body in all three lightbar phases; preserve the pack."""
import argparse, copy, hashlib, io, json, zipfile
from pathlib import Path
import custom_logan_body as c
BASE_SHA1='5fdb821f0e294a9e2a9f22696d011555b1967c5c'
INPUT=Path(__file__).parent/'assets/user-edits/body_flash_1.json'
BLUE=((1.35,17.2,5.65),(7.4,18.15,8.75))
RED=((8.6,17.2,5.65),(14.65,18.15,8.75))

def variants(source,files):
    src=copy.deepcopy(source); tex=src.get('textures',{}); elements=src.get('elements',[])
    if len(elements)!=241:raise ValueError('unexpected user model element count')
    for e in elements:
        for k in ('from','to'):
            if len(e[k])!=3 or any(not isinstance(x,(int,float)) or not -16<=x<=32 for x in e[k]):raise ValueError('invalid model bounds')
        if any(a>b for a,b in zip(e['from'],e['to'])):raise ValueError('inverted model element')
        rot=e.get('rotation')
        # Blockbench may emit zero-degree rotations with invalid pivots.
        # Removing a zero rotation does not alter geometry and avoids a rejected model.
        if rot and rot.get('angle') == 0:
            e.pop('rotation'); rot=None
        if rot and (rot.get('axis') not in ('x','y','z') or rot.get('angle') not in (-45,-22.5,0,22.5,45) or len(rot.get('origin',[]))!=3 or any(not -16<=x<=32 for x in rot['origin'])):raise ValueError('invalid rotation')
        for f in e.get('faces',{}).values():
            name=f.get('texture','')
            if not name.startswith('#') or name[1:] not in tex:raise ValueError('unresolved face texture '+str(name))
    for value in tex.values():
        if not value.startswith('daciapolice:item/') or 'assets/daciapolice/textures/item/'+value.split('/')[-1]+'.png' not in files:raise ValueError('texture missing '+value)
    tex.update({'red_dim':'daciapolice:item/siren_red_dim','blue':'daciapolice:item/horizon_siren_blue'})
    for value in (tex['red_dim'],tex['blue']):
        if 'assets/daciapolice/textures/item/'+value.split('/')[-1]+'.png' not in files:raise ValueError('missing siren texture')
    def find(bounds,expected):
        parts=[e for e in elements if (tuple(e['from']),tuple(e['to']))==bounds]
        if len(parts)!=1 or {f['texture'] for f in parts[0]['faces'].values()}!={expected}:raise ValueError('unexpected lightbar geometry')
        return elements.index(parts[0])
    blue=find(BLUE,'#blue_dim'); red=find(RED,'#red')
    result=[]
    for b,r in (('#blue_dim','#red_dim'),('#blue','#red_dim'),('#blue_dim','#red')):
        variant=copy.deepcopy(src)
        for i,color in ((blue,b),(red,r)):
            for face in variant['elements'][i]['faces'].values():face['texture']=color
        result.append(variant)
    return result

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected installed pack')
    files=c.readzip(data)
    for path,model in zip(c.PATHS,variants(json.loads(INPUT.read_text()),files)):files[path]=c.encode(model)
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for name,value in sorted(files.items()):
            item=zipfile.ZipInfo(name,(1980,1,1,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;z.writestr(item,value)
    return out.getvalue()
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('base',type=Path);parser.add_argument('output',type=Path);a=parser.parse_args()
    if a.base.resolve()==a.output.resolve():parser.error('output must be different')
    result=build(a.base.read_bytes());a.output.write_bytes(result);print('SHA-1',hashlib.sha1(result).hexdigest())
if __name__=='__main__':main()
