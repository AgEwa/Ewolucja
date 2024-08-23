import os
import uuid

import imageio.v2 as imageio
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import config
from src.external import grid, move_queue, kill_queue
from src.population.Specimen import Specimen
from src.types import Coord
from src.utils.utils import random_genome, drain_move_queue, drain_kill_queue
from src.world.Grid import Grid


def make_plot(p_matrix: np.array, p_folder_name: str, p_plot_name: str) -> str:
    """ creates color map of passed matrix and saves it in specified folder with specified name """

    assert isinstance(p_matrix, np.ndarray)
    assert isinstance(p_folder_name, str)
    assert isinstance(p_plot_name, str)

    if not os.path.exists(p_folder_name):
        os.mkdir(p_folder_name)

    field_to_color = np.rot90(np.ma.masked_where(p_matrix == 0, p_matrix), 1)

    fig, ax = plt.subplots()
    cmap = mpl.colormaps['gray']
    cmap.set_bad(color='white')
    ax.matshow(field_to_color, interpolation=None, cmap=cmap)
    ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labeltop=False, labelright=False,
                   labelleft=False)

    name = os.path.join(p_folder_name, f'{p_plot_name}.png')

    plt.savefig(name)
    plt.close()

    return name


def to_gif(p_target_name: str, p_filenames: list[str]) -> None:
    """ composes pictures of specified filenames into one animated .gif file """

    assert isinstance(p_target_name, str)
    assert isinstance(p_filenames, list)
    for filename in p_filenames:
        assert isinstance(filename, str)

    with imageio.get_writer(f'{p_target_name}.gif', mode='I') as writer:
        for filename in p_filenames:
            image = imageio.imread(filename)
            writer.append_data(image)

    return


def initialize() -> list[Specimen]:
    """ initializes population with randomly placed specimen across the grid """

    # look for empty spaces
    initials = np.argwhere(grid.data == Grid.EMPTY)
    # randomly select sufficient amount of spaces for population
    selected = initials[np.random.choice(initials.shape[0], size=config.POPULATION_SIZE, replace=False)]
    # index 0 is reserved, as indexes in population list will be placed on grid at their positions so to reference
    # them. Index 0 means empty space
    population = [None]

    for i in range(config.POPULATION_SIZE):
        # create specimen and add it to population. Save its index (in population list), location (in grid) and
        # randomly generated genome
        population.append(Specimen(i + 1, Coord(selected[i, 0].item(), selected[i, 1].item()), random_genome(config.GENOME_LENGTH)))
        # place index (reference to population list) on grid
        grid.data[selected[i][0], selected[i][1]] = i + 1

    # return created population
    return population


def one_step(p_specimen: Specimen, p_step: int) -> None:
    """ supports single simulation step for specified specimen """

    assert isinstance(p_specimen, Specimen)
    assert isinstance(p_step, int) and p_step >= 0

    # make specimen older by one unit
    p_specimen.age += 1
    # retrieve actions specimen would execute
    actions = p_specimen.think(p_step)
    # evaluate previously retrieved actions
    p_specimen.act(actions)

    return


def simulation() -> None:
    """ main simulation function """

    # name of folder to store frames
    folder_name = 'frames'
    # unique ID for current simulation
    uid = uuid.uuid4()

    # names of frames
    filenames = []

    # population of specimens
    population = initialize()

    # simulation loop
    for generation in range(config.NUMBER_OF_GENERATIONS):
        # if it is the next generation
        if generation != 0:
            # TODO: recreate population based on currently alive specimens
            pass

        # add population state frame before actions
        filenames.append(make_plot(grid.data, folder_name, f'gif_{uid}_gen_{generation}_frame_0'))

        # every generation
        for step in range(config.STEPS_PER_GENERATION):
            # has some time (in form of steps) to do something

            # for every specimen
            for specimen_idx in range(1, config.POPULATION_SIZE + 1):
                # if it is alive
                if population[specimen_idx].alive:
                    # let it take some actions
                    one_step(population[specimen_idx], step)

            # execute kill actions
            drain_kill_queue(kill_queue)
            # execute move actions
            drain_move_queue(move_queue)

            # add population state frame after one generation actions
            filenames.append(make_plot(grid.data, folder_name, f'gif_{uid}_gen_{generation}_frame_{step + 1}'))

    # compose frames into animation
    to_gif(os.path.join(folder_name, f'gif_{uid}'), filenames)


def main():
    """ starting point of application """
    simulation()

    return


if __name__ == '__main__':
    main()
