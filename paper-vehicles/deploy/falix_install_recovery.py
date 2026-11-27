#!/usr/bin/env python3
"""Install the recovery candidate only over the specifically audited server."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
installer.NAMES=installer.NAMES | {'garages.yml'}
installer.OLD_JAR='9b63797b49224a565c3807c5e492ad8c416fc4c02eacd7296cf9bb3788b793c2'
installer.OLD_PACK='136f003f9c56ee849881d41fb6697876353b5681'
installer.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-45727535290/HorizonOffRoader-1.21.4.zip'
_original_properties=installer.properties
def offline_properties(api):
    if api.status()!='offline':
        raise ValueError('Server started during installation; do not modify live files')
    return _original_properties(api)
installer.properties=offline_properties

# Guard each mutating operation, not just the initial snapshot. Backup uploads
# at the server root remain permitted, while live plugin/config writes do not.
class OfflineFalix(installer.f.Falix):
    def upload(self, directory, name, content):
        if directory != '/' and self.status() != 'offline':
            raise ValueError('Server started; refusing plugin file write')
        return super().upload(directory,name,content)
    def api(self, path, data=None, method=None):
        if path == '/properties' and method == 'PUT' and self.status() != 'offline':
            raise ValueError('Server started; refusing resource pack configuration change')
        return super().api(path,data,method)
installer.f.Falix=OfflineFalix
if __name__=='__main__':
    if installer.f.Falix(installer.f.login()).status()!='offline':raise SystemExit('Server must remain offline; no installation performed')
    installer.main()
