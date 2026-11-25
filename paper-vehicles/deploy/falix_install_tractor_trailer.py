#!/usr/bin/env python3
"""Install remodeled UTB only over the verified user-body deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='f9fb836672c0d963abe028c62dcab189f80025756f02674b7755b2a7b0b6833f'
installer.OLD_PACK='a47458c5229f4f7f167016f72672a38c2d009e4b'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45666237164/HorizonOffRoader-1.21.4.zip'
installer.main()
