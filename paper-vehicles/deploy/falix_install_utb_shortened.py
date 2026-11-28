#!/usr/bin/env python3
"""Install shortened UTB only over the verified refit deployment."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='8781b43423b65f323bef145899244eac826e5cadbfd5a68a4de4a9b372e5b095'
installer.OLD_PACK='4bd882618d246d096222ad48ebdaaba5677d8ca9'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45553211325/HorizonOffRoader-1.21.4.zip'
installer.main()
