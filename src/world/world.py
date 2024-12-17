import random

import numpy as np

import config
from src.LocationTypes import Coord
from src.external import grid, move_queue, kill_queue, population
from src.population.Specimen import Specimen
from src.utils.utils import initialize_genome, drain_move_queue, drain_kill_queue
from src.world.Grid import Grid


def initialize_world():
    """
    Initializes the world by modifying global grid to place barriers and food sources.
    """
    all_places = [(row, col) for row in range(grid.height) for col in range(grid.width)]
    bar_placement = random.sample(all_places, config.BARRIERS_NUMBER)
    grid.set_barriers_at_indexes(bar_placement)
    places_left = list(set(all_places).difference(bar_placement))
    food_placement = random.sample(places_left, config.FOOD_SOURCES_NUMBER)
    grid.set_food_sources_at_indexes(food_placement)


def initialize_population():
    """
    Initializes the simulation by creating an initial population of specimens and placing them randomly on the empty
    grid locations.
    Side Effects:
        - Modifies global `grid.data` by placing the population in random empty spots.
        - Updates global `population` list with Specimen objects.
    """
    initials = np.argwhere(grid.data == Grid.EMPTY)
    selected = initials[np.random.choice(initials.shape[0], size=config.POPULATION_SIZE, replace=False)]

    for i in range(config.POPULATION_SIZE):
        population.append(Specimen(i + 1, Coord(selected[i, 0].item(), selected[i, 1].item()),
                                   initialize_genome(config.GENOME_LENGTH)))
        grid.data[selected[i][0], selected[i][1]] = i + 1

    return


def one_step(p_specimen, step):
    """Advances a specimen by one step in the simulation."""
    p_specimen.age += 1
    actions = p_specimen.think()
    p_specimen.act(actions)


def simulation():
    """
    Runs the simulation for a defined number of generations and steps.
    Side Effects:
        - Modifies global `grid.data`, `move_queue`, and `kill_queue`.
        - Calls the `one_step` function for each specimen.
    """
    for generation in range(config.NUMBER_OF_GENERATIONS):
        print(f'GENERATION {generation}')
        print(grid.data)
        print(grid.food_data)

        # every generation
        for step in range(config.STEPS_PER_GENERATION):
            # has some time (in form of steps) to do something
            print(f'STEP {step}')

            for specimen_idx in range(1, config.POPULATION_SIZE + 1):
                if population[specimen_idx].alive:
                    one_step(population[specimen_idx], step)

            drain_kill_queue(kill_queue)
            drain_move_queue(move_queue)
            #decreases and spreads after each step
            grid.pheromones.spread()

            print(grid.data)
            print(grid.food_data)
            print(grid.pheromones.grid)

        print()


def main():
    initialize_world()
    initialize_population()
    simulation()

    return


if __name__ == '__main__':
    main()
