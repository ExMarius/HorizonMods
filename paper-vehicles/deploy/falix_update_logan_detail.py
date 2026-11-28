#!/usr/bin/env python3
"""Install refined Logan body only over the verified repaired Logan pair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
# The server also has garage data; back it up without altering it.
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='f57d6bece18145136b457e8198fdba1f2d72e8daaf071d7bc9f9ffeaa6100b3e'
installer.OLD_PACK='e2df98516df738c740e1160c81ce8dc0cd870963'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45426294538/HorizonOffRoader-1.21.4.zip'
installer.main()
