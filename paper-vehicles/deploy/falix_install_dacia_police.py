#!/usr/bin/env python3
"""Install only over the verified Horizon seats/cowl pair, with backups."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.OLD_JAR='c8474ff6aa4824abb17b5ceb5ebd231c7e659e48661d2f66078fa3b41e6956ca'
installer.OLD_PACK='62ae2a64b6966143e06882b9beca519668241ec7'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45396585154/HorizonOffRoader-1.21.4.zip'
installer.main()
