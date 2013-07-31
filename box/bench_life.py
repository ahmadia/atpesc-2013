import numpy as np
from life import life_step
import time

def bench_life_step():
    """ measures how many iterations per second the life step is capable of """
    
    glide_size = [1024,1024]
    
    A = np.random.randint(0,2,glide_size)
    B = np.zeros_like(A)

    iters = 100

    start = time.time()

    # cold life_step to throw away
    life_step(A,B)
    
    for i in range(iters):
        life_step(A,B)
        life_step(B,A)

    t = time.time() - start

    print "iters/s for grid: %d,%d: %g" % (glide_size[0], glide_size[1], 
                                           iters/t)

if __name__ == "__main__":
    bench_life_step()
