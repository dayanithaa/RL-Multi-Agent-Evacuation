class Agent:

    def __init__(self, agent_id, position):

        self.id = agent_id
        self.position = position

        self.alive = True
        self.evacuated = False

    def move(self, action, grid_size):

        if not self.alive or self.evacuated:
            return self.position

        x, y = self.position

        if action == 0:      # UP
            x -= 1

        elif action == 1:    # DOWN
            x += 1

        elif action == 2:    # LEFT
            y -= 1

        elif action == 3:    # RIGHT
            y += 1

        elif action == 4:    # WAIT
            pass

        x = max(0, min(grid_size - 1, x))
        y = max(0, min(grid_size - 1, y))

        return (x, y)