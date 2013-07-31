#cython: boundscheck=False
#cython: nonecheck=False
#cython: wraparoun=False

import numpy
cimport numpy

def _life_step(long[:,::1] g,
               long[:,::1] gnew):
    """Given a grid, compute one Game of Life step along the interior of the grid into gnew"""

    cdef:
        Py_ssize_t m,n
        Py_ssize_t i,j,ii,jj
        long sum
        long g_val

    m,n = g.shape[0],g.shape[1]

    for i in range(1,m-1):
        for j in range(1,n-1):
            sum = 0

            for ii in xrange(i-1,i+2):
                for jj in xrange(j-1,j+2):
                    if ii == i and jj == j:
                        continue
                    sum += g[ii,jj]

            if sum < 2 or sum > 3:
                gnew[i,j] = 0
            elif sum == 3:
                gnew[i,j] = 1
            else:
                g_val = g[i,j]
                gnew[i,j] = g_val

    return
