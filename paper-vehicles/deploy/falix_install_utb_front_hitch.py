#!/usr/bin/env python3
"""Install remodeled UTB only over the verified user-body deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='216d88a9ccb608d4483be5183765fade6bdd686558a4a6b82a26aa60d6884be6'
installer.OLD_PACK='8fefe950909edabc554a05ad09f46638fd33a7dc'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45562368474/HorizonOffRoader-1.21.4.zip'
installer.main()
