#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
# Dependencies are automatically detected, but it might need
# Fine tuning . python3.5 setup.py build
# Usar python  en Macos bdist_dmg
# Or in python setup.py bdist_rpm y en windows bdist_msi

import sys
import os.path
from cx_Freeze import setup, Executable

build_options = dict(build_exe={'include_files': ['logging.conf', 'LICENSE', 'README.md', 'icons'],
                                'packages': ['idna', 'cryptography', 'cffi', 'humanize', 'OpenSSL', 'webbrowser'],
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
      version='0.3.15.dev',
      description='Client for Vcenter 6.0/6.5 VMware en python',
      author='Mario Ezquerro',
      author_email='mario.ezquerro@gmail.com',
      options=build_options,
      maintainer="Mario Ezquerro",
      maintainer_email="mario.ezquerro@gmail.com",
      url="https://github.com/wbugbofh/pyvmwareclient",
      license='GNU',
      classifiers=[
        'Development Status :: 3 - BETA',
        'License :: OSI Approved :: GNU',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Environment :: No Input/Output (Daemon)',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
      ],
      #long_description=read('README.md'),
      platforms=['Windows', 'Linux', 'Solaris', 'Mac OS-X', 'Unix'],
      zip_safe=True,
      executables=[exe], requires=['cx_Freeze']
      )
