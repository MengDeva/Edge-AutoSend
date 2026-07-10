import os
from setuptools import setup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def folder_files(folder_name):
    folder_path = os.path.join(BASE_DIR, folder_name)
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path)]


APP = ['Run.py']  # your main script
DATA_FILES = [
    'checkinMe.py',
    'timelines.py',
    'aow.py',
    ('CheckinMe Screenshots', folder_files('CheckinMe Screenshots')),
    ('Timelines Screenshots', folder_files('Timelines Screenshots')),
    ('Aow Screenshots', folder_files('Aow Screenshots')),
]
OPTIONS = {
    'argv_emulation': False,
    'packages': ['tkinter', 'requests', 'urllib3', 'certifi', 'charset_normalizer', 'idna'],
    'includes': ['tkinter', 'requests', 'urllib3', 'certifi', 'charset_normalizer', 'idna'],
    'iconfile': './icon.icns',  # optional, remove if you don't have one
    'plist': {
        'CFBundleName': 'Deva Tools',
        'CFBundleShortVersionString': '1.0.0',
    },
    # add any packages your script imports, e.g. 'openpyxl'
    'packages': [],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
