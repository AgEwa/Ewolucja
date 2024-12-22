import time
import uuid
from multiprocessing import Process, set_start_method

from src.LocationTypes import Coord
from src.evolution.Operators import *
from src.external import move_queue, kill_queue, grid
from src.population.Specimen import Specimen
from src.utils.Plot import *
from src.utils.utils import initialize_genome, drain_move_queue, drain_kill_queue, probability
from src.world.Grid import Grid


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


def new_generation_initialize(p_genomes: list) -> None:
    """ initializes new population from given genomes and randomly places them across the grid """

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


def simulation() -> None:
    """ main simulation function """

    # name of folder to store frames
    folder_name = 'frames'
    # unique ID for current simulation
    uid = uuid.uuid4()

    # names of frames
    filenames = []
    plot_processes = []
    gif_processes = []
    # population of specimens
    initialize_world()
    initialize_population()

    # simulation loop
    for generation in range(config.NUMBER_OF_GENERATIONS):
        logging.info(f"Gen {generation} started.")
        gen_start = time.time()
        # add population state frame before actions
        if config.SAVE_ANIMATION:
            save_path_name = os.path.join(folder_name, f'gif_{uid}_gen_{generation}_frame_0.png')
            p = Process(target=plot_world,
                        args=(grid.barriers.copy(), grid.food_data.copy(), population.copy(), save_path_name))
            p.start()
            plot_processes.append(p)
            filenames.append(save_path_name)
        # every generation
        for step in range(config.STEPS_PER_GENERATION):
            # has some time (in form of steps) to do something

            # movement/evolution
            # for every specimen
            for specimen_idx in range(1, config.POPULATION_SIZE + 1):
                # if it is alive
                if population[specimen_idx].alive:
                    # mutation
                    if probability(config.MUTATION_PROBABILITY):
                        mutate(population[specimen_idx])

                    # let it take some actions
                    population[specimen_idx].live()

            # execute kill actions
            drain_kill_queue(kill_queue)
            # execute move actions
            drain_move_queue(move_queue)
            # spread pheromones
            grid.pheromones.spread()

            # add population state frame after one generation actions
            if config.SAVE_ANIMATION:
                save_path_name = os.path.join(folder_name, f'gif_{uid}_gen_{generation}_frame_{step + 1}.png')
                p = Process(target=plot_world,
                            args=(grid.barriers.copy(), grid.food_data.copy(), population.copy(), save_path_name))
                p.start()
                plot_processes.append(p)
                filenames.append(save_path_name)

        probabilities, selected_idx = evaluate_and_select()
        genomes_for_new_population = reproduce(probabilities, selected_idx)
        wait_start = time.time()
        for p in plot_processes:
            p.join()
        logging.info(f"Waited {time.time() - wait_start}s for plot processes.")
        plot_processes.clear()
        # compose frames into animation
        if config.SAVE_ANIMATION:
            p = Process(target=to_gif,
                        args=(os.path.join(folder_name, f'gif_{uid}_gen_{generation}'), filenames.copy()))
            p.start()
            gif_processes.append(p)

        filenames.clear()

        new_generation_initialize(genomes_for_new_population)
        logging.info(f"Gen {generation} took {time.time() - gen_start}s.")

    wait_start = time.time()
    for p in gif_processes:
        p.join()
    logging.info(f"Waited {time.time() - wait_start}s for gif processes.")


def main():
    """ starting point of application """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    start = time.time()
    simulation()
    logging.info(f"Simulation took {time.time() - start}s.")

    return


if __name__ == '__main__':
    set_start_method('spawn')
    main()
