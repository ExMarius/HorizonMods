#!/usr/bin/env python3
"""Install BMW candidate only over the verified trailer deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='0606383405b792aa12cd9f719b44e1f779a588b9239372dd11f495b1f4ac4333'
installer.OLD_PACK='7b2ff0a429667b6e28bb560d01672aeb724acdaf'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45705068841/HorizonOffRoader-1.21.4.zip'
installer.main()
