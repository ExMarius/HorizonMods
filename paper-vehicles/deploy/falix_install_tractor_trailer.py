#!/usr/bin/env python3
"""Install remodeled UTB only over the verified user-body deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='e973f249151c2862e2848cbd4764ff0fb1172a4d5d1c3a2fc013e0846fd43196'
installer.OLD_PACK='75512413a144dbc611e544617ae599f71f4e2d49'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45584942989/HorizonOffRoader-1.21.4.zip'
installer.main()
