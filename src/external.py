import config
from src.world.Grid import Grid

grid = Grid(config.WIDTH, config.HEIGHT)

# index 0 is reserved, as indexes in population list will be placed on grid at their positions so to reference
# them. Index 0 means empty space
population = [None]

kill_set = set()

move_queue = []
