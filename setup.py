from __future__ import unicode_literals

import re
from setuptools import setup, find_packages


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']


setup(
    name='Mopidy-Arcam',
    version=get_version('mopidy_arcam/__init__.py'),
    url='https://github.com/TooDizzy/mopidy-arcam',
    license='Apache License, Version 2.0',
    author='Tue S. Dissing',
    author_email='tue@somersault.dk',
    description='Mopidy extension for controlling an Arcam amplifier',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Mopidy',
        'Pykka',
        'pyserial',
    ],
    entry_points={
        'mopidy.ext': [
            'arcam = mopidy_arcam:Extension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
