import random

import numpy as np

import config
from src.evolution.Simulation import simulation
from src.external import grid, population
from src.population.Specimen import Specimen
from src.saves.MapSave import MapSave
from src.saves.Settings import Settings
from src.utils.utils import initialize_genome
from src.world.Grid import Grid
from src.world.LocationTypes import Coord


def initialize_simulation(map_save: MapSave = None, uid=None):
    # this function called as process, so settings needs to be read
    Settings.read()

    if map_save:
        assert (grid.data == Grid.EMPTY).all()
        assert not grid.food_data

        grid.set_barriers_at_indexes(map_save.get_barrier_positions())
        grid.set_food_sources_at_indexes(map_save.get_food_positions())
    else:
        initialize_world()

    initialize_population()

    simulation(uid)

    return


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

    return


def initialize_population() -> None:
    """
    Initializes population with randomly placed specimen across the grid
    """

    # look for empty spaces
    initials = np.argwhere(grid.data == Grid.EMPTY)
    # randomly select sufficient amount of spaces for population
    selected = initials[np.random.choice(initials.shape[0], size=Settings.settings.population_size, replace=False)]

    for i in range(Settings.settings.population_size):
        # create specimen and add it to population. Save its index (in population list), location (in grid) and
        # randomly generated genome
        population.append(Specimen(i + 1, Coord(
            selected[i, 0].item(), selected[i, 1].item()), initialize_genome(Settings.settings.genome_length)))
        # place index (reference to population list) on grid
        grid.data[selected[i][0], selected[i][1]] = i + 1

    return
