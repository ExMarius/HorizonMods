#!/usr/bin/env python3
"""Install refined Logan body only over the verified repaired Logan pair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
# The server also has garage data; back it up without altering it.
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='01ea6f68ecea941d1b3af04b21a2e5134e6bb6c1fe5e16183b990778df6446f6'
installer.OLD_PACK='9159951f45d8449c9e70f4e9a925f1d537df207b'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45436491163/HorizonOffRoader-1.21.4.zip'
installer.main()
