#!/usr/bin/env python3
"""Install remodeled UTB only over the verified user-body deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='b868db9dbdd9699839101813bb51635e028dfdc0ea27ca6798e51042090e2801'
installer.OLD_PACK='d29fad800a3c2cb6895e9aa8f8449bb6a96fc9ed'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45573217651/HorizonOffRoader-1.21.4.zip'
installer.main()
