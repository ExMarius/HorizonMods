#!/usr/bin/env python3
"""Install refined Logan body only over the verified repaired Logan pair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
# The server also has garage data; back it up without altering it.
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='524fda2ba813a140622e2e2d23113ba0aec9163736177921c78295c4626f3771'
installer.OLD_PACK='13521f225f298923a18b6cdc8dc6fd0f9330259b'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45433382850/HorizonOffRoader-1.21.4.zip'
installer.main()
