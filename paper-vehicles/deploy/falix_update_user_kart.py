#!/usr/bin/env python3
"""Install refined Logan body only over the verified repaired Logan pair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
# The server also has garage data; back it up without altering it.
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='181b809ed1b46ee4cc6bc68bc2be4a232a9c3514c75f35f3b86a5a93bffc9da6'
installer.OLD_PACK='17f288e0a4abd966c161150fd10edf2502249272'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45488524699/HorizonOffRoader-1.21.4.zip'
installer.main()
