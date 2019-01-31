#!/usr/bin/env python
import itertools

from setuptools import setup
from setuptools.config import read_configuration

# Create an 'all' extra which is all the others combined
extras = read_configuration("setup.cfg")['options']['extras_require']
extras['all'] = list(itertools.chain.from_iterable(extras.values()))

"""
If we can import astropy_helpers, then we are in a build phase, and we should
be able to use astropy helpers to build our C extension.
"""


def register_build_command(srcdir='.'):
    from astropy_helpers.setup_helpers import _module_state, add_command_hooks
    from astropy_helpers.commands.build_ext import AstropyHelpersBuildExt
    from astropy_helpers.distutils_helpers import add_command_option
    _module_state['registered_commands'] = registered_commands = {
        'build_ext': AstropyHelpersBuildExt}

    for option in [
            ('use-system-libraries',
             "Use system libraries whenever possible", True)]:
        add_command_option('build', *option)
        add_command_option('install', *option)

    add_command_hooks(registered_commands, srcdir=srcdir)

    return registered_commands


pkg_info = {}
try:
    from astropy_helpers.setup_helpers import get_package_info
    pkg_info.update(register_build_command())
    pkg_info.update(get_package_info())
except ModuleNotFoundError:
    pass

setup(use_scm_version=True, extras_require=extras, **pkg_info)
