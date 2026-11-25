#!/usr/bin/env python3
"""Install remodeled UTB only over the verified user-body deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='f9fb836672c0d963abe028c62dcab189f80025756f02674b7755b2a7b0b6833f'
installer.OLD_PACK='a1965c7d7628f1c91f9fb40d469abc1fbdb72414'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45669921266/HorizonOffRoader-1.21.4.zip'
installer.main()
