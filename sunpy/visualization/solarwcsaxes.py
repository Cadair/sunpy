"""
A solar specific subclass of `astropy.visualization.wcsaxes.WCSAxes`.
"""
from functools import wraps

from matplotlib import patches
from matplotlib.axes import Axes

import astropy.units as u
from astropy.nddata import NDData
from astropy.visualization.wcsaxes import WCSAxes


# https://github.com/sunpy/sunpy/issues/4022
# TODO:
#   - pass data to imshow /contour and/or have the Axes have a reference to the NDData?
class SolarWCSAxes(WCSAxes):
    """
    """

    @wraps(WCSAxes.reset_wcs)
    def reset_wcs(self, *args, **kwargs):
        super().reset_wcs(*args, **kwargs)

        # TODO: override the default labels here by setting coords[i].default_label
        # Need to workout how to do that based on the info in the CoordinateHelper if possible.

    @wraps(Axes.imshow)
    def imshow(self, X, *args, **kwargs):
        if isinstance(X, NDData):
            X = X.data
        return super().imshow(X, *args, **kwargs)


    # TODO: Name to restrict to celestial?
    def draw_rectangle(self, bottom_left, *, width: u.deg=None, height: u.deg=None, top_right=None, **kwargs):
        """
        Draw a rectangle in celestial coordinates.
        """
        # TODO: Check that we have two spatial dimensions, and we are plotting them.
        bottom_left, top_right = get_rectangle_coordinates(bottom_left,
                                                           top_right=top_right,
                                                           width=width,
                                                           height=height)

        # TODO: The axes object knows which coordinate is lat and which is lon.
        width = Longitude(top_right.spherical.lon - bottom_left.spherical.lon)
        height = Latitude(top_right.spherical.lat - bottom_left.spherical.lat)

        # TODO: Actually look this up from coord_meta or whereever
        axes_unit = u.deg

        # TODO: Use our own representation of the coordinate
        coord = bottom_left.transform_to(self.coordinate_frame)
        bottom_left = u.Quantity((coord.spherical.lon, coord.spherical.lat), unit=axes_unit).value

        width = width.to(axes_unit).value
        height = height.to(axes_unit).value
        kwergs = {'transform': self.get_world_transform(),
                  'color': 'white',
                  'fill': False}
        kwergs.update(kwargs)
        # TODO: Don't use pyplot here
        rect = plt.Rectangle(bottom_left, width, height, **kwergs)
        self.add_artist(rect)
        return [rect]

    def draw_limb(self, **kwargs):
        """
        """
        # TODO: Check that we are in HGS or abort here.
        transform = self.get_world_transform()

        # TODO: How to handle needing extra map metadata?
        # TODO: Easy enough for map (pass the map to the init, but what about NDCube?
        radius = self.rsun_obs.to(u.deg).value
        c_kw = {'radius': radius,
                'fill': False,
                'color': 'white',
                'zorder': 100,
                'transform': transform
                }
        c_kw.update(kwargs)

        circ = patches.Circle([0, 0], **c_kw)
        self.add_artist(circ)

        return [circ]

    # TODO: Decide on naming this, draw_grid, grid, heliographic_grid
    def heliographic_grid(self, grid_spacing: u.deg=15*u.deg, annotate=True, **kwargs):
        """
        """

    def _process_contour_input(self, *args, **kwargs):
        """
        Accept NDData as data, and accept percentage quantity as levels.
        """
        if isinstance(args[0], NDData):
            args[0] = args[0].data

        data_index = 0
        level_index = None
        if len(args) == 2:
            level_index = 1
        if len(args) == 4:
            level_index = 3
            data_index = 2

        if isinstance(args[level_index], u.Quantity) and args[level_index].unit.is_equivalent(u.percent):
            args[level_index] = args[level_index].to('percent').value * args[data_index].max()

        return args, kwargs

    @wraps(WCSAxes.contour)
    def contour(self, *args, **kwargs):
        args, kwargs = self._process_contour_input(*args, **kwargs)
        return super().contour(*args, **kwargs)

    @wraps(WCSAxes.contourf)
    def contourf(self, *args, **kwargs):
        args, kwargs = self._process_contour_input(*args, **kwargs)
        return super().contourf(*args, **kwargs)
