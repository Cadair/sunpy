"""RHESSI Map subclass definitions"""

__author__ = "Steven Christe"
__email__ = "steven.d.christe@nasa.gov"

import astropy.units as u

from sunpy import log
from sunpy.map import GenericMap

__all__ = ['RHESSIMap']


class RHESSIMap(GenericMap):
    """RHESSI Image Map.

    The RHESSI mission consists of a single spin-stabilized
    spacecraft in a low-altitude orbit inclined 38 degrees to
    the Earth's equator. The only instrument on board is an
    Germaniun imaging spectrometer with the ability to obtain high
    fidelity solar images in X rays (down to 3 keV) to gamma rays (1 MeV).

    RHESSI provides an angular resolution of 2 arcseconds at
    X-ray energies below ~40 keV, 7 arcseconds to 400 keV,
    and 36 arcseconds for gamma-ray lines and continuum above 1 MeV.

    RHESSI was launched on 5 February 2002.

    References
    ----------
    * RHESSI Homepage `<https://hesperia.gsfc.nasa.gov/rhessi3/index.html>`_
    * Mission Paper `<https://doi.org/10.1023/A:1022428818870>`_

    .. warning::

        This software is in beta and cannot read fits files containing more than one image.
    """

    def __init__(self, data, header, **kwargs):
        # Fix some broken/misapplied keywords
        if header['ctype1'] == 'arcsec':
            header['cunit1'] = 'arcsec'
            header['ctype1'] = 'HPLN-TAN'

        if header['ctype2'] == 'arcsec':
            header['cunit2'] = 'arcsec'
            header['ctype2'] = 'HPLT-TAN'

        super().__init__(data, header, **kwargs)

        self._nickname = self.detector
        self.plot_settings['cmap'] = 'rhessi'

        if ('TIMESYS' in self.meta and
                self.meta['keycomments']['TIMESYS'] == 'Reference Time'):
            log.debug('Moving "TIMESYS" FITS keyword to "DATEREF"')
            self.meta['DATEREF'] = self.meta.pop('TIMESYS')

    @property
    def waveunit(self):
        unit = self.meta.get("waveunit", 'keV')
        return u.Unit(unit)

    @property
    def wavelength(self):
        return u.Quantity([self.meta['energy_l'], self.meta['energy_h']],
                          unit=self.waveunit)

    @property
    def detector(self):
        return self.meta['telescop']

    @classmethod
    def is_datasource_for(cls, data, header, **kwargs):
        """Determines if header corresponds to an RHESSI image"""
        return header.get('instrume') == 'RHESSI'
