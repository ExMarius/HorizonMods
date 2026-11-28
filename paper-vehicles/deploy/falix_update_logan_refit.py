#!/usr/bin/env python3
"""Install refined Logan body only over the verified repaired Logan pair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
# The server also has garage data; back it up without altering it.
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='6ddf2f509eebfca58a0686f0378da74b324e78b3b79d8953e3e5978a06ae37a6'
installer.OLD_PACK='ba7b73145f5312aac04d4158d2340576da4afb9e'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45420871057/HorizonOffRoader-1.21.4.zip'
installer.main()
