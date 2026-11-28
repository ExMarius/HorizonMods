#!/usr/bin/env python3
"""Install refined Logan body only over the verified repaired Logan pair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
# The server also has garage data; back it up without altering it.
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='a2c0d24b67862b72c871d980fb0e20337b4bf3ec23cd2c00dfae7f76020b4852'
installer.OLD_PACK='2069088cc44c8c55157ed6baceba8eda16bcd9a0'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45442315730/HorizonOffRoader-1.21.4.zip'
installer.main()
