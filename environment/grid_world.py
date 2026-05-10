import random
import numpy as np

from environment.agent import Agent
from environment.fire import spread_fire

from utils.constants import *


class GridWorld:

    def __init__(self,
                 grid_size,
                 num_agents,
                 fire_spread_prob):

        self.grid_size = grid_size
        self.num_agents = num_agents
        self.fire_spread_prob = fire_spread_prob

        self.grid = np.zeros((grid_size, grid_size), dtype=int)

        self.agents = []

        self.initialize_environment()

    def random_empty_cell(self):

        while True:

            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)

            if self.grid[x][y] == EMPTY:
                return (x, y)

    def random_empty_boundary_cell(self):

        while True:

            edge = random.randint(0, 3)
            if edge == 0:
                x = 0
                y = random.randint(0, self.grid_size - 1)
            elif edge == 1:
                x = self.grid_size - 1
                y = random.randint(0, self.grid_size - 1)
            elif edge == 2:
                x = random.randint(0, self.grid_size - 1)
                y = 0
            else:
                x = random.randint(0, self.grid_size - 1)
                y = self.grid_size - 1

            if self.grid[x][y] == EMPTY:
                return (x, y)

    def initialize_environment(self):

        # Obstacles
        for _ in range(12):

            x, y = self.random_empty_cell()
            self.grid[x][y] = OBSTACLE

        # Exit Gates
        for _ in range(2):

            x, y = self.random_empty_boundary_cell()
            self.grid[x][y] = EXIT

        # Initial Fire
        for _ in range(2):

            x, y = self.random_empty_cell()
            self.grid[x][y] = FIRE

        # Agents
        for i in range(self.num_agents):

            pos = self.random_empty_cell()

            agent = Agent(i, pos)

            self.agents.append(agent)

    def step(self):

        proposed_moves = {}

        # Random movement for now
        for agent in self.agents:

            if not agent.alive or agent.evacuated:
                continue

            action = random.randint(0, 4)

            new_pos = agent.move(action, self.grid_size)

            proposed_moves[agent.id] = new_pos

        # Collision handling
        occupied = {}

        for aid, pos in proposed_moves.items():

            if pos not in occupied:
                occupied[pos] = [aid]

            else:
                occupied[pos].append(aid)

        # Apply valid moves
        for pos, ids in occupied.items():

            if len(ids) == 1:

                aid = ids[0]

                agent = self.agents[aid]

                x, y = pos

                if self.grid[x][y] == OBSTACLE:
                    continue

                agent.position = pos

                if self.grid[x][y] == FIRE:
                    agent.alive = False

                if self.grid[x][y] == EXIT:
                    agent.evacuated = True

        # Spread fire
        self.grid = spread_fire(
            self.grid,
            self.fire_spread_prob
        )

        # Fire kills agents
        for agent in self.agents:

            if not agent.alive:
                continue

            x, y = agent.position

            if self.grid[x][y] == FIRE:
                agent.alive = False