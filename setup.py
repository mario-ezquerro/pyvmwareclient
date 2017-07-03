from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning . python3.5 setup.py build
buildOptions = dict(packages = [], excludes = [])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('app.py',
               base='Console',
               targetName = 'pyvmwareclient',
               compress=False,
               copyDependentFiles=True,
               appendScriptToExe=True,
               appendScriptToLibrary=False,
               icon='./icons/vmwareclient.png')]

setup(name='pyvmwareclient',
      version = '0.3.0a',
      description = 'Client for Vcenter 6.0/6.5 VMware en python',
      options = dict(build_exe = buildOptions),
      maintainer="Mario Ezquerro",
      maintainer_email="mario.ezquerro@gmail.com",
      url = "http://gdglarioja.blogspot.com.es/",
      executables = executables)
