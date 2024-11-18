import numpy as np

import config
from src.LocationTypes import Coord
from src.external import grid, move_queue, kill_queue, population
from src.population.Specimen import Specimen
from src.utils.utils import initialize_genome, drain_move_queue, drain_kill_queue
from src.world.Grid import Grid


def initialize():
    initials = np.argwhere(np.isin(grid.data, Grid.EMPTY))
    selected = initials[np.random.choice(initials.shape[0], size=config.POPULATION_SIZE, replace=False)]

    for i in range(config.POPULATION_SIZE):
        population.append(Specimen(i + 1, Coord(selected[i, 0].item(), selected[i, 1].item()),
                                   initialize_genome(config.GENOME_LENGTH)))
        grid.data[selected[i][0], selected[i][1]] = i + 1


def one_step(p_specimen, step):
    p_specimen.age += 1
    actions = p_specimen.think(step)
    p_specimen.act(actions)


def simulation(population):
    for generation in range(config.NUMBER_OF_GENERATIONS):
        print(f'GENERATION {generation}')
        print(grid.data)

        # every generation
        for step in range(config.STEPS_PER_GENERATION):
            # has some time (in form of steps) to do something
            print(f'STEP {step}')

            for specimen_idx in range(1, config.POPULATION_SIZE + 1):
                if population[specimen_idx].alive:
                    one_step(population[specimen_idx], step)

            drain_kill_queue(kill_queue)
            drain_move_queue(move_queue)

            print(grid.data)

        print()


def main():
    initialize()
    simulation(population)

    return


if __name__ == '__main__':
    main()
