#!/usr/bin/env python3
"""Replace only our previously uploaded sync build, with verified backups."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('prior_deploy', Path(__file__).with_name('falix_deploy_sync.py'))
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
# Refuse to overwrite a different build that the user may have installed.
prior.BASELINE='e32c0af133f33985e810ffdac72ac6776cb204d386fc215d0b7fb4507eaa5371'
prior.main()
