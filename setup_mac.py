#!/usr/bin/python5.5
# -*- coding: utf-8 -*-

# para ejecutar python3.5 setup_mac.py py2app

from setuptools import setup
OPTIONS = {
 'iconfile':'./icons/vmwareclient.ico',
}
setup(
 app=["app.py"],
 options = {'py2app': OPTIONS},
 setup_requires=["py2app"],
)