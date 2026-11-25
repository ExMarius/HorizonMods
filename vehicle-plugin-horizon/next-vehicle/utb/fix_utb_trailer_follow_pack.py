#!/usr/bin/env python3
"""Apply only the modern trailer's two models to the verified installed pack."""
import argparse,hashlib
from pathlib import Path
import fix_utb_modern_details_pack as patch
BASE_SHA1='a1965c7d7628f1c91f9fb40d469abc1fbdb72414'
def build(data,expected=BASE_SHA1):return patch.build(data,expected)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.base.resolve()==a.output.resolve():p.error('output must differ')
    result=build(a.base.read_bytes());a.output.write_bytes(result);print('SHA-1',hashlib.sha1(result).hexdigest())
if __name__=='__main__':main()
