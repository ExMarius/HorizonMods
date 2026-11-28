#!/usr/bin/env python3
"""Install remodeled UTB only over the verified user-body deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='84291afdc84cda6522c1a4b59993619b0f7b5462000a56ad9b224f186dde8335'
installer.OLD_PACK='deaad61c12776b6e478e92744e5f0606e5ef658f'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45564597650/HorizonOffRoader-1.21.4.zip'
installer.main()
