#! /usr/bin/env python
#-*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

packages = [
    'source'
]

scripts = [
    'source/pcap_to_object.py'
]

requires = ['pypacker', 'networkx', 'pillow']

with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    readme = f.read()
with codecs.open(os.path.join(here, 'NEWS.rst'), encoding='utf-8') as f:
    changelog = f.read()

setup(
    name='IP-Link',
    version='0.3',
    author='Cédric Bonhomme',
    author_email='cedric@cedricbonhomme.org',
    packages=packages,
    include_package_data=True,
    scripts=scripts,
    url='https://git.sr.ht/~cedric/IP-Link',
    description='Visualizing the relationships between different IP from network traffic capture.',
    long_description=readme + '\n|\n\n' + changelog,
    platforms = ['Linux'],
    license='Python',
    install_requires=requires,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Security',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
    ]
)
