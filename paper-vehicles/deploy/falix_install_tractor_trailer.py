#!/usr/bin/env python3
"""Install remodeled UTB only over the verified user-body deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='fee48a7ecbb19023102d4940bc68672f63aa3dbfc27ff861d6b5edd96acbab82'
installer.OLD_PACK='4c2fde06fa7e6932e2f01df1c259581d10da8f56'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45625403233/HorizonOffRoader-1.21.4.zip'
installer.main()
