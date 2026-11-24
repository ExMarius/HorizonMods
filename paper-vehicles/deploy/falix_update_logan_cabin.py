#!/usr/bin/env python3
"""Install refined Logan body only over the verified repaired Logan pair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
# The server also has garage data; back it up without altering it.
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='d412e636ee5b51f875fc7cec397dd8f661398acf36aa12ca41040291edd3cd0c'
installer.OLD_PACK='0dc8d1a76098d8ab752a34366ab3c91fe1dcb010'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45423974565/HorizonOffRoader-1.21.4.zip'
installer.main()
