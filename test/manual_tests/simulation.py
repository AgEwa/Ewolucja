import os
import random
import uuid

import imageio.v2 as imageio
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import config
from src.external import grid, population, move_queue, kill_set
from src.population.NeuralNetwork import NeuralNetwork
from src.population.Specimen import Specimen
from src.saves.Settings import Settings
from src.utils.utils import initialize_genome, drain_move_queue, drain_kill_queue, probability
from src.world.Grid import Grid
from src.world.LocationTypes import Coord


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
    ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labeltop=False, labelright=False, labelleft=False)

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
    """ initializes population with randomly placed specimen across the grid """

    # look for empty spaces
    initials = np.argwhere(grid.data == Grid.EMPTY)
    # randomly select sufficient amount of spaces for population
    selected = initials[np.random.choice(initials.shape[0], size=config.POPULATION_SIZE, replace=False)]

    for i in range(config.POPULATION_SIZE):
        # create specimen and add it to population. Save its index (in population list), location (in grid) and
        # randomly generated genome
        population.append(Specimen(i + 1, Coord(
            selected[i, 0].item(), selected[i, 1].item()), initialize_genome(config.GENOME_LENGTH)))
        # place index (reference to population list) on grid
        grid.data[selected[i][0], selected[i][1]] = i + 1

    return


def new_generation_initialize(p_genomes: list) -> None:
    """ initializes population from given genomes and randomly places them across the grid """

    grid.reset()
    population.clear()
    population.append(None)

    # look for empty spaces
    initials = np.argwhere(grid.data == Grid.EMPTY)
    # randomly select sufficient amount of spaces for population
    selected = initials[np.random.choice(initials.shape[0], size=config.POPULATION_SIZE, replace=False)]

    for i in range(config.POPULATION_SIZE):
        # create specimen and add it to population. Save its index (in population list), location (in grid) and
        # randomly generated genome
        population.append(Specimen(i + 1, Coord(selected[i, 0].item(), selected[i, 1].item()), p_genomes[i][1:]))
        # place index (reference to population list) on grid
        grid.data[selected[i][0], selected[i][1]] = i + 1
        # set max energy
        population[i + 1].max_energy = p_genomes[i][0]
        population[i + 1].energy = population[i + 1].max_energy

    return


def mutate(p_specimen: Specimen) -> None:
    """ makes given specimen mutate """
    genome = p_specimen.genome.copy()

    # select random genes from genome
    selected_idx = random.sample(range(len(genome)), config.MUTATE_N_GENES)
    selected = [genome[x] for x in range(len(genome)) if x in selected_idx]

    genome = [genome[x] for x in range(len(genome)) if x not in selected_idx]

    # mutate selected genes
    for i in range(len(selected)):
        # convert to binary
        # for every hexadecimal character in gene, convert it to integer and then format is as 4-bit binary number
        # then join groups and convert string to list for further easier negation of bits
        # (str[i] = 'something' yields error but list[i] = 'something' does not)
        binary = list(''.join(['{0:04b}'.format(int(d, 16)) for d in selected[i]]))
        # negate specified number of neighbouring bits
        # find index from which bits will be negated
        # since randint includes boundaries, we do from 0 to len - 1
        # but also considering how many bits we want to negate we subtract that number from the end
        idx = random.randint(0, len(binary) - config.MUTATE_N_BITS)
        for b in range(idx, idx + config.MUTATE_N_BITS):
            binary[b] = '0' if binary[b] == '1' else '1'
        # convert it back to hex
        selected[i] = '{:08x}'.format(int(''.join(binary), 2))

    # update genome
    assert all(len(gene) == 8 for gene in selected)
    genome = genome + selected
    assert len(genome) == config.GENOME_LENGTH
    p_specimen.genome = genome
    p_specimen.brain = NeuralNetwork(genome, p_specimen)

    return


def crossover_get_genomes(p_parent_a: Specimen, p_parent_b: Specimen) -> tuple[list, list]:
    # how many genes from parent_a will go to child_a
    # at least one up to GENOME_LENGTH - 1
    a_2_a_size = np.random.choice(range(1, config.GENOME_LENGTH))
    # how many genes from parent_b will go to child_a
    # compatible to GENOME_LENGTH
    b_2_a_size = config.GENOME_LENGTH - a_2_a_size

    # parent_a's genes for child_a indexes
    a_2_a_genes_idx = np.random.choice(config.GENOME_LENGTH, size=a_2_a_size, replace=False)
    # parent_b's genes for child_a indexes
    b_2_a_genes_idx = np.random.choice(config.GENOME_LENGTH, size=b_2_a_size, replace=False)

    # parent_a's genes for child_a
    a_2_a_genes = [p_parent_a.genome[gene_idx] for gene_idx in range(config.GENOME_LENGTH) if
                   gene_idx in a_2_a_genes_idx]
    # parent_a's genes for child_b
    a_2_b_genes = [p_parent_a.genome[gene_idx] for gene_idx in range(config.GENOME_LENGTH) if
                   gene_idx not in a_2_a_genes_idx]
    # parent_b's genes for child_a
    b_2_a_genes = [p_parent_b.genome[gene_idx] for gene_idx in range(config.GENOME_LENGTH) if
                   gene_idx in b_2_a_genes_idx]
    # parent_b's genes for child_b
    b_2_b_genes = [p_parent_b.genome[gene_idx] for gene_idx in range(config.GENOME_LENGTH) if
                   gene_idx not in b_2_a_genes_idx]

    key = probability(0.5)
    child_a_max_energy_value = p_parent_a.max_energy if key else p_parent_b.max_energy
    child_b_max_energy_value = p_parent_a.max_energy if not key else p_parent_b.max_energy

    child_a_genome = a_2_a_genes + b_2_a_genes
    child_b_genome = a_2_b_genes + b_2_b_genes
    assert len(child_a_genome) == config.GENOME_LENGTH
    assert len(child_b_genome) == config.GENOME_LENGTH

    child_a_genome = [child_a_max_energy_value] + child_a_genome
    child_b_genome = [child_b_max_energy_value] + child_b_genome

    return child_a_genome, child_b_genome


def simulation() -> None:
    """ main simulation function """

    # name of folder to store frames
    folder_name = 'frames'
    # unique ID for current simulation
    uid = uuid.uuid4()

    # names of frames
    filenames = []

    # population of specimens
    initialize_world()
    initialize_population()

    # simulation loop
    for generation in range(config.NUMBER_OF_GENERATIONS):
        # add population state frame before actions
        if config.SAVE_ANIMATION:
            filenames.append(make_plot(grid.data, folder_name, f'gif_{uid}_gen_{generation}_frame_0'))

        # every generation
        for step in range(config.STEPS_PER_GENERATION):
            # has some time (in form of steps) to do something

            # movement/evolution
            # for every specimen
            for specimen_idx in range(1, config.POPULATION_SIZE + 1):
                # if it is alive
                if population[specimen_idx].alive and population[specimen_idx].energy > 0:
                    # mutation
                    if probability(config.MUTATION_PROBABILITY):
                        mutate(population[specimen_idx])

                    # let it take some actions
                    population[specimen_idx].live()

            # execute kill actions
            drain_kill_queue(kill_set)
            # execute move actions
            drain_move_queue(move_queue)

            # add population state frame after one generation actions
            if config.SAVE_ANIMATION:
                filenames.append(make_plot(grid.data, folder_name, f'gif_{uid}_gen_{generation}_frame_{step + 1}'))

        # initiate storage for energy
        current_energy = np.zeros(config.POPULATION_SIZE)
        maximum_energy = np.zeros(config.POPULATION_SIZE)
        # fill with values
        for specimen_idx in range(1, config.POPULATION_SIZE + 1):
            current_energy[specimen_idx - 1] = population[specimen_idx].energy
            maximum_energy[specimen_idx - 1] = population[specimen_idx].max_energy

        # selection
        # calculate weighted average
        adaptation_function_value = current_energy * 0.25 + maximum_energy * 0.75
        # calculate values for sigmoid function
        # multiply by 0 for those with 0 current energy, so their probability of selection is 0
        pre_sigmoid = np.exp(adaptation_function_value) * np.where(current_energy == 0, 0, 1)
        # calculate probabilities
        probabilities = pre_sigmoid / np.sum(pre_sigmoid)
        # acquire random indexes according to probabilities calculated step above
        selected_idx = np.random.choice(range(1, config.POPULATION_SIZE + 1), size=Settings.settings.SELECT_N_SPECIMENS, replace=False, p=probabilities)

        pre_sigmoid = np.exp(adaptation_function_value[selected_idx - 1])
        probabilities = pre_sigmoid / np.sum(pre_sigmoid)
        genomes_for_new_population = []
        # every two parents give two children, and we want to have population of POPULATION_SIZE size
        # so there should be POPULATION_SIZE / 2 pairs of children and such POPULATION_SIZE / 2 crossovers
        # add + 1 extra pair if POPULATION_SIZE is odd
        for _ in range(int(config.POPULATION_SIZE / 2) + 1):
            # randomly select two parents
            parent_a_idx, parent_b_idx = np.random.choice(selected_idx, size=2, replace=False, p=probabilities)
            # cross them and get their children's genomes
            child_a_genome, child_b_genome = crossover_get_genomes(population[parent_a_idx], population[parent_b_idx])
            # add genomes to evaluate them next
            genomes_for_new_population.append(child_a_genome)
            genomes_for_new_population.append(child_b_genome)

        # compose frames into animation
        if config.SAVE_ANIMATION:
            to_gif(os.path.join(folder_name, f'gif_{uid}_gen_{generation}'), filenames)
            for filename in filenames:
                os.remove(filename)
            filenames.clear()

        new_generation_initialize(genomes_for_new_population)
