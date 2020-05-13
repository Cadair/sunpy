import sunpy.coordinates

from astropy.wcs import WCS
from astropy.coordinates import SkyCoord, EarthLocation


class SolarWCS(WCS):
    """
    A small wrapper around `~astropy.wcs.WCS` which provides better support for observer location.
    """
    @property
    def observer_coordinate(self):
        """
        An `astropy.coordinates.SkyCoord` representing the position of the observer.
        """
        return SkyCoord(lat=self.wcs.aux.hglt_obs,
                        lon=self.wcs.aux.hgln_obs,
                        distance=self.wcs.aux.dsun_obs,
                        frame=sunpy.coordinates.HeliographicStonyhurst)

    @observer_coordinate.setter
    def _set_observer(self, observer):
        if isinstance(observer, EarthLocation):
            observer = observer.to_itrs(self.wcs.dateobs)

        if isinstance(observer, SkyCoord):
            observer = observer.frame

        observer = observer.transform_to(sunpy.coordinates.HeliographicStonyhurst(obstime=self.wcs.dateobs))

        self.wcs.aux.hglt_obs = observer.lat
        self.wcs.aux.hgln_obs = observer.lon
        self.wcs.aux.dsun_obs = observer.distance
