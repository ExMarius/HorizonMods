#!/usr/bin/env python3
"""Install Logan redesign only over the verified prior Dacia release."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.OLD_JAR='2943944c0db6bbd6ccf0d38f097f6e0af8721818ec4be21ddbb60221a8b212ec'
installer.OLD_PACK='c4b0ccc2ec583a50e2a5f99d3e9a9d6601d66f4f'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45406628530/HorizonOffRoader-1.21.4.zip'
installer.main()
