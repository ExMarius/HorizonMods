#!/usr/bin/env python3
"""Install the oriented GD-3.2 rig only over the verified harrow release."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='b1f43d21edce37a7112f80d84fce1023202fe4c7ec64e81600de02038fe97f2a'
installer.OLD_PACK='136f003f9c56ee849881d41fb6697876353b5681'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45723536290/HorizonOffRoader-1.21.4.zip'
installer.main()
