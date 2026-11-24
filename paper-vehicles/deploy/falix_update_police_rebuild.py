#!/usr/bin/env python3
"""Install rebuilt Dacia only over the verified police-livery pair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.OLD_JAR='ec7995898e3ee4372a78fe33487ef9d183701be9e8f676210a97e6481148ba00'
installer.OLD_PACK='162d4dd9ff52d0980d1eb4adbe9057f024b779c7'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45402788222/HorizonOffRoader-1.21.4.zip'
installer.main()
