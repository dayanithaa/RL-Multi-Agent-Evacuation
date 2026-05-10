import random
import numpy as np

from environment.agent import Agent
from environment.fire import spread_fire

from utils.constants import *

from config import *


class GridWorld:

    def __init__(self):

        self.grid_size = GRID_SIZE

        self.num_agents = NUM_AGENTS

        self.fire_spread_prob = FIRE_SPREAD_PROB

        self.reset()

    def reset(self):

        self.grid = np.zeros(
            (self.grid_size, self.grid_size),
            dtype=np.int32
        )

        self.agents = []

        self.place_obstacles()

        self.place_exits()

        self.place_fire()

        self.place_agents()

        self.steps = 0

        return self.get_all_observations()

    def random_empty_cell(self):

        while True:

            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)

            if self.grid[x][y] == EMPTY:

                occupied = False

                for agent in self.agents:

                    if agent.position == (x, y):
                        occupied = True

                if not occupied:
                    return (x, y)

    def random_boundary_cell(self):

        while True:

            side = random.choice([
                "top",
                "bottom",
                "left",
                "right"
            ])

            if side == "top":
                x = 0
                y = random.randint(0, self.grid_size - 1)

            elif side == "bottom":
                x = self.grid_size - 1
                y = random.randint(0, self.grid_size - 1)

            elif side == "left":
                x = random.randint(0, self.grid_size - 1)
                y = 0

            else:
                x = random.randint(0, self.grid_size - 1)
                y = self.grid_size - 1

            if self.grid[x][y] == EMPTY:
                return (x, y)

    def place_obstacles(self):

        for y in range(2, 8):

            self.grid[4][y] = OBSTACLE

        self.grid[4][5] = EMPTY

        for x in range(1, 6):

            self.grid[x][7] = OBSTACLE

        self.grid[3][7] = EMPTY

    def place_exits(self):

        for _ in range(NUM_EXITS):

            x, y = self.random_boundary_cell()

            self.grid[x][y] = EXIT

    def place_fire(self):

        for _ in range(2):

            x, y = self.random_empty_cell()

            self.grid[x][y] = FIRE

    def place_agents(self):

        for i in range(self.num_agents):

            pos = self.random_empty_cell()

            self.agents.append(
                Agent(i, pos)
            )

    def get_local_observation(self, agent):

        obs_size = 3

        radius = 1

        obs = np.ones(
            (obs_size, obs_size),
            dtype=np.float32
        )

        ax, ay = agent.position

        for dx in range(-radius, radius + 1):

            for dy in range(-radius, radius + 1):

                nx = ax + dx
                ny = ay + dy

                ox = dx + radius
                oy = dy + radius

                if 0 <= nx < self.grid_size and \
                   0 <= ny < self.grid_size:

                    obs[ox][oy] = self.grid[nx][ny]

        for other_agent in self.agents:

            if other_agent.id == agent.id:
                continue

            if not other_agent.alive:
                continue

            x, y = other_agent.position

            rx = x - ax + radius
            ry = y - ay + radius

            if 0 <= rx < obs_size and \
               0 <= ry < obs_size:

                obs[rx][ry] = 4

        obs[radius][radius] = 5

        return obs.flatten()

    def get_all_observations(self):

        observations = []

        for agent in self.agents:

            observations.append(
                self.get_local_observation(agent)
            )

        return observations

    def step(self, actions):

        rewards = [0 for _ in range(self.num_agents)]

        proposed_moves = {}

        old_positions = {}

        # Action selection
        for i, agent in enumerate(self.agents):

            if not agent.alive or agent.evacuated:
                continue

            old_positions[i] = agent.position

            new_pos = agent.move(
                actions[i],
                self.grid_size
            )

            proposed_moves[i] = new_pos

        # Collision resolution
        move_counts = {}

        for aid, pos in proposed_moves.items():

            if pos not in move_counts:
                move_counts[pos] = []

            move_counts[pos].append(aid)

        for pos, ids in move_counts.items():

            if len(ids) > 1:

                for aid in ids:

                    rewards[aid] -= 10

                    proposed_moves[aid] = \
                        old_positions[aid]

        # Apply moves
        for aid, pos in proposed_moves.items():

            agent = self.agents[aid]

            x, y = pos

            if self.grid[x][y] == OBSTACLE:

                rewards[aid] -= 2

                continue

            agent.position = pos

            rewards[aid] -= 1

            if self.grid[x][y] == FIRE:

                agent.alive = False

                rewards[aid] -= 50

                for j in range(self.num_agents):

                    if j != aid:
                        rewards[j] -= 10

            if self.grid[x][y] == EXIT:

                if not agent.evacuated:

                    agent.evacuated = True

                    rewards[aid] += 50

                    for j in range(self.num_agents):

                        if j != aid:
                            rewards[j] += 8

        # Fire spread
        self.grid = spread_fire(
            self.grid,
            self.fire_spread_prob
        )

        # Fire proximity penalty
        for i, agent in enumerate(self.agents):

            if not agent.alive:
                continue

            x, y = agent.position

            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:

                    nx = x + dx
                    ny = y + dy

                    if 0 <= nx < self.grid_size and \
                       0 <= ny < self.grid_size:

                        if self.grid[nx][ny] == FIRE:

                            rewards[i] -= 5

        self.steps += 1

        done = self.is_done()

        if self.all_safe():

            rewards = [r + 100 for r in rewards]

        observations = self.get_all_observations()

        return observations, rewards, done

    def all_safe(self):

        for agent in self.agents:

            if not agent.evacuated:
                return False

        return True

    def is_done(self):

        if self.steps >= MAX_STEPS:
            return True

        alive_exists = False

        for agent in self.agents:

            if agent.alive and not agent.evacuated:
                alive_exists = True

        return not alive_exists