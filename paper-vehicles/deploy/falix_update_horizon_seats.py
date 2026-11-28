#!/usr/bin/env python3
"""Install the seat/cowl update only over the expected turbo-fixed Horizon build."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.OLD_JAR='ca07036967750541cb1362e359cf0939a265a003beb9fc3fd55e14c865b6c219'
installer.OLD_PACK='ca0413462ebbbc2fde1b8c2f1cfaf43620709661'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45392102009/HorizonOffRoader-1.21.4.zip'
installer.main()
