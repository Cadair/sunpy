"""
Cython Wrapper for the ana C code instead of the large C wrapper.
"""
cdef extern from "stdint.h":
    ctypedef unsigned int uint8_t

cdef extern from "ana/anarw.h":
    char *ana_fzhead(char *file_name)
    uint8_t *ana_fzread(char *file_name, int **ds, int *nd, char **header, int *type, int *osz)
    void ana_fzwrite(uint8_t *data, char *file_name, int *ds, int nd, char *header, int py_type)
    void ana_fcwrite(uint8_t *data, char *file_name, int *ds, int nd, char *header, int py_type, int slice)

#cdef ana_fzwrite(file_name):
#    ana_fzwrite(file_name):

def read_header(file_name):
    pass
    
def read(filename):
    pass
    
def write(uint8_t *data, file_name, int ds ,nd, header, py_type):
    ana_fzwrite(data, file_name, int ds, nd, header, py_type)

def write_slice(filename):
    pass