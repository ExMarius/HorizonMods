#!/usr/bin/env python3
"""Install refined Logan body only over the verified repaired Logan pair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
# The server also has garage data; back it up without altering it.
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='6c39a187aa6b7f0343500998f7f1129e4b6e667f750d27e118ad8a154d4f53fe'
installer.OLD_PACK='88c00d83de155aa9dba76cea5a0aaac6c174b4db'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45446961259/HorizonOffRoader-1.21.4.zip'
installer.main()
