"""
SunPy AIA Image
===============

This example demonstrates how to make a simple AIA plot from SunPy sample data.
"""

import sunpy.data
import sunpy.map


################################################################################
# First, we must download the sample data, if it has not already been
# downloaded.
sunpy.data.download_sample_data(overwrite=False)

################################################################################
# Then import the downloaded sample data.

import sunpy.data.sample

################################################################################
# Now, create a SunPy map from the sample data, and create a quick look plot.

aia_map = sunpy.map.Map(sunpy.data.sample.AIA_171_IMAGE)
aia_map.peek()
