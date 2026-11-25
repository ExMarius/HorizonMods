#!/usr/bin/env python3
"""Install UTB refit only over the verified atlas-fixed deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='3d1e0d49517461a4116a6fa5560c65b8d769870a49d19c5e1cc45941f9db0504'
installer.OLD_PACK='23fc16c0e0870a323fa4d5f06d9806b8fc613a90'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45550575491/HorizonOffRoader-1.21.4.zip'
installer.main()
