#!/usr/bin/env python3
"""Install new Logan body only over the verified previous Logan pair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.OLD_JAR='2943944c0db6bbd6ccf0d38f097f6e0af8721818ec4be21ddbb60221a8b212ec'
installer.OLD_PACK='8bd4d0043b7dde65dc761b87cfc667041acd8ec5'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45409075758/HorizonOffRoader-1.21.4.zip'
installer.main()
