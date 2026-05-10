import pygame

from utils.constants import *


class Renderer:

    def __init__(self, grid_size):

        pygame.init()

        self.grid_size = grid_size

        self.width = grid_size * CELL_SIZE
        self.height = grid_size * CELL_SIZE

        self.screen = pygame.display.set_mode(
            (self.width, self.height)
        )

        pygame.display.set_caption(
            "Multi-Agent Fire Evacuation"
        )

    def draw(self, grid, agents):

        self.screen.fill(WHITE)

        for i in range(self.grid_size):

            for j in range(self.grid_size):

                rect = pygame.Rect(
                    j * CELL_SIZE,
                    i * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )

                pygame.draw.rect(
                    self.screen,
                    BLACK,
                    rect,
                    1
                )

                cell = grid[i][j]

                if cell == OBSTACLE:

                    pygame.draw.rect(
                        self.screen,
                        GRAY,
                        rect
                    )

                elif cell == FIRE:

                    pygame.draw.rect(
                        self.screen,
                        RED,
                        rect
                    )

                elif cell == EXIT:

                    pygame.draw.rect(
                        self.screen,
                        GREEN,
                        rect
                    )

        # Draw agents
        for agent in agents:

            if not agent.alive:
                continue

            x, y = agent.position

            center = (
                y * CELL_SIZE + CELL_SIZE // 2,
                x * CELL_SIZE + CELL_SIZE // 2
            )

            color = BLUE

            if agent.evacuated:
                color = YELLOW

            pygame.draw.circle(
                self.screen,
                color,
                center,
                CELL_SIZE // 3
            )

        pygame.display.flip()