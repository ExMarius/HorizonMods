#!/usr/bin/env python3
"""Install police livery only over the verified previous Dacia pair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.OLD_JAR='69074d160c8f7b198a285a7ef2b820c7dd64808a83e36d84a1c1f07cb1473470'
installer.OLD_PACK='4357e64281b5889d4c24d3e85faf35010e0d709e'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45399405882/HorizonOffRoader-1.21.4.zip'
installer.main()
