try: 
    from numba import autojit
except ImportError:
    print "Unable to import numba, life_step will not be accelerated"
    def autojit(func):
        return func
    
import itertools
import numpy as np
from mpi4py import MPI

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

        
def parallel_communicate(grid, left, right, up, down):
    """ Communicates parallel grid data.  
    
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



class Comms:
    """encapsulates cartesian communications"""
    
    def __init__(self):
        size = MPI.COMM_WORLD.Get_size()
        ngs = int(np.sqrt(size))
        ng = [ngs, ngs]

        cart = MPI.COMM_WORLD.Create_cart(ng, reorder=True)

        self.left_buf = None
        self.right_buf = None
        
        coords = cart.coords
        c = np.asarray(coords)

        self.ng = ng
        self.cart = cart
        self.reqs = []
        
        # get neighbors filtered by boundaries
        self.left = cart.Get_cart_rank(c - [0,1]) if c[1] > 0 else None
        self.right = cart.Get_cart_rank(c + [0,1]) if c[1] < ng[1] - 1 else None
        self.down = cart.Get_cart_rank(c - [1,0]) if c[0] > 0  else None
        self.up = cart.Get_cart_rank(c + [1,0]) if c[0] < ng[0] - 1 else None

        self.left_sbuf = None
        self.left_rbuf = None
        self.right_sbuf = None
        self.right_rbuf = None

        self.buffered_grid = None

        rank = self.cart.Get_rank()
        
    def comm_start_1(self, grid):
        cart = self.cart

        # special handling for non-contiguous data
        if self.left_sbuf is None:
            self.left_sbuf = np.empty((grid.shape[0]-2), np.int)
        if self.left_rbuf is None:
            self.left_rbuf = np.empty((grid.shape[0]-2), np.int)

        if self.right_sbuf is None:
            self.right_sbuf = np.empty((grid.shape[0]-2), np.int)
        if self.right_rbuf is None:
            self.right_rbuf = np.empty((grid.shape[0]-2), np.int)
        
        
        if self.left is not None:
            self.left_sbuf[:] = grid[1:-1, 1]
            self.reqs += [cart.Irecv(self.left_rbuf, self.left),
                          cart.Isend(self.left_sbuf, self.left)] 
                          
        if self.right is not None:
            self.right_sbuf[:] = grid[1:-1,-2]
            self.reqs += [cart.Irecv(self.right_rbuf, self.right),
                          cart.Isend(self.right_sbuf, self.right)]
        self.buffered_grid = grid
            
    def comm_start_2(self, grid):
        cart = self.cart

        if self.up is not None:
            self.reqs += [cart.Irecv(grid[-1,:], self.up), 
                          cart.Isend(grid[-2,:], self.up)]
        if self.down is not None:
            self.reqs += [cart.Irecv(grid[0,:], self.down),
                          cart.Isend(grid[1,:], self.down)]

    def comm_end(self):

        rank = self.cart.Get_rank()

        MPI.Request.Waitall(self.reqs)

        if self.buffered_grid is not None:
            if self.right is not None:
                self.buffered_grid[1:-1,-1] = self.right_rbuf[:] 
            if self.left is not None:
                self.buffered_grid[1:-1, 0] = self.left_rbuf[:]
            self.buffered_grid = None

            
def setup_parallel():
    """Builds and distributes parallel grids"""

    comms = Comms()
    shape = (64,64)

    A = np.random.randint(0,2,shape)

    cart = comms.cart
    ng   = comms.ng
    A = cart.bcast(A)
    rank = cart.Get_rank()
    my_coords = cart.Get_coords(rank)
    
    gridl = [s/n for s,n in zip(shape,ng)]

    gs = [int(l*i) for i,l in zip(my_coords, gridl)]
    ge = [int(l*(i+1)) for i,l in zip(my_coords, gridl)]
    
    lgs = [l*i-1 if i > 0 else 0 for i, l in zip(my_coords, gridl)]
    lge = [l*(i+1)+1 if l*(i+1)+1 <= s  else l*(i+1) for i, l, s in zip(my_coords, gridl, shape)]    

    sg = [slice(s,e) for s,e in zip(gs, ge)]
    sl = [slice(s,e) for s,e in zip(lgs, lge)]
    
    grid = A[sg]
    
    l1 = A[sl]
    l2 = l1.copy()

    return A, l1, l2, sg, grid, comms
    
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
