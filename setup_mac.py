#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
# Use http://sveinbjorn.org/platypus

from setuptools import setup
import py2app

APP = ['app.py']
APP_NAME = "vmWareClient"
DATA_FILES = [('../Frameworks', ['/usr/local/lib/libwx_mac-2.4.0.rsrc',]), 'logging.conf', 'LICENSE', 'README.md']

OPTIONS = {
    'argv_emulation': True,
    'packages': ['idna', 'cryptography', 'cffi'],
    'iconfile': './icons/vmwareclient.icns',
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': "Cliente VMWare fabricado en python",
        'CFBundleIdentifier': "com.ezquerro.mario",
        'CFBundleVersion': "0.3.0a",
        'CFBundleShortVersionString': "0.3.0a",
        'NSHumanReadableCopyright': u"Copyright © 2017, Mario Ezquerro, All Rights Reserved"
    }
}

setup(
    name=APP_NAME,
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
