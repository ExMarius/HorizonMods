#!/usr/bin/env python3
"""Install remodeled UTB only over the verified user-body deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='55de05a63bdd0b340432af0cbc25b30b64db23733a40ac4a52cc64b52596d16b'
installer.OLD_PACK='5d8260da16cbcf3e3a9a2941baa023c950214199'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45643761103/HorizonOffRoader-1.21.4.zip'
installer.main()
