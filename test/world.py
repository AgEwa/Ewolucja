import numpy as np

import config
from src.population.Specimen import Specimen
from src.world.Grid import Grid
from utils.utils import random_genome


def main():
    grid = Grid(config.WIDTH, config.HEIGHT)

    initials = np.argwhere(grid.data == Grid.EMPTY)
    selected = initials[np.random.choice(initials.shape[0], size=config.POPULATION_SIZE, replace=False)]
    population = [None]

    for i in range(config.POPULATION_SIZE):
        population.append(Specimen(i + 1, selected[i], random_genome(config.GENOME_LENGTH)))
        grid.data[selected[i][0], selected[i][1]] = i + 1

    print(grid.data)
    print(population)

    return


if __name__ == '__main__':
    main()
