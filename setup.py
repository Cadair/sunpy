#!/usr/bin/env python
import itertools

from setuptools import setup
from setuptools.config import read_configuration

# Create an 'all' extra which is all the others combined
extras = read_configuration("setup.cfg")['options']['extras_require']
extras['all'] = list(itertools.chain.from_iterable(extras.values()))

setup(use_scm_version=True, extras_require=extras)
