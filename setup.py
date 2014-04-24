# -*- coding: utf8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import pylint_symbolizer


with open('README.rst', 'rb') as readme:
    long_description = readme.read()


config = {
    'name': 'pylint_symbolizer',
    'version': pylint_symbolizer.__version__,
    'author': 'Mike Jarrett',
    'author_email': 'mdj00m@gmail.com',
    'url': 'https://github.com/mikejarrett/pylint-symbolizer',
    'description': 'Renames disabled Pylint IDs to Pylint symbolic names',
    'long_description': long_description,
    'download_url': 'https://github.com/mikejarrett/pylint-symbolizer',
    'install_requires': ['pylint>=1.2.0'],
    'packages': ['pylint_symbolizer'],
    'scripts': [],
    'entry_points':  {
        'console_scripts': [
            'symbolizer = symbolizer.main:main',
        ]},
}

setup(**config)
