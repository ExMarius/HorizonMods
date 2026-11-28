#!/usr/bin/env python3
"""Install UTB only over the verified user-edited Go-Kart deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='102d7e7e631194cf44fe08ed0bef3fb30007adba1a1b9e66b4a8ec6272db7621'
installer.OLD_PACK='ec159abcd4250da7c991015e35a65b3440ed3e41'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45491237890/HorizonOffRoader-1.21.4.zip'
installer.main()
