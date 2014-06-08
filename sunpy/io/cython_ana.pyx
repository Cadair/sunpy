"""
Cython Wrapper for the ana C code instead of the large C wrapper.
"""

cimport numpy

cdef extern from "stdint.h":
    ctypedef unsigned int uint8_t

cdef extern from "src/ana/anarw.h":
    char *ana_fzhead(char *file_name)
    uint8_t *ana_fzread(char *file_name, int **ds, int *nd, char **header, int *type, int *osz)
    void ana_fzwrite(uint8_t *data, char *file_name, int *ds, int nd, char *header, int py_type)
#    void ana_fcwrite(uint8_t *data, char *file_name, int *ds, int nd, char *header, int py_type, int slice)
    
def header_read(file_name):
    return ana_fzhead(file_name)
