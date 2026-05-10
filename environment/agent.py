class Agent:

    def __init__(self, agent_id, position):

        self.id = agent_id

        self.position = position

        self.alive = True

        self.evacuated = False

    def move(self, action, grid_size):

        x, y = self.position

        if action == 0:
            x -= 1

        elif action == 1:
            x += 1

        elif action == 2:
            y -= 1

        elif action == 3:
            y += 1

        elif action == 4:
            pass

        x = max(0, min(grid_size - 1, x))
        y = max(0, min(grid_size - 1, y))

        return (x, y)