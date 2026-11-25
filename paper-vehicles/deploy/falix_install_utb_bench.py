#!/usr/bin/env python3
"""Install remodeled UTB only over the verified user-body deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='49d4b355d5f86936e9b0ede36cf8f95ec7b0c24e889fbfe7b0cb3e94d1da090d'
installer.OLD_PACK='1a430feb796a9b756ae5ceaf1842f8e09c749ce2'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45566804564/HorizonOffRoader-1.21.4.zip'
installer.main()
