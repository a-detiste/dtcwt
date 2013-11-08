import os

import numpy as np
from dtcwt.opencl.lowlevel import colifilt
from dtcwt.lowlevel import colifilt as colifilt_gold
from dtcwt.coeffs import biort, qshift

from nose.tools import raises

from .util import assert_almost_equal, skip_if_no_cl

def setup():
    global lena
    lena = np.load(os.path.join(os.path.dirname(__file__), 'lena.npz'))['lena']

def test_lena_loaded():
    assert lena.shape == (512, 512)
    assert lena.min() >= 0
    assert lena.max() <= 1
    assert lena.dtype == np.float32

@skip_if_no_cl
@raises(ValueError)
def test_odd_filter():
    colifilt(lena, (-1,2,-1), (-1,2,1))

@skip_if_no_cl
@raises(ValueError)
def test_different_size_h():
    colifilt(lena, (-1,2,1), (-0.5,-1,2,-1,0.5))

@skip_if_no_cl
def test_zero_input():
    Y = colifilt(np.zeros_like(lena), (-1,1), (1,-1))
    assert np.all(Y[:0] == 0)

@skip_if_no_cl
@raises(ValueError)
def test_bad_input_size():
    colifilt(lena[:511,:], (-1,1), (1,-1))

@skip_if_no_cl
def test_good_input_size():
    Y = colifilt(lena[:,:511], (-1,1), (1,-1))
    Z = colifilt_gold(lena[:,:511], (-1,1), (1,-1))
    assert_almost_equal(Y,Z)

@skip_if_no_cl
def test_output_size():
    Y = colifilt(lena, (-1,1), (1,-1))
    assert Y.shape == (lena.shape[0]*2, lena.shape[1])
    Z = colifilt_gold(lena, (-1,1), (1,-1))
    assert_almost_equal(Y,Z)

@skip_if_no_cl
def test_non_orthogonal_input():
    Y = colifilt(lena, (1,1), (1,1))
    assert Y.shape == (lena.shape[0]*2, lena.shape[1])
    Z = colifilt_gold(lena, (1,1), (1,1))
    assert_almost_equal(Y,Z)

@skip_if_no_cl
def test_output_size_non_mult_4():
    Y = colifilt(lena, (-1,0,0,1), (1,0,0,-1))
    assert Y.shape == (lena.shape[0]*2, lena.shape[1])
    Z = colifilt_gold(lena, (-1,0,0,1), (1,0,0,-1))
    assert_almost_equal(Y,Z)

@skip_if_no_cl
def test_non_orthogonal_input_non_mult_4():
    Y = colifilt(lena, (1,0,0,1), (1,0,0,1))
    assert Y.shape == (lena.shape[0]*2, lena.shape[1])
    Z = colifilt_gold(lena, (1,0,0,1), (1,0,0,1))
    assert_almost_equal(Y,Z)

@skip_if_no_cl
def test_qshift():
    h0a, h0b, g0a, g0b, h1a, h1b, g1a, g1b = qshift('qshift_d')
    y = colifilt(lena, h1b, h1b)
    z = colifilt_gold(lena, h1b, h1a)
    assert_almost_equal(y, z)

@skip_if_no_cl
def test_qshift_odd_input():
    h0a, h0b, g0a, g0b, h1a, h1b, g1a, g1b = qshift('qshift_d')
    y = colifilt(lena, h1b[:-2], h1b[:-2])
    z = colifilt_gold(lena, h1a[:-2], h1b[:-2])
    assert_almost_equal(y, z)

# vim:sw=4:sts=4:et
