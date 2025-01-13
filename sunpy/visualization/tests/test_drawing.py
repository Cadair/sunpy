import warnings

import numpy as np
import pytest
from matplotlib.figure import Figure

import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from astropy.wcs.wcsapi import HighLevelWCSWrapper
from astropy.wcs.wcsapi.wrappers import SlicedLowLevelWCS

import sunpy.io
from sunpy.data.test import get_test_filepath
from sunpy.map import Map
from sunpy.tests.helpers import figure_test
from sunpy.visualization import drawing


@pytest.fixture
def aia171_test_map():
    return Map(get_test_filepath('aia_171_level1.fits'))


@pytest.fixture
def cropped_aia193_sample_map():
    import sunpy.data.sample
    m = sunpy.map.Map(sunpy.data.sample.AIA_193_JUN2012)
    return m.submap(SkyCoord(Tx=300*u.arcsec, Ty=-325*u.arcsec, frame=m.coordinate_frame),
                    width=500*u.arcsec,
                    height=250*u.arcsec)


@pytest.fixture
def euvi195_sample_map():
    import sunpy.data.sample
    return Map(sunpy.data.sample.STEREO_A_195_JUN2012)


@pytest.fixture
def heliographic_test_map():
    (data, header), = sunpy.io._file_tools.read_file(get_test_filepath('heliographic_phase_map.fits.gz'))
    # Fix unit strings to prevent some astropy fits fixing warnings
    header['CUNIT1'] = 'deg'
    header['CUNIT2'] = 'deg'
    # Set observer location to avoid warnings later
    header['HGLN_OBS'] = 0.0
    return Map((data, header))


@figure_test
def test_draw_equator_aia171(aia171_test_map):
    fig = Figure()
    axes = fig.add_subplot(projection=aia171_test_map)
    aia171_test_map.plot(axes=axes)
    drawing.equator(axes)
    return fig


@figure_test
def test_draw_prime_meridian_aia171(aia171_test_map):
    fig = Figure()
    axes = fig.add_subplot(projection=aia171_test_map)
    aia171_test_map.plot(axes=axes)
    drawing.prime_meridian(axes)
    return fig


@figure_test
def test_heliographic_equator_prime_meridian(heliographic_test_map):
    fig = Figure()
    axes = fig.add_subplot(projection=heliographic_test_map)
    heliographic_test_map.plot(axes=axes)
    drawing.equator(axes, color="blue")
    drawing.prime_meridian(axes, color="red")
    return fig


@figure_test
def test_draw_extent(cropped_aia193_sample_map, euvi195_sample_map):
    fig = Figure()
    ax = fig.add_subplot(projection=euvi195_sample_map)
    euvi195_sample_map.plot(axes=ax)
    drawing.extent(ax, cropped_aia193_sample_map.wcs)
    return fig


def test_prime_meridian_error():
    axes = Figure().add_subplot(projection=WCS())
    with pytest.raises(ValueError, match="does not have an observer"):
        drawing.prime_meridian(axes)


def test_limb_invisible(aia171_test_map):
    aia_obs = aia171_test_map.observer_coordinate
    # Create a new observer on the opposite side of the Sun
    new_obs = SkyCoord(lon=aia_obs.lon + 180*u.deg,
                       lat=-aia_obs.lat,
                       radius=aia_obs.radius / 10,
                       frame=aia_obs.replicate_without_data())

    ax = Figure().add_subplot(projection=aia171_test_map)
    # Original observer
    visible, hidden = drawing.limb(ax, aia_obs)
    assert visible is not None
    assert hidden is None
    # Far side observer
    visible, hidden = drawing.limb(ax, new_obs)
    assert visible is None
    assert hidden is not None


@pytest.fixture
def wcs_3d_ln_lt_l_coupled(aia171_test_map):
    # WCS for a 3D data cube with two celestial axes and one wavelength axis.
    # The latitudinal dimension is coupled to the third pixel dimension through
    # a single off diagonal element in the PCij matrix
    header = {
        'NAXIS1': 100,
        'NAXIS2': 120,
        'NAXIS3': 50,
        'CTYPE1': 'HPLN-TAN',
        'CRPIX1': 5,
        'CDELT1': 5,
        'CUNIT1': 'arcsec',
        'CRVAL1': 0.0,

        'CTYPE2': 'HPLT-TAN',
        'CRPIX2': 5,
        'CDELT2': 5,
        'CUNIT2': 'arcsec',
        'CRVAL2': 0.0,

        'CTYPE3': 'UTC',
        'CRPIX3': 1.0,
        'CDELT3': 1,
        'CUNIT3': 's',
        'CRVAL3': 1.0,

        'PC1_1': 1,
        'PC1_2': 0,
        'PC1_3': 0,
        'PC2_1': 0,
        'PC2_2': 1,
        'PC2_3': -1.0,
        'PC3_1': 1.0,
        'PC3_2': 0.0,
        'PC3_3': 0.0,

        'WCSAXES': 3,

        'DATE-OBS': aia171_test_map.date.isot,
        'HGLN_OBS': aia171_test_map.wcs.wcs.aux.hgln_obs,
        'HGLT_OBS': aia171_test_map.wcs.wcs.aux.hglt_obs,
        'DSUN_OBS': aia171_test_map.wcs.wcs.aux.dsun_obs,
    }
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return HighLevelWCSWrapper(SlicedLowLevelWCS(WCS(header=header), np.s_[0, :, :]))


@figure_test
def test_draw_extent_3d(aia171_test_map, wcs_3d_ln_lt_l_coupled):
    fig = Figure()
    ax = fig.add_subplot(projection=aia171_test_map)
    aia171_test_map.plot(axes=ax)
    drawing.extent(ax, wcs_3d_ln_lt_l_coupled)
    return fig
