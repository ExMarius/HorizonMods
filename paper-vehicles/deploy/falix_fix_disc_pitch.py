#!/usr/bin/env python3
"""Install the oriented GD-3.2 rig only over the verified harrow release."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='f9e33f57ed92d47783c796f17647861d0fca1284e1752d802ca33083426cc4d2'
installer.OLD_PACK='136f003f9c56ee849881d41fb6697876353b5681'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45726354974/HorizonOffRoader-1.21.4.zip'
installer.main()
