#!/usr/bin/env python3
"""Install the scaled UTB only over its verified previous deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='e4b7b710d20737de2494abf1b809ed2bf808797f67666505f53df29b10772024'
installer.OLD_PACK='045bfc6c38e80373e6d985e2b534e95fb801855b'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45510103071/HorizonOffRoader-1.21.4.zip'
installer.main()
