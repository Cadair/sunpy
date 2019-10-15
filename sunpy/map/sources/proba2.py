"""PROBA2 Map subclass definitions"""
from sunpy.map import GenericMap

__all__ = ['SWAPMap']


class SWAPMap(GenericMap):
    """PROBA2 SWAP Image Map.

    The Sun Watcher using Active Pixel System detector and Image Processing (SWAP)
    SWAP provides images of the solar corona at about 17.4 nm, a bandpass
    that corresponds to a temperature of roughly 1 million degrees,
    with a cadence of 1 image per 1-2 minutes, and field of view (FOV) of 54 arcmin.
    It is derived from the SOHO EIT telescope concept design.

    PROBA2 was launched on 2 November 2009.

    References
    ----------
    * `Proba2 SWAP Science Center <http://proba2.sidc.be/about/SWAP/>`_
    * `Fits headers reference <http://proba2.oma.be/data/SWAP/level0>`_
    """

    def __init__(self, data, header, **kwargs):
        super().__init__(data, header, **kwargs)

        # It needs to be verified that these must actually be set and
        # are not already in the header.
        self.meta['detector'] = "SWAP"
#        self.meta['instrme'] = "SWAP"
        self.meta['obsrvtry'] = "PROBA2"

        self._nickname = self.detector

    def _default_plot_settings(self):
        import matplotlib.pyplot as plt

        plot_settings = super()._default_plot_settings()
        plot_settings['cmap'] = plt.get_cmap(name='sdoaia171')

        return plot_settings

    @classmethod
    def is_datasource_for(cls, data, header, **kwargs):
        """Determines if header corresponds to an SWAP image"""
        return header.get('instrume') == 'SWAP'
