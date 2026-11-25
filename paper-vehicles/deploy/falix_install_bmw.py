#!/usr/bin/env python3
"""Install BMW candidate only over the verified trailer deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='957dcfc265d8cdbfe4008c9ba32c5c7f15474202615f8f7e5fff5e4a8347daa2'
installer.OLD_PACK='bdd3a3ee9108990bbd7a3c5e343776af49792d27'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45689348066/HorizonOffRoader-1.21.4.zip'
installer.main()
