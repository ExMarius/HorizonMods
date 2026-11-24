#!/usr/bin/env python3
"""Install the built 10 October source only over the confirmed 9 October release."""
import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location('oct9', Path(__file__).with_name('falix_install_oct9.py'))
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
prior.CURRENT = '39d884e35e30444db14803900a2b843b7d1510340830bb8b506e09eaa1bfc5c5'
# The artifact comes directly from the pinned source build in this workflow.
prior.EXPECTED = prior.f.sha(Path(sys.argv[1]).read_bytes())
prior.main()
