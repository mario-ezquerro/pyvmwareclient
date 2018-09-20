#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
# Dependencies are automatically detected, but it might need
# Fine tuning  python3.5 setup.py build
# Usar python  en Macos bdist_dmg
# Or in python sudo python3.5 setup.py bdist_rpm y en windows bdist_msi
# Error subsane with :
# pip install --upgrade setuptools
# pip install --upgrade distribute

import sys
import os.path
import glob
from codecs import open
from cx_Freeze import setup, Executable

build_options = dict(build_exe={'include_files': ['logging.conf', 'LICENSE', 'README.md', 'icons'],
                                'packages': ['idna', 
                                             'cryptography',
                                             'cffi',
                                             'OpenSSL',
                                             'webbrowser',
                                             'setuptools',
                                             'humanize',
                                             'matplotlib',
                                             'numpy',
                                             'tkinter'],
                                'includes': [],
                                'excludes': []
                                },
                     bdist_mac={'iconfile': "./icons/vmwareclient.icns",
                                })
script = os.path.join("app.py")

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


if sys.platform == 'win32':
    os.environ['TCL_LIBRARY'] = r'E:\python\tcl\tcl8.6'
    os.environ['TK_LIBRARY'] = r'E:\python\tcl\tk8.6'
    exe = Executable(script='app.py',
                     targetName="pyvmwareclient.exe",
                     base="Win32GUI",
                     shortcutName='PyVMwareClient',
                     copyright='All Right reserver',
                     shortcutDir='DesktopFolder',
                     icon=os.path.join("icons", "vmwareclient.ico"))

else:
    os.environ['TCL_LIBRARY']=r'/System/Library/Frameworks/Tcl.framework/Versions/8.5/Tcl' 
    os.environ['TK_LIBRARY']=r'/System/Library/Frameworks/Tk.framework/Versions/8.5/Tk' 
    exe = Executable(script='app.py',
                     base='Console',
                     icon='./icons/vmwareclient.ico',
                     targetName='pyvmwareclient')

# sudo mkdir -p /Library/Frameworks/Tcl.framework/Versions/8.5
# sudo mkdir -p /Library/Frameworks/Tk.framework/Versions/8.5
# sudo cp  -r /System/Library/Frameworks/Tcl.framework/Versions/8.5/Tcl /Library/Frameworks/Tcl.framework/Versions/8.5
# sudo cp -r /System/Library/Frameworks/Tk.framework/Versions/8.5/Tk /Library/Frameworks/Tk.framework/Versions/8.5

setup(name='pyvmwareclient',
      version='0.4.1',
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
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Environment :: No Input/Output (Daemon)',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
      ],
      long_description=long_description,
      #platforms=['Windows', 'Linux', 'Solaris', 'Mac OS-X', 'Unix'],
      #zip_safe=True,
      keywords='pyvmwareclient Client esxi and vmware',
      #packages=['menu_action', 'wxgladegen', 'tools'],
      #package_dir = {'menu_action':'action_vm'},
      data_files=[
      ('app.py', glob.glob('app.py')),
      ('icons', glob.glob('icons/*')),
      ('images', glob.glob('images/*.png')),
      ('README.md', glob.glob('README.md')),
      ('logging.conf', glob.glob('logging.conf'))
      ],
      executables=[exe],
      requires=['cx_Freeze']
      )
