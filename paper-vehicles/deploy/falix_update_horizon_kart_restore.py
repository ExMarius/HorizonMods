#!/usr/bin/env python3
"""Install refined Logan body only over the verified repaired Logan pair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
# The server also has garage data; back it up without altering it.
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='e51a963bf57a7c079741acd1c67e9a437381898a766e6014f4cfa2dc7e6da301'
installer.OLD_PACK='17f288e0a4abd966c161150fd10edf2502249272'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45486419677/HorizonOffRoader-1.21.4.zip'
installer.main()
