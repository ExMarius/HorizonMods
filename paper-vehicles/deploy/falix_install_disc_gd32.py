#!/usr/bin/env python3
"""Install GD-3.2 only over the exact last verified production release."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='964091d5a1aaf1a7ed6ca60eb8aeb8e4fc706346a621b508e7186e3b471860f4'
installer.OLD_PACK='49a5735816925c01248e28ab185d35c45404d018'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45708228938/HorizonOffRoader-1.21.4.zip'
installer.main()
