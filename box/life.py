from numba import autojit

import itertools

def communicate(grid, left, right, up, down):
    """ Communicates grid data.  
    
    Performs a simulated inner 'put' from grid into two left-right neighbors, then a full 'put' from grid into up-down neighbors"""

    if left != None:
        left[1:-1,-1] = grid[1:-1,1]

    if right != None:
        right[1:-1,0] = grid[1:-1,-2]

    if up != None:
        up[-1,:] = grid[1,:]

    if down != None:
        down[0,:] = grid[-2,:]

def build_grids(A, ng):
    """Create a decomposition of the grids on A"""
    
    shape = A.shape
    gridl = [s/n for s,n in zip(shape,ng)]
    gs = [[l * i for i in range(ngi)] for ngi,l in zip(ng,gridl)]
    gs = list(itertools.product(*gs))
    slices = [[(slice(i,i+l)) for i, l in zip(gsi,gridl)] for gsi in gs]
    sliceA = [slice(0,s) for s in shape]
    return sliceA, slices, [A[i] for i in slices]
    
def build_local_grids(A, ng):
    """Create a copy of the local grids on A"""
    
    shape = A.shape
    gridl = [s/n for s,n in zip(shape,ng)]

    lgs = [[l*i-1 if i > 0 else 0 for i in range(ngi)] for ngi,l in zip(ng, gridl)]
    lge = [[l*(i+1)+1 if i+1 < ngi else l*(i+1) for i in range(ngi)] for ngi,l in zip(ng, gridl)]
    lgs = list(itertools.product(*lgs))
    lge = list(itertools.product(*lge))
    lslices = [[slice(i,j) for i, j in zip(gsi, gei)] for gsi, gei in zip(lgs, lge)]
    return [A[i].copy() for i in lslices]
    
def setup_4(A, local_grids, ng):    
    l_00, l_01, l_10, l_11 = [grid for grid in local_grids]
    
    n_00 = (None, l_01, None, l_10)
    n_01 = (l_00, None, None, l_11)
    n_10 = (None, l_11, l_00, None)
    n_11 = (l_10, None, l_01, None)  
    
    shape = A.shape
    gridl = [s/n for s,n in zip(shape,ng)]

    m0 = gridl[0]
    m1 = gridl[1]
    
    g_00 = l_00[:m0,:m1]
    l_00[m0,:] = 0
    l_00[1:m0-1,m1] = 0
    
    g_01 = l_01[:m0,1:]
    l_01[m0,:] = 0
    l_01[1:m0-1,0] = 0
    
    g_10 = l_10[1:,:m1]
    l_10[0,:] = 0
    l_10[1:m0-1,m1] = 0
        
    g_11 = l_11[1:,1:]
    l_11[0,:] = 0
    l_11[1:m1-1,0] = 0

    def comm_all():
        communicate(l_00, *n_00[:2] + (None, None))
        communicate(l_01, *n_01[:2] + (None, None))
        communicate(l_10, *n_10[:2] + (None, None))
        communicate(l_11, *n_11[:2] + (None, None))
        communicate(l_00, *(None, None) + n_00[2:])
        communicate(l_01, *(None, None) + n_01[2:])
        communicate(l_10, *(None, None) + n_10[2:])
        communicate(l_11, *(None, None) + n_11[2:])
    
    grids = (g_00, g_01, g_10, g_11)
    
    return grids, comm_all

@autojit
def life_step(g, gnew):
    """Given a grid, compute one Game of Life step along the interior of the grid into gnew"""
    
    m,n = g.shape
    
    for i in range(1,m-1):
        for j in range(1,n-1):

            sum = 0

            for ii in range(i-1,i+2):
                for jj in range(j-1,j+2):
                    if ii == i and jj == j:
                        continue
                    sum += g[ii,jj]
            
            if sum < 2 or sum > 3:
                gnew[i,j] = 0
            elif sum == 3:
                gnew[i,j] = 1
            else:
                gnew[i,j] = g[i,j]    
