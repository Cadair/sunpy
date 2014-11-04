"""
Cython Wrapper for the ana C code instead of the large C wrapper.
"""

import numpy as np
cimport numpy as np

ctypedef np.uint8_t numpy_unit8

cdef extern from "stdint.h":
    ctypedef unsigned int uint8_t

cdef extern from "src/ana/anarw.h":
    int INT8, INT16, INT32, INT64, FLOAT32, FLOAT64
    char *ana_fzhead(char *file_name)
    uint8_t *ana_fzread(char *file_name, int **ds, int *nd, char **header, int *type, int *osz)
    void ana_fzwrite(uint8_t *data, char *file_name, int *ds, int nd, char *header, int py_type)
    void ana_fcwrite(uint8_t *data, char *file_name, int *ds, int nd, char *header, int py_type, int slice)


cdef class ArrayWrapper:
    """
    An array wrapper to deallocate the C array.
    Borrowed from:
    http://gael-varoquaux.info/blog/?p=157
    """

    cdef void* data_ptr
    cdef int size
     
    cdef set_data(self, int size, void* data_ptr):
        """
        Set the data of the array
         
        This cannot be done in the constructor as it must recieve C-level
        arguments.
         
        Parameters:
        -----------
        size: int
            Length of the array.
        data_ptr: void*
            Pointer to the data
        """
        self.data_ptr = data_ptr
        self.size = size
     
    def __array__(self):
        """ Here we use the __array__ method, that is called when numpy
        tries to get an array from the object."""
        cdef np.npy_intp shape[1]
        shape[0] = <np.npy_intp> self.size
        # Create a 1D array, of length 'size'
        ndarray = np.PyArray_SimpleNewFromData(1, shape,
        np.NPY_INT, self.data_ptr)
        return ndarray
     
    def __dealloc__(self):
        """ Frees the array. This is called by Python when all the
        references to the object are gone. """
        free(<void*>self.data_ptr)


def read_header(file_name):
    return ana_fzhead(file_name)
    
def read(file_name):
    # Init ANA IO variables
    cdef char *header			# ANA header (comments)
    cdef uint8_t *anaraw		# Raw data
    cdef int	ndim=-1, dtype=-1, *pshape, size=-1, # Various properties
    
    anaraw = ana_fzread(file_name, &pshape, &ndim, &header, &dtype, &size)
    
    # Select Type
    if dtype == INT8:
        npdtype = np.NPY_INT8
    elif dtype == INT16:
        npdtype = np.NPY_INT16
    elif dtype == INT32:
        npdtype = np.NPY_INT32
    elif dtype == INT64:
        npdtype = np.NPY_INT64
    elif dtype == FLOAT32:
        npdtype = np.NPY_FLOAT32
    elif dtype == FLOAT64:
        npdtype = np.NPY_FLOAT64
    else:
        raise TypeError("The type of the data array {0} is not supported".format(dtype))
  
    cdef np.npy_intp* nshape = <np.npy_intp*> pshape
    #cdef np.npy_intp* npdim = <np.npy_intp*> ndim
    
    return ndarray

def write(file_name, np.ndarray data, comments='', compress=False):
    cdef int ndim = data.ndim
    cdef np.ndarray shape = np.array((data.shape[0], data.shape[1]), dtype=int)

    cdef int *pshape = <int*> shape.data
    cdef uint8_t *cdata = <uint8_t*> data.data
    
    # Select Type
    cdef int dtype
    if data.dtype == np.int8:
        dtype = INT8
    elif data.dtype == np.int16:
        dtype = INT16
    elif data.dtype == np.int32:
        dtype = INT32
    elif data.dtype == np.int64:
        dtype = INT64
    elif data.dtype == np.float32:
        dtype = FLOAT32
    elif data.dtype == np.float64:
        dtype = FLOAT64
    else:
        raise TypeError("The type of the data array {0} is not supported".format(data.dtype))

    if compress:
        ana_fcwrite(cdata, file_name, pshape, ndim, comments, dtype, 5)
    else:
        ana_fzwrite(cdata, file_name, pshape, ndim, comments, dtype)

def write_slice(filename):
    pass
