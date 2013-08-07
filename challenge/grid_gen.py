"""
This script creates an input grid for the game of life and stores it to the file
grid.txt

The generated grid contains several different items at random positions of the gird
"""

import random
import sys

""" puts the top left corner of a gilder at position (x,y) 
    (moves from top left to bottom right)"""
def put_glider( f, x, y ):
    f.write( str(x+0) + " " + str(y+0) + " 1\n" )
    f.write( str(x+1) + " " + str(y+1) + " 1\n" )
    f.write( str(x+1) + " " + str(y+2) + " 1\n" )
    f.write( str(x+2) + " " + str(y+0) + " 1\n" )
    f.write( str(x+2) + " " + str(y+1) + " 1\n" )

""" puts the top left corner of a LWSS at position (x,y) 
    (moves from left to right (ltr)) """
def put_LWSS_ltr( f, x, y ):
    f.write( str(x+0) + " " + str(y+0) + " 1\n" )
    f.write( str(x+3) + " " + str(y+0) + " 1\n" )
    f.write( str(x+4) + " " + str(y+1) + " 1\n" )
    f.write( str(x+0) + " " + str(y+2) + " 1\n" )
    f.write( str(x+4) + " " + str(y+2) + " 1\n" )
    f.write( str(x+1) + " " + str(y+3) + " 1\n" )
    f.write( str(x+2) + " " + str(y+3) + " 1\n" )
    f.write( str(x+3) + " " + str(y+3) + " 1\n" )
    f.write( str(x+4) + " " + str(y+3) + " 1\n" )

""" puts the top left corner of a transposed LWSS at position (x,y) 
    (moves from top to bottom (ttb))"""
def put_LWSS_ttb( f, x, y ):
    f.write( str(x+0) + " " + str(y+0) + " 1\n" )
    f.write( str(x+0) + " " + str(y+3) + " 1\n" )
    f.write( str(x+1) + " " + str(y+4) + " 1\n" )
    f.write( str(x+2) + " " + str(y+0) + " 1\n" )
    f.write( str(x+2) + " " + str(y+4) + " 1\n" )
    f.write( str(x+3) + " " + str(y+1) + " 1\n" )
    f.write( str(x+3) + " " + str(y+2) + " 1\n" )
    f.write( str(x+3) + " " + str(y+3) + " 1\n" )
    f.write( str(x+3) + " " + str(y+4) + " 1\n" )

""" puts the top left corner of a transposed LWSS at position (x,y) 
    (moves from bottom to top (btt))"""
def put_LWSS_btt( f, x, y ):
    f.write( str(x+0) + " " + str(y+1) + " 1\n" )
    f.write( str(x+0) + " " + str(y+4) + " 1\n" )
    f.write( str(x+1) + " " + str(y+0) + " 1\n" )
    f.write( str(x+2) + " " + str(y+0) + " 1\n" )
    f.write( str(x+2) + " " + str(y+4) + " 1\n" )
    f.write( str(x+3) + " " + str(y+0) + " 1\n" )
    f.write( str(x+3) + " " + str(y+1) + " 1\n" )
    f.write( str(x+3) + " " + str(y+2) + " 1\n" )
    f.write( str(x+3) + " " + str(y+3) + " 1\n" )

""" puts the top left corner of a transposed LWSS at position (x,y) 
    (moves from top to bottom (ttb))"""
def put_LWSS_rtl( f, x, y ):
    f.write( str(x+1) + " " + str(y+0) + " 1\n" )
    f.write( str(x+4) + " " + str(y+0) + " 1\n" )
    f.write( str(x+0) + " " + str(y+1) + " 1\n" )
    f.write( str(x+0) + " " + str(y+2) + " 1\n" )
    f.write( str(x+4) + " " + str(y+2) + " 1\n" )
    f.write( str(x+0) + " " + str(y+3) + " 1\n" )
    f.write( str(x+1) + " " + str(y+3) + " 1\n" )
    f.write( str(x+2) + " " + str(y+3) + " 1\n" )
    f.write( str(x+3) + " " + str(y+3) + " 1\n" )

""" puts the top left corner of a gilder at position (x,y) 
    (does not move)"""
def put_blinker( f, x, y ):
    f.write( str(x+0) + " " + str(y+0) + " 1\n" )
    f.write( str(x+1) + " " + str(y+0) + " 1\n" )
    f.write( str(x+2) + " " + str(y+0) + " 1\n" )


""" creates a grid with LWWS and transposed LWWS that move from the top and left borders
    of the grid to right and """
def create_LWWS_grid( f, xdim, ydim, nItems):
    f.write(str(xdim) + " " + str(ydim) + "\n")

    for i in range(nItems):
        if (random.randint(0,3) == 0): 
            put_LWSS_rtl( f, random.randint(0, xdim - 5), random.randint(0, ydim - 5) )
        if (random.randint(0,3) == 1): 
            put_LWSS_ltr( f, random.randint(0, xdim - 5), random.randint(0, ydim - 5) )
        if (random.randint(0,3) == 2): 
            put_LWSS_ttb( f, random.randint(0, xdim - 5), random.randint(0, ydim - 5) )
        if (random.randint(0,3) == 3): 
            put_LWSS_btt( f, random.randint(0, xdim - 5), random.randint(0, ydim - 5) )

""" creates a random grid """
def create_random_grid( f, xdim, ydim ):
    f.write(str(xdim) + " " + str(ydim) + "\n")

    for i in range(xdim):
        for j in range(ydim):
            if( random.randint(0,1) == 1 ):
                f.write(str(i) + " " + str(j) + " 1\n")

""" creates a grid populated with blinkers with uniform distances """
def create_blinker_grid( f, xdim, ydim ):
    f.write(str(xdim) + " " + str(ydim) + "\n")

    for i in range(1, xdim - 4, 4):
        for j in range(2, ydim - 2 , 4):
            put_blinker( f, i, j )


if len(sys.argv) == 4:
    xdim = int(argv[1])
    ydim = int(argv[2])
    nItems = int(argv[3])
else:
    print "USAGE: <x-dim> <y-dim> <#items to put>"
    """ default dimensions """
    xdim = 100
    ydim = 100
    nItems = 10

f = open("grid.txt","w+")
#create_LWWS_grid( f, xdim, ydim, nItems)
create_blinker_grid( f, xdim, ydim)
f.close()


