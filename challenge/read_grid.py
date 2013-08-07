import sys

def print_grid(grid):
    for i in range(len(grid)):
        line = ''
        for j in range(len(grid[0])):
            if( grid[i][j] == 0 ):
                line += '.'
            else:
                line += '#'
        print line

def read_grid(filename):

    f = open(filename)
    words = f.readline().split()
    xdim = int(words[0])
    ydim = int(words[1])

    grid = [[0] * xdim for i in range(ydim)]

    for l in f:
        words = l.split()
        grid[ int(words[1]) ] [ int(words[0]) ] = 1

    f.close()

    return grid

def life_step(grid):

    xdim = len(grid[0])
    ydim = len(grid)

    grid_new = [[0] * xdim for i in range(ydim)]

    for i in range(1,ydim-1):
        for j in range(1,xdim-1):
            sum = 0
            sum += grid[i+1][j]
            sum += grid[i-1][j]
            sum += grid[i][j+1]
            sum += grid[i][j-1]
            sum += grid[i-1][j+1]
            sum += grid[i-1][j-1]
            sum += grid[i+1][j-1]
            sum += grid[i+1][j+1]

            if( grid[i][j] and sum == 2 or sum == 3 ):
                grid_new[i][j] = 1

    return grid_new



def game_of_life(numIter):
    grid = read_grid(sys.argv[1])
    xdim = len(grid[0])
    ydim = len(grid)

    for i in range(numIter):
        grid = life_step(grid)
        print_grid(grid)


game_of_life(100)

