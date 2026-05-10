import pygame
import torch
import numpy as np

from environment.grid_world import GridWorld

from renderer.pygame_renderer import Renderer

from dqn.model import DQN

from config import *


DEVICE = torch.device(
    "cuda" if torch.cuda.is_available()
    else "cpu"
)

STATE_DIM = 9
ACTION_DIM = 5


model = DQN(
    STATE_DIM,
    ACTION_DIM
).to(DEVICE)

model.load_state_dict(
    torch.load(
        "multi_agent_dqn.pth",
        map_location=DEVICE
    )
)

model.eval()


def select_action(state):

    state = torch.FloatTensor(state)\
        .unsqueeze(0)\
        .to(DEVICE)

    with torch.no_grad():

        q_values = model(state)

    return q_values.argmax().item()


env = GridWorld()

renderer = Renderer(GRID_SIZE)

clock = pygame.time.Clock()

states = env.reset()

done = False

running = True


while running and not done:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

    actions = []

    for state in states:

        action = select_action(state)

        actions.append(action)

    next_states, rewards, done = \
        env.step(actions)

    renderer.draw(
        env.grid,
        env.agents
    )

    states = next_states

    clock.tick(FPS)

pygame.quit()