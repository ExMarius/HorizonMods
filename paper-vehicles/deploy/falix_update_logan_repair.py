#!/usr/bin/env python3
"""Install repaired Logan body only over the verified custom Logan pair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.OLD_JAR='2943944c0db6bbd6ccf0d38f097f6e0af8721818ec4be21ddbb60221a8b212ec'
installer.OLD_PACK='0a0105a9f19d90d5cb37425265692a333012379b'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45411366753/HorizonOffRoader-1.21.4.zip'
installer.main()
