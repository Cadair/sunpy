"""
Cython Wrapper for the ana C code instead of the large C wrapper.
"""

import numpy as np
cimport numpy as cnp

ctypedef cnp.uint8_t numpy_unit8

cdef extern from "stdint.h":
    ctypedef unsigned int uint8_t

cdef extern from "src/ana/anarw.h":
    char *ana_fzhead(char *file_name)
    uint8_t *ana_fzread(char *file_name, int **ds, int *nd, char **header, int *type, int *osz)
    void ana_fzwrite(uint8_t *data, char *file_name, int *ds, int nd, char *header, int py_type)
    void ana_fcwrite(uint8_t *data, char *file_name, int *ds, int nd, char *header, int py_type, int slice)

def read_header(file_name):
    return ana_fzhead(file_name)
    
def read(filename):
    pass
    
def write(file_name, cnp.ndarray data, comments='', compress=False):
    cdef int ndim = data.ndim
    cdef cnp.ndarray shape = np.array((data.shape[0], data.shape[1]), dtype=int)

    cdef int *pshape = <int*> shape.data
    cdef uint8_t *cdata = <uint8_t*> data.data 

    
    if compress:
        ana_fcwrite(cdata, file_name, pshape, ndim, comments, 1, 5)
    else:
        ana_fzwrite(cdata, file_name, pshape, ndim, comments, 1)

def write_slice(filename):
    pass
