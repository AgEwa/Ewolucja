import logging
import pickle
import random
import time

import numpy as np

import config
from src.evolution.Simulation import simulation
from src.external import grid, population
from src.population.Specimen import Specimen
from src.saves.PlaneSave import PlaneSave
from src.saves.Settings import Settings
from src.utils.utils import initialize_genome
from src.world.Grid import Grid
from src.world.LocationTypes import Coord


def initialize_simulation(map_save: PlaneSave = None, uid=None, population_filepath: str = None):
    # this function called as process, so settings needs to be read
    Settings.read()
    grid.reload_size()

    if map_save:
        assert (grid.data == Grid.EMPTY).all()
        assert not grid.food_data
        barriers = map_save.get_barrier_positions()
        if barriers:            # so it doesn't fail if there are no barriers/foods marked
            grid.set_barriers_at_indexes(barriers)
        foods = map_save.get_food_positions()
        if foods:
            grid.set_food_sources_at_indexes(foods)
    else:
        initialize_random_world()

    if population_filepath and population_filepath != "":
        load_existing_population(population_filepath)
    else:
        initialize_random_population()
    start = time.time()
    simulation(uid)
    logging.info(f"Simulation took {time.time() - start}s.")

    return


def load_existing_population(population_filepath):
    try:
        with open(population_filepath, "rb") as file:
            pop = pickle.load(file)
        assert isinstance(pop, list)
        assert len(pop) > 1
        assert pop[0] is None
        initials = np.argwhere(grid.data == Grid.EMPTY)
        # randomly select sufficient amount of spaces for population
        selected = initials[np.random.choice(initials.shape[0], size=len(pop) - 1, replace=False)]
        population.clear()
        population.append(None)
        for idx in range(len(pop) - 1):
            assert isinstance(pop[idx + 1], Specimen)
            population.append(pop[idx + 1].reset(Coord(selected[idx, 0].item(), selected[idx, 1].item())))
            grid.data[selected[idx][0], selected[idx][1]] = idx + 1

        Settings.settings.population_size = len(population) - 1
        Settings.settings.genome_length = len(population[1].genome)

    except Exception as e:
        print(e)
        initialize_random_population()


def initialize_random_world():
    """
    Initializes the world by modifying global grid to place barriers and food sources.
    """
    # assert that grid is empty
    assert (grid.data == Grid.EMPTY).all()
    assert not grid.food_data
    # list of all indexes available in the grid
    all_places = [(row, col) for row in range(grid.size) for col in range(grid.size)]
    # select indexes for barriers and update grid object
    bar_placement = random.sample(all_places, config.BARRIERS_NUMBER)
    grid.set_barriers_at_indexes(bar_placement)
    # list of available indexes left
    places_left = list(set(all_places).difference(bar_placement))
    # select indexes for food sources and update grid object
    food_placement = random.sample(places_left, config.FOOD_SOURCES_NUMBER)
    grid.set_food_sources_at_indexes(food_placement)

    return


def initialize_random_population() -> None:
    """
    Initializes population with randomly placed specimen across the grid
    """
    population.clear()
    population.append(None)
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
