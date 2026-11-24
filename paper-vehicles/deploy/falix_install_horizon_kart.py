#!/usr/bin/env python3
"""Install refined Logan body only over the verified repaired Logan pair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
# The server also has garage data; back it up without altering it.
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='1d4bba6773947c26e29f9189b05269feef756b6d1546ca061108dbe1a2b9ea94'
installer.OLD_PACK='db14f4d396fb950567f1ec52ac5d27d417bdb26c'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45479473394/HorizonOffRoader-1.21.4.zip'
installer.main()
