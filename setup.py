#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup for 劳动法数据库 v2
"""
from setuptools import setup

APP = ['main.py']
DATA_FILES = [
    ('src', ['src/main_window.py', 'src/database.py', 'src/search_utils.py', 'src/user_data.py']),
    ('src/widgets', []),
    ('src/case_workbench', []),
    ('assets', ['assets/laws.db']),
]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt6', 'docx', 'lxml'],
    'includes': ['src', 'src.widgets', 'src.case_workbench'],
    'iconfile': None,
    'plist': {
        'CFBundleName': '劳动法数据库v2',
        'CFBundleShortVersionString': '2.0.0',
        'CFBundleVersion': '2.0.0',
        'CFBundleIdentifier': 'com.laborlawdb.v2',
        'NSHighResolutionCapable': True,
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
