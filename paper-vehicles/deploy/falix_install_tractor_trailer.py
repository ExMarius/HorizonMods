#!/usr/bin/env python3
"""Install remodeled UTB only over the verified user-body deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='0e455077664781da197517c4bef34a5bf8697842f47bd99bee64283daf6730fd'
installer.OLD_PACK='c459a2bbccc86741c4d1ebfb0e56481dcfeb7763'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45679671889/HorizonOffRoader-1.21.4.zip'
installer.main()
