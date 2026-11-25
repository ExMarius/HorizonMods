#!/usr/bin/env python3
"""Install UTB atlas fix over the checked 1:1 UTB pair only."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='3d1e0d49517461a4116a6fa5560c65b8d769870a49d19c5e1cc45941f9db0504'
installer.OLD_PACK='f5a1ee884256dcfa96cfc24c753cf65c22747fc0'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45549595389/HorizonOffRoader-1.21.4.zip'
installer.main()
