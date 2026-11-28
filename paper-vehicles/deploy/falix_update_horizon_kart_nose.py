#!/usr/bin/env python3
"""Install refined Logan body only over the verified repaired Logan pair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
# The server also has garage data; back it up without altering it.
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='23976bd0c8231d841f2df06b1fc1487d5fb6aa6dc2a98cd702bff6ca27b64e78'
installer.OLD_PACK='17f288e0a4abd966c161150fd10edf2502249272'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45482837773/HorizonOffRoader-1.21.4.zip'
installer.main()
