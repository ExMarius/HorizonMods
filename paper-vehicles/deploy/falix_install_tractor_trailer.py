#!/usr/bin/env python3
"""Install remodeled UTB only over the verified user-body deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='35547db755c592da99fd4de16cba302318faa57c055c6e03ac1bf4c6932a4509'
installer.OLD_PACK='51258b834bdd24fe2ab2cce4cb289780974d6bcd'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45596788102/HorizonOffRoader-1.21.4.zip'
installer.main()
