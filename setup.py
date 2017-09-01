#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Dependencies are automatically detected, but it might need
# Fine tuning . python3.5 setup.py build
# Usar python setup.py bdist_dmg en Macos
# Or in python setup.py bdist_rpm y en windows bdist_msi

import sys
import os.path
from cx_Freeze import setup, Executable

build_options = dict(build_exe={'include_files': ['logging.conf', 'LICENSE', 'README.md', 'icons'],
                                'packages': ['idna', 'cryptography', 'cffi'],
                                'includes': [],
                                'excludes': []
                                },
                     bdist_mac={'iconfile': "./icons/vmwareclient.icns",
                                })
script = os.path.join("app.py")

if sys.platform == 'win32':
    exe = Executable(script='app.py',
                     targetName="pyvmwareclient.exe",
                     base="Win32GUI",
                     shortcutName='PyVMwareClient',
                     copyright='All Right reserver',
                     shortcutDir='DesktopFolder',
                     icon=os.path.join("icons", "vmwareclient.ico"))

else:
    exe = Executable(script='app.py',
                     base='Console',
                     icon='./icons/vmwareclient.ico',
                     targetName='pyvmwareclient')

setup(name='pyvmwareclient',
      version='0.3.06',
      description='Client for Vcenter 6.0/6.5 VMware en python',
      options=build_options,
      maintainer="Mario Ezquerro",
      maintainer_email="mario.ezquerro@gmail.com",
      url="http://gdglarioja.blogspot.com.es/",
      executables=[exe], requires=['cx_Freeze']
      )
