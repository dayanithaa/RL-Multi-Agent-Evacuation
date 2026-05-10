import random

from utils.constants import *


def spread_fire(grid, spread_prob):

    rows = len(grid)
    cols = len(grid[0])

    new_fires = []

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    for i in range(rows):

        for j in range(cols):

            if grid[i][j] == FIRE:

                for dx, dy in directions:

                    nx = i + dx
                    ny = j + dy

                    if 0 <= nx < rows and 0 <= ny < cols:

                        if grid[nx][ny] in [EMPTY]:

                            if random.random() < spread_prob:

                                new_fires.append((nx, ny))

    for x, y in new_fires:

        grid[x][y] = FIRE

    return grid