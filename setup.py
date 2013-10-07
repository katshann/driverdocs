#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='driverdocs',
      version='0.0.1',
      author='Rob Dobson',
      packages=find_packages(),
      package_data={'': ['*.html']},
      include_package_data=True,
      install_requires=[],
      )
