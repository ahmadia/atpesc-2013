import numpy as np
import numpy.testing as npt

from life import life_step, build_grids, build_local_grids, setup_4
from life import setup_parallel, Comms
from _life import _life_step
from mpi4py import MPI

size = (4,4)
glide_size = (16,16)

def hash_grid(g, s):
    """Compute hash of grid/slice.

    Given a grid and a slice defining its range, compute hash using a
    hash function that can be reduced over subgrids by summation """ 

    X = np.mgrid[s]
    h = 0
    for i in range(X.shape[0]):
        h += np.sum((X[i] + 1)*g)
    return h

def test_ones():
    """check that all ones gives right result"""
    A = np.ones(size, dtype=np.int64)
    B = np.zeros_like(A)

    life_step(A,B)

    npt.assert_equal(A, np.ones(size))
    npt.assert_equal(B, np.zeros(size))
    
    
def test_zeros():
    """check that all zeros gives right result"""
    
    A = np.zeros(size, dtype=np.int64)
    B = np.zeros_like(A)

    life_step(A,B)

    npt.assert_equal(A, np.zeros(size))
    npt.assert_equal(B, np.zeros(size))
    
    
def test_block():
    """check that an internal block gives the right result"""
    
    A = np.zeros(size, dtype=np.int64)
    A[1:2][1:2] = 1
    B = np.zeros_like(A)
    C = A.copy()
    
    life_step(A,B)

    npt.assert_equal(A, B)
    npt.assert_equal(A, C)    
    
    
def test_two_blocks():
    """check that an internal block is correctly preserved"""
    
    A = np.zeros(size, dtype=np.int64)
    A[1:2][1:2] = 1
    B = np.zeros_like(A)
    C = A.copy()

    life_step(A,B)
    life_step(B,A)
    
    npt.assert_equal(A, B)
    npt.assert_equal(A, C)
    
def test_glider(step=life_step):
    """check that a glider moves correctly"""

    G = np.zeros((3,3), dtype=np.int64)
    G[0,1] = 1
    G[1,2] = 1
    G[2,0:3] = 1
    
    A = np.zeros(glide_size, dtype=np.int64)
    B = np.zeros_like(A)

    A[1:4,1:4] = G
    
    step(A,B)
    
    C = np.zeros_like(A)
    C[2][[1,3]] = 1
    C[3,2:4] = 1
    C[4,2] = 1
    
    npt.assert_equal(B, C)

def test_cython():
    test_glider(step=_life_step)
    
def test_communicate():
    """Verify communications between processes"""

    shape = (8,8)
    A = np.random.randint(0,2,shape)
    
    ng = (2, 2)
    sliceA, slices, grids = build_grids(A, ng)
    local_grids = build_local_grids(A, ng)
    
    # check that subgrids match before we start
    hashes = [hash_grid(g, s) for g, s in zip(grids, slices)]
    assert(sum(hashes) == hash_grid(A, sliceA))
        
    grids, comm_all = setup_4(A, local_grids, ng)
    
    comm_all()
    
    c_hashes = [hash_grid(g, s) for g, s in zip(grids, slices)]
    
    assert(sum(hashes) == hash_grid(A, sliceA))
    assert(sum(c_hashes) == hash_grid(A, sliceA))
    
def test_communicating_steps():
    """Verify communications in running code between processes"""

    shape = (4,4)
    A = np.random.randint(0,2,shape)

    B = A.copy()
    B_swap = B.copy()
    
    ng = (2, 2)
    sliceA, slices, grids = build_grids(A, ng)
    local_grids = build_local_grids(A, ng)

    swap_local_grids = [local_grid.copy() for local_grid in local_grids]
    
    # check that subgrids match before we start
    hashes = [hash_grid(g, s) for g, s in zip(grids, slices)]
    assert(sum(hashes) == hash_grid(A, sliceA))
        
    grids, comm_all = setup_4(A, local_grids, ng)
    swap_grids, swap_comm_all = setup_4(A, swap_local_grids, ng)
    
    iters = 10

    for i in range(iters):
        comm_all()
        
        for grid, swap_local_grid in zip(local_grids, swap_local_grids):
            life_step(grid, swap_local_grid)
            
        (local_grids, comm_all, grids, swap_local_grids, swap_comm_all, swap_grids) = \
            swap_local_grids, swap_comm_all, swap_grids, local_grids, comm_all, grids
    
        life_step(B, B_swap)
        B_swap, B = B, B_swap

        hashes = [hash_grid(g, s) for g, s in zip(grids, slices)]

        if sum(hashes) != hash_grid(B, sliceA):       
            for grid in swap_local_grids:
                print grid
            print '-'*40
            print B_swap

            print '*'*40
            for grid in local_grids:
                print grid
            print '-'
            print B

    hashes = [hash_grid(g, s) for g, s in zip(grids, slices)]
             
    assert(sum(hashes) == hash_grid(B, sliceA))

def test_4_cart_neighbors():

    size = MPI.COMM_WORLD.Get_size()
    ngs = np.sqrt(size)
    ng = [ngs, ngs]

    comms = Comms()
    cart = comms.cart

    rank = cart.Get_rank()
    coords = cart.Get_coords(rank)

    shape = (16,16)
    A = np.random.randint(0,2,shape)
    A = cart.bcast(A)

    if size != 4:
        return

    neighbors = [comms.left, comms.right, comms.up, comms.down]

    assert(sum([1 for n in neighbors if n is not None]) == 2)
    assert(sum([n for n in neighbors if n is not None]) == 3)
    assert(rank not in neighbors)
    
def test_parallel_communication():
    """Verify parallel communication on processes"""

    # build un-decomposed array on each process
    # you would never do this in a real code

    A, l1, l2, sg, grid, comms = setup_parallel()

    cart = comms.cart

    shape = A.shape
    sliceA = [slice(0,s) for s in shape]

    B = A.copy()
    A_swap = A.copy()

    # check that subgrids match before we start
    h = hash_grid(grid, sg)

    h = np.array(h, dtype=np.int64)
    h_sum = np.empty_like(h)

    cart.Reduce([h, MPI.LONG], [h_sum, MPI.LONG], op=MPI.SUM, root=0)

    rank = cart.Get_rank()
    size = cart.Get_size()
    
    if rank == 0:
        assert(h_sum == hash_grid(A, sliceA))

    comms.comm_start_1(l1)

    comms.comm_end()

    comms.comm_start_2(l1)

    comms.comm_end()

    h = hash_grid(grid, sg)
    h = np.array(h, dtype=np.int64)

    cart.Reduce([h, MPI.LONG], [h_sum, MPI.LONG], op=MPI.SUM, root=0)

    if rank == 0:
        assert(h_sum == hash_grid(B, sliceA))
    
if __name__ == '__main__':
    test_parallel_communication()
    test_ones()
    test_zeros()
    test_block()
    test_two_blocks()
    test_glider()
    test_communicate()
    test_communicating_steps()
    test_cython()
    test_4_cart_neighbors()
