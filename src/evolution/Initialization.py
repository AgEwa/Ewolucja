import logging
import random
import time
from multiprocessing import freeze_support, set_start_method

import numpy as np

import config
from saves.Settings import Settings
from src.evolution.Simulation import simulation
from src.external import grid, population
from src.population.Specimen import Specimen
from src.saves.MapSave import MapSave
from src.utils.utils import initialize_genome
from src.world.Grid import Grid
from src.world.LocationTypes import Coord


def initialize_simulation(map_save: MapSave = None):
    settings = Settings.read()
    settings.update_configs()
    if map_save:
        assert (grid.data == Grid.EMPTY).all()
        assert not grid.food_data

        grid.set_barriers_at_indexes(map_save.get_barrier_positions())
        grid.set_food_sources_at_indexes(map_save.get_food_positions())
    else:
        initialize_world()
    initialize_population()
    simulation()


def initialize_world():
    """
    Initializes the world by modifying global grid to place barriers and food sources.
    """
    # assert that grid is empty
    assert (grid.data == Grid.EMPTY).all()
    assert not grid.food_data
    # list of all indexes available in the grid
    all_places = [(row, col) for row in range(grid.height) for col in range(grid.width)]
    # select indexes for barriers and update grid object
    bar_placement = random.sample(all_places, config.BARRIERS_NUMBER)
    grid.set_barriers_at_indexes(bar_placement)
    # list of available indexes left
    places_left = list(set(all_places).difference(bar_placement))
    # select indexes for food sources and update grid object
    food_placement = random.sample(places_left, config.FOOD_SOURCES_NUMBER)
    grid.set_food_sources_at_indexes(food_placement)


def initialize_population() -> None:
    """
    Initializes population with randomly placed specimen across the grid
    """

    # look for empty spaces
    initials = np.argwhere(grid.data == Grid.EMPTY)
    # randomly select sufficient amount of spaces for population
    selected = initials[np.random.choice(initials.shape[0], size=config.POPULATION_SIZE, replace=False)]

    for i in range(config.POPULATION_SIZE):
        # create specimen and add it to population. Save its index (in population list), location (in grid) and
        # randomly generated genome
        population.append(Specimen(i + 1, Coord(selected[i, 0].item(), selected[i, 1].item()),
                                   initialize_genome(config.GENOME_LENGTH)))
        # place index (reference to population list) on grid
        grid.data[selected[i][0], selected[i][1]] = i + 1

    return


def main():
    """ starting point of application """
    start = time.time()
    initialize_simulation()
    logging.info(f"Simulation took {time.time() - start}s.")

    return


if __name__ == '__main__':
    # add support for freezing for Windows, otherwise no effect
    freeze_support()
    set_start_method('spawn')
    main()
