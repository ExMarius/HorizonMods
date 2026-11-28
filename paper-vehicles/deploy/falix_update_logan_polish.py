#!/usr/bin/env python3
"""Install refined Logan body only over the verified repaired Logan pair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
# The server also has garage data; back it up without altering it.
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='2943944c0db6bbd6ccf0d38f097f6e0af8721818ec4be21ddbb60221a8b212ec'
installer.OLD_PACK='566045f084e745bf4b76706435c573763ec07e74'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45418479212/HorizonOffRoader-1.21.4.zip'
installer.main()
