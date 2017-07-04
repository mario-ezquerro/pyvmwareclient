#!/usr/bin/python5.5
# -*- coding: utf-8 -*-

from setuptools import setup

APP = ['app.py']
APP_NAME = "vmWareClient"
DATA_FILES = []

OPTIONS = {
    'argv_emulation': True,
    'iconfile': './icons/vmwareclient.ico',
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': "Cliente VMWare",
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