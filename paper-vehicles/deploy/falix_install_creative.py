#!/usr/bin/env python3
"""Install the November 5 source over the confirmed October 10 build."""
import importlib.util
import sys
from pathlib import Path
spec = importlib.util.spec_from_file_location('oct9', Path(__file__).with_name('falix_install_oct9.py'))
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
prior.CURRENT = 'e947040ede69120d94bdfd2cd0e7639ad7d51b6045b31d80faf5fae04bdebda7'
prior.EXPECTED = prior.f.sha(Path(sys.argv[1]).read_bytes())
prior.main()
