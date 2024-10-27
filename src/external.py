import config
from src.world.Grid import Grid

grid = Grid(config.WIDTH, config.HEIGHT)
pop = [None]
kill_queue = []
move_queue = []
