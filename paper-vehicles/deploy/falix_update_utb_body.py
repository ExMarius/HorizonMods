#!/usr/bin/env python3
"""Update UTB only over its verified previous deployed pair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='22f67e799b0921183dbbec801b520f97a87d486ab59389c0bf30cc0908fb4feb'
installer.OLD_PACK='5ef2a14348ab3973904bcb4b314d64c476126cb1'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45496009585/HorizonOffRoader-1.21.4.zip'
installer.main()
