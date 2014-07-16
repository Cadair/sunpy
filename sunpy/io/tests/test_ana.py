"""
General ANA Tests
"""
import numpy as np
import pytest

from sunpy.io import ana

# Skip ana tests if we are on Windows or we can't import the c extension.
import platform
if platform.system() == 'Windows':
    skip_ana = True
else:
    skip_ana = False

try:
    import sunpy.io._pyana
except ImportError:
    skip_ana = True
else:
    skip_ana = skip_ana or False

# Create a test image, store it, reread it and compare
img_size = (456, 345)
img_src = np.arange(np.product(img_size))
img_src.shape = img_size
img_i8 = img_src*2**8/img_src.max()
img_i8 = img_i8.astype(np.int8)
img_i16 = img_src*2**16/img_src.max()
img_i16 = img_i16.astype(np.int16)
img_f32 = img_src*1.0/img_src.max()
img_f32 = img_f32.astype(np.float32)

@pytest.mark.skipif("skip_ana is True")
def test_i8c():
    # Test int 8 compressed functions
    ana.write('/tmp/pyana-testi8c', img_i8, 'testcase', 0)
    img_i8c_rec = ana.read('/tmp/pyana-testi8c')
    assert np.sum(img_i8c_rec[0][0] - img_i8) == 0

@pytest.mark.skipif("skip_ana is True")
def test_i8u():
    # Test int 8 uncompressed functions
    ana.write('/tmp/pyana-testi8u', img_i8, 'testcase', 0)
    img_i8u_rec = ana.read('/tmp/pyana-testi8u')
    assert np.sum(img_i8u_rec[0][0] - img_i8) == 0

@pytest.mark.skipif("skip_ana is True")
def test_i16c():
    # Test int 16 compressed functions
    ana.write('/tmp/pyana-testi16c', img_i16, 'testcase', 0)
    img_i16c_rec = ana.read('/tmp/pyana-testi16c')
    assert np.sum(img_i16c_rec[0][0] - img_i16) == 0

@pytest.mark.skipif("skip_ana is True")
def test_i16u():
    # Test int 16 uncompressed functions
    ana.write('/tmp/pyana-testi16u', img_i16, 'testcase', 0)
    img_i16u_rec = ana.read('/tmp/pyana-testi16u')
    assert np.sum(img_i16u_rec[0][0] - img_i16) == 0

@pytest.mark.skipif("skip_ana is True")
def test_f32u():
    # Test float 32 uncompressed functions
    ana.write('/tmp/pyana-testf32u', img_f32, 'testcase', 0)
    img_f32u_rec = ana.read('/tmp/pyana-testf32u')
    assert np.sum(img_f32u_rec[0][0]- img_f32) == 0

@pytest.mark.skipif("skip_ana is True")
def test_f32c():
    # Test if float 32 compressed functions
    #TODO: Bug with same code. Needs to be tracked down.

#        ana.write('/tmp/pyana-testf32c', img_f32, 1, 'testcase', 0)
#        img_f32c_rec = ana.read('/tmp/pyana-testf32c', 1)
#        assert_(np.sum(img_f32c_rec[0][1]- img_f32) == 0,
#            msg="Storing 32 bits float data without compression failed (diff: %g)" % (1.0*np.sum(img_f32c_rec[0][1] - img_f32)))
    with pytest.raises(RuntimeError):
        ana.write('/tmp/pyana-testf32c', img_f32, 'testcase', 1)
