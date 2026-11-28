#!/usr/bin/env python3
"""Install user-edited UTB only over the verified shortened deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='c1df2653fa10ca4b7dd00bdd5305663196217cb63854897064d567be8b779079'
installer.OLD_PACK='6b4c143119fe02cb439559e03a67fc05a0106353'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45555835105/HorizonOffRoader-1.21.4.zip'
installer.main()
