#!/usr/bin/env python3
"""Install remodeled UTB only over the verified user-body deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='b7c9b136dbd468be9312c66714236ea183ddcee895dd24f17d9c18567571711b'
installer.OLD_PACK='a4e394a13c687d99ac096c0969bc3198865ba5fe'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45592585127/HorizonOffRoader-1.21.4.zip'
installer.main()
