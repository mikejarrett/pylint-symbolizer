# -*- coding: utf8 -*-
from codecs import open
from os import path
from setuptools import setup, find_packages

from pylint_symbolizer import __version__

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as file_:
    long_description = file_.read()


setup(
    name='pylint_symbolizer',
    version=__version__,
    author='Mike Jarrett',
    author_emai='mike<dot>d<dot>jarrett<at>gmail<dot>com',
    url='https://github.com/mikejarrett/pylint-symbolizer',
    description='Renames disabled Pylint IDs to Pylint symbolic names',
    long_description=long_description,
    download_url='https://github.com/mikejarrett/pylint-symbolizer',
    install_requires=['pylint>=1.5.0'],
    packages=['pylint_symbolizer'],
    scripts=[],
    tests_require=['nose', 'coverage', 'unittest2', 'mock'],
    entry_points={
        'console_scripts': [
            'symbolizer = symbolizer.main:main',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.4',
    ],
)
