#!/usr/bin/env python
import os
from setuptools import setup, find_packages


BASE = os.path.dirname(__file__)
README_PATH = os.path.join(BASE, 'README.rst')
CHANGES_PATH = os.path.join(BASE, 'CHANGES.rst')
long_description = '\n\n'.join((
    open(README_PATH).read(),
    open(CHANGES_PATH).read(),
))


setup(
    name='bericht',
    version='0.0.11',
    url='https://github.com/systori/bericht',
    license='BSD',
    description='Improved tabular report generation with ReportLab.',
    long_description=long_description,
    author='Lex Berezhny',
    author_email='lex@damoti.com',
    keywords='pdf,table,report,reportlab,html',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
    ],
    install_requires=['reportlab', 'pdfrw', 'tinycss2'],
    packages=find_packages(exclude=('bericht.tests',)),
    include_package_data=True
)
