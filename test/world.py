import numpy as np

import config
from src.external import grid, move_queue, kill_queue
from src.population.Specimen import Specimen
from src.utils import random_genome, drain_move_queue, drain_kill_queue
from src.world.Grid import Grid


def initialize():
    initials = np.argwhere(grid.data == Grid.EMPTY)
    selected = initials[np.random.choice(initials.shape[0], size=config.POPULATION_SIZE, replace=False)]
    population = [None]

    for i in range(config.POPULATION_SIZE):
        population.append(Specimen(i + 1, selected[i], random_genome(config.GENOME_LENGTH)))
        grid.data[selected[i][0], selected[i][1]] = i + 1

    return population


def one_step(p_specimen, step):
    p_specimen.age += 1
    actions = p_specimen.think(step)
    p_specimen.act(actions)


def simulation(population):
    for generation in range(config.NUMBER_OF_GENERATIONS):
        for step in range(config.STEPS_PER_GENERATION):
            for specimen_idx in range(1, config.POPULATION_SIZE + 1):
                if population[specimen_idx].alive:
                    one_step(population[specimen_idx], step)

            drain_kill_queue(kill_queue)
            drain_move_queue(move_queue)


def main():
    population = initialize()

    simulation(population)

    return


if __name__ == '__main__':
    main()
