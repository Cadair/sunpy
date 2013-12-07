# Tomas Meszaros <exo@tty.sk>

# NOTE: All test are "disabled" until the test data will be available.

import sunpy.io  #read_file blows away RAM when using big Raster fits
from sunpy.hypermap.sources.iris import Parser
from sunpy.hypermap.coordinate_system import CoordinateSystem, CoordinateFrame

# This is temporary, Stuart Mumford will provide nice & small test samples :-)
_IRIS_SAMPLE_DATA = "/home/exo/iris_sample_data.fits"
_IRIS_RASTER_SAMPLE_DATA = "/home/exo/iris_raster_sample_data.fits"

def _test_get_header_item_group():
    hdus = sunpy.io.read_file(_IRIS_SAMPLE_DATA)
    header = hdus[0][1]
    p = Parser(header)

    assert p._get_header_item_group('DUMMY_FOO_JANE_DOE_#!@') == []
    assert p._get_header_item_group('NAXIS') != []
    assert p._get_header_item_group('CTYPE') != []
    assert p._get_header_item_group('CUNIT') != []
    assert p._get_header_item_group('CRPIX') != []
    assert p._get_header_item_group('CDELT') != []

def _test_get_header_item_group_raster():
    headers = sunpy.io.read_file_header(_IRIS_RASTER_SAMPLE_DATA)
    p0 = Parser(headers[0])

    assert p0._get_header_item_group('DUMMY_FOO_JANE_DOE_#!@') == []
    assert p0._get_header_item_group('NAXIS') == []
    assert p0._get_header_item_group('CTYPE') == []
    assert p0._get_header_item_group('CUNIT') == []
    assert p0._get_header_item_group('CRPIX') == []
    assert p0._get_header_item_group('CDELT') == []

    p1 = Parser(headers[1])

    assert p1._get_header_item_group('DUMMY_FOO_JANE_DOE_#!@') == []
    assert p1._get_header_item_group('NAXIS') != []
    assert p1._get_header_item_group('CTYPE') != []
    assert p1._get_header_item_group('CUNIT') != []
    assert p1._get_header_item_group('CRPIX') != []
    assert p1._get_header_item_group('CDELT') != []

def _test_make_coord_system():
    hdus = sunpy.io.read_file(_IRIS_SAMPLE_DATA)
    header = hdus[0][1]
    p = Parser(header)
    s = p.get_coordinate_system("Coordinate Test System")

    assert isinstance(s, CoordinateSystem)
    for i in s.frames:
        assert isinstance(i, CoordinateFrame)
        assert type(i.system) == str and i.system != ""
        assert type(i.pixel_size) == float and i.pixel_size > 0
        assert type(i.number_of_pixels) == int and i.number_of_pixels > 0
        assert type(i.num_axes) == int and i.num_axes > 0
        assert type(i.axes_names) == list or i.axes_names is None
        assert type(i.units) == list or i.units is None

def _test_make_raster_coord_system():
    headers = sunpy.io.read_file_header(_IRIS_RASTER_SAMPLE_DATA)
    p1 = Parser(headers[1])
    s1 = p1.get_coordinate_system("Coordinate Test System")

    assert isinstance(s1, CoordinateSystem)
    for i in s1.frames:
        assert isinstance(i, CoordinateFrame)
        assert type(i.system) == str and i.system != ""
        assert type(i.pixel_size) == float and i.pixel_size > 0
        assert type(i.number_of_pixels) == int and i.number_of_pixels > 0
        assert type(i.num_axes) == int and i.num_axes > 0
        assert type(i.axes_names) == list or i.axes_names is None
        assert type(i.units) == list or i.units is None


# ================== #
# Just for debugging #
# ================== #

def _show_coordinate_system():
    hdus = sunpy.io.read_file(_IRIS_SAMPLE_DATA)
    header = hdus[0][1]
    p = Parser(header)
    s = p.get_coordinate_system("Coordinate Test System")

    print "=" * len(s.name)
    print s.name
    print "=" * len(s.name)

    for f in s.frames:
        print "            system: %s" % f.system
        print "reference_position: %f" % f.reference_position
        print "        pixel_size: %f" % f.pixel_size
        print "  number_of_pixels: %d" % f.number_of_pixels
        print "          num_axes: %d" % f.num_axes
        print "        axes_names: %s" % f.axes_names
        print "             units: %s" % f.units
        print "=" * len(s.name)

def _show_raster_coordinate_system():
    headers = sunpy.io.read_file_header(_IRIS_RASTER_SAMPLE_DATA)

    for i in range(1,5):
        p = Parser(headers[i])
        s = p.get_coordinate_system("Coordinate Test System " + str(i))

        print "=" * len(s.name)
        print s.name
        print "=" * len(s.name)

        for f in s.frames:
            print "            system: %s" % f.system
            print "reference_position: %f" % f.reference_position
            print "        pixel_size: %f" % f.pixel_size
            print "  number_of_pixels: %d" % f.number_of_pixels
            print "          num_axes: %d" % f.num_axes
            print "        axes_names: %s" % f.axes_names
            print "             units: %s" % f.units
            print "=" * len(s.name)