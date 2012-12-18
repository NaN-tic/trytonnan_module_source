#!/usr/bin/env python
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from setuptools import setup
import re
import os
import ConfigParser


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

config = ConfigParser.ConfigParser()
config.readfp(open('tryton.cfg'))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()
major_version, minor_version, _ = info.get('version', '0.0.1').split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)

requires = []
for dep in info.get('depends', []):
    if not re.match(r'(ir|res|webdav)(\W|$)', dep):
        requires.append('trytond_%s >= %s.%s, < %s.%s' %
                (dep, major_version, minor_version, major_version,
                    minor_version + 1))
requires.append('trytond >= %s.%s, < %s.%s' %
        (major_version, minor_version, major_version, minor_version + 1))

setup(name='trytonnan_module_source',
    version=info.get('version', '0.0.1'),
    description='Tryton module to manage sources of Tryton modules',
    long_description=read('README'),
    author='Tryton',
    url='http://www.nan-tic.com/',
    download_url="https://bitbucket.org/nantic/python-pypi_client/downloads",
    package_dir={'trytond.modules.module_source': '.'},
    packages=[
        'trytond.modules.module_source',
        'trytond.modules.module_source.tests',
        ],
    package_data={
        'trytond.modules.module_source': info.get('xml', []) \
            + ['tryton.cfg', 'locale/*.po', '*.odt', 'icons/*.svg'],
        },
    classifiers=[
#        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Framework :: Tryton',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business',
        ],
    license='GPL-3',
    install_requires=requires,
    extras_require={
        'PypiClient': ['pypi_client'],
        },
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    module_source = trytond.modules.module_source
    """,
    test_suite='tests',
    test_loader='trytond.test_loader:Loader',
    )
