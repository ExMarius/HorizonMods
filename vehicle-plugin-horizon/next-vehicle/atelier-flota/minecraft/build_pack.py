#!/usr/bin/env python3
"""Build a local resource-pack candidate; never deploys or overwrites a base pack."""
import argparse, hashlib, io, json, subprocess, tempfile, zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent

def build(base: bytes, expected_sha1: str) -> bytes:
    if hashlib.sha1(base).hexdigest()!=expected_sha1.lower():
        raise ValueError('base pack SHA-1 mismatch')
    with zipfile.ZipFile(io.BytesIO(base)) as src:
        names=src.namelist()
        if len(names)!=len(set(names)) or src.testzip(): raise ValueError('invalid or duplicate zip entries')
        files={name:src.read(name) for name in names}
    if json.loads(files['pack.mcmeta'])['pack']['pack_format']!=46: raise ValueError('unsupported pack format')
    with tempfile.TemporaryDirectory() as tmp:
        output=Path(tmp)
        subprocess.run(['node',str(HERE/'export.mjs'),str(output)],check=True,stdout=subprocess.DEVNULL)
        additions={f'assets/vehicle/{p.relative_to(output).as_posix()}':p.read_bytes()
                   for p in output.rglob('*') if p.is_file() and p.name!='conversion-report.json'}
        if not additions or set(files)&set(additions): raise ValueError('asset collision')
        files.update(additions)
    result=io.BytesIO()
    with zipfile.ZipFile(result,'w',zipfile.ZIP_DEFLATED) as dst:
        for name,content in sorted(files.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            dst.writestr(info,content)
    return result.getvalue()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('base',type=Path);p.add_argument('output',type=Path);p.add_argument('--expected-sha1',required=True)
    a=p.parse_args()
    if a.base.resolve()==a.output.resolve() or a.output.exists(): p.error('output must be a new file')
    result=build(a.base.read_bytes(),a.expected_sha1)
    with a.output.open('xb') as file:file.write(result)
    print('Candidate pack SHA-1:',hashlib.sha1(result).hexdigest())
if __name__=='__main__':main()
