"""
Working with GOES LightCurves
=============================

Overview
--------
"""
################################################################################
# A basic example working with GOES light curves in SunPy. Below, we generate a lightcurve for the previous day and create a simple plot.

from __future__ import print_function, division
from sunpy.lightcurve import GOESLightCurve

goes = GOESLightCurve.from_yesterday()
fig = goes.peek()

################################################################################
# To see what time-range the data is for, we can use the `time_range` method.

print(goes.time_range())

################################################################################
# The underlying data is stored as a
# `pandas DataFrame <http://pandas.pydata.org/pandas-docs/dev/dsintro.html>`_ object.

print(goes.data)

