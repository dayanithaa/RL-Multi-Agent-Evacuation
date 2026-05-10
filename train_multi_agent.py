import random
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim

from environment.grid_world import GridWorld

from dqn.model import DQN
from dqn.replay_buffer import ReplayBuffer

from config import *


DEVICE = torch.device(
    "cuda" if torch.cuda.is_available()
    else "cpu"
)

STATE_DIM = 9

ACTION_DIM = 5


policy_net = DQN(
    STATE_DIM,
    ACTION_DIM
).to(DEVICE)

target_net = DQN(
    STATE_DIM,
    ACTION_DIM
).to(DEVICE)

target_net.load_state_dict(
    policy_net.state_dict()
)

optimizer = optim.Adam(
    policy_net.parameters(),
    lr=LR
)

criterion = nn.MSELoss()

memory = ReplayBuffer(MEMORY_SIZE)


def select_action(state, epsilon):

    if random.random() < epsilon:

        return random.randint(0, ACTION_DIM - 1)

    state = torch.FloatTensor(state)\
        .unsqueeze(0)\
        .to(DEVICE)

    with torch.no_grad():

        q_values = policy_net(state)

    return q_values.argmax().item()


def train_step():

    if len(memory) < BATCH_SIZE:
        return

    states, actions, rewards, \
    next_states, dones = \
        memory.sample(BATCH_SIZE)

    states = torch.FloatTensor(states).to(DEVICE)

    actions = torch.LongTensor(actions)\
        .unsqueeze(1).to(DEVICE)

    rewards = torch.FloatTensor(rewards)\
        .to(DEVICE)

    next_states = torch.FloatTensor(
        next_states
    ).to(DEVICE)

    dones = torch.FloatTensor(dones)\
        .to(DEVICE)

    current_q = policy_net(states)\
        .gather(1, actions)\
        .squeeze(1)

    with torch.no_grad():

        next_q = target_net(next_states)\
            .max(1)[0]

        target_q = rewards + \
            GAMMA * next_q * (1 - dones)

    loss = criterion(
        current_q,
        target_q
    )

    optimizer.zero_grad()

    loss.backward()

    optimizer.step()


epsilon = EPSILON_START

for episode in range(EPISODES):

    env = GridWorld()

    states = env.reset()

    done = False

    total_reward = 0

    while not done:

        actions = []

        for state in states:

            action = select_action(
                state,
                epsilon
            )

            actions.append(action)

        next_states, rewards, done = \
            env.step(actions)

        for i in range(NUM_AGENTS):

            memory.push(
                states[i],
                actions[i],
                rewards[i],
                next_states[i],
                done
            )

        train_step()

        states = next_states

        total_reward += sum(rewards)

    epsilon = max(
        EPSILON_MIN,
        epsilon * EPSILON_DECAY
    )

    if episode % TARGET_UPDATE == 0:

        target_net.load_state_dict(
            policy_net.state_dict()
        )

    print(
        f"Episode {episode} | "
        f"Reward: {total_reward:.2f} | "
        f"Epsilon: {epsilon:.3f}"
    )

torch.save(
    policy_net.state_dict(),
    "multi_agent_dqn.pth"
)

print("Training Complete")