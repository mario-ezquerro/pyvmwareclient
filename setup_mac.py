#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
# Use http://sveinbjorn.org/platypus

from setuptools import setup
#from distutils.core import setup
import py2app

APP = ['app.py']
APP_NAME = "vmWareClient"
DATA_FILES = [('../Frameworks', ['/usr/local/lib/libwx_mac-2.4.0.rsrc',]), 'logging.conf', 'LICENSE', 'README.md']

OPTIONS = {
    'argv_emulation': True,
    'packages': ['idna', 'cryptography', 'cffi','humanize'],
    'iconfile': './icons/vmwareclient.icns',
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': "Client VMWare make with python",
        'CFBundleIdentifier': "com.ezquerro.mario",
        'CFBundleVersion': "0.3.10",
        'CFBundleShortVersionString': "0.3.10",
        'NSHumanReadableCopyright': u"Copyright © 2018, Mario Ezquerro, All Rights Reserved"
    }
}

setup(
    name=APP_NAME,
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
