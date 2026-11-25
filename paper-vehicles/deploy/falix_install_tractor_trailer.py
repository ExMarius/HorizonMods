#!/usr/bin/env python3
"""Install remodeled UTB only over the verified user-body deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='d94e7f1f0cd5adea03324b6fa47ba8557290e9226d6022f10e0f62171d7e32d3'
installer.OLD_PACK='c459a2bbccc86741c4d1ebfb0e56481dcfeb7763'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45673545820/HorizonOffRoader-1.21.4.zip'
installer.main()
