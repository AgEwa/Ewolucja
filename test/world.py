import numpy as np

import config
from src.population.Specimen import Specimen
from src.utils import random_genome
from src.world.Grid import Grid


def initialize():
    grid = Grid(config.WIDTH, config.HEIGHT)

    initials = np.argwhere(grid.data == Grid.EMPTY)
    selected = initials[np.random.choice(initials.shape[0], size=config.POPULATION_SIZE, replace=False)]
    population = [None]

    for i in range(config.POPULATION_SIZE):
        population.append(Specimen(i + 1, selected[i], random_genome(config.GENOME_LENGTH)))
        grid.data[selected[i][0], selected[i][1]] = i + 1

    return grid, population


def simulation(grid, population):
    for generation in range(config.NUMBER_OF_GENERATIONS):
        for step in range(config.STEPS_PER_GENERATION):
            for specimen_idx in range(1, config.POPULATION_SIZE + 1):
                if population[specimen_idx].alive:
                    population[specimen_idx].age += 1
                    actions = population[specimen_idx].think(step)
                    population[specimen_idx].act(actions)


def main():
    # grid, population = initialize()

    # simulation(grid, population)

    x = {'a': 5, 'b': 6, 'c': 7}

    if 5 in x:
        print('a is in x')

    return


if __name__ == '__main__':
    main()
