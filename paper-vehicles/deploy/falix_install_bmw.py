#!/usr/bin/env python3
"""Install BMW candidate only over the verified trailer deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='f50a7d39aec80cbff01c871042161a6cf75e079daee19b6c1a73a9ad336169fc'
installer.OLD_PACK='7b2ff0a429667b6e28bb560d01672aeb724acdaf'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45702206432/HorizonOffRoader-1.21.4.zip'
installer.main()
