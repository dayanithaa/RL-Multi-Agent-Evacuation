import pygame
import time

from config import *

from environment.grid_world import GridWorld
from renderer.pygame_renderer import Renderer


def main():

    env = GridWorld(
        GRID_SIZE,
        NUM_AGENTS,
        FIRE_SPREAD_PROB
    )

    renderer = Renderer(GRID_SIZE)

    clock = pygame.time.Clock()

    running = True

    step = 0

    while running and step < MAX_STEPS:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

        env.step()

        renderer.draw(
            env.grid,
            env.agents
        )

        clock.tick(FPS)

        step += 1

    pygame.quit()


if __name__ == "__main__":
    main()