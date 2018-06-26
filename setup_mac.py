#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
# Use http://sveinbjorn.org/platypus
# python3.5 setup_mac.py  py2app usar el otroooo

#from setuptools import setup
from distutils.core import setup
import py2app

APP = ['app.py']
APP_NAME = "vmWareClient"
DATA_FILES = [ 'logging.conf', 'LICENSE', 'README.md']

OPTIONS = {
    'argv_emulation': True,
    'packages': ['idna', 'cryptography', 'cffi','humanize'],
    'iconfile': './icons/vmwareclient.icns',
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundlePackageType': 'APPL',
        #'CFBundleSignature'='????',
        'CFBundleDevelopmentRegion': 'English',
        'CFBundleGetInfoString': "Client VMWare make with python",
        'CFBundleIdentifier': "com.ezquerro.mario",
        'CFBundleVersion': "0.3.20.dev",
        'CFBundleShortVersionString': "0.3.25",
        'NSAppleScriptEnabled':False,
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
