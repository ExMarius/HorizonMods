#!/usr/bin/env python3
"""Install remodeled UTB only over the verified user-body deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='59c3337d296aa6e3f2d501005df48cd58e91f48679ea808d411a75fa981a2e25'
installer.OLD_PACK='ed9183ba6cc662297ed2cb971b999e69c9ace4da'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45661047973/HorizonOffRoader-1.21.4.zip'
installer.main()
