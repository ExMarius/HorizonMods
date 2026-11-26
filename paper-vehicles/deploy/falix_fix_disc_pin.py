#!/usr/bin/env python3
"""Install the oriented GD-3.2 rig only over the verified harrow release."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='c0c5cb1d2cde576a52a9077f20fe3b84d66bbbd718e280be9c599711abaec27d'
installer.OLD_PACK='136f003f9c56ee849881d41fb6697876353b5681'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45724921999/HorizonOffRoader-1.21.4.zip'
installer.main()
