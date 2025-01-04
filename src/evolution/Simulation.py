import time
import uuid
from multiprocessing import Process

from src.evolution.Operators import *
from src.external import move_queue, kill_set, grid
from src.population.Specimen import Specimen
from src.utils.Plot import *
from src.utils.Save import SavingHelper
from src.utils.utils import drain_move_queue, drain_kill_set, probability
from src.world.Grid import Grid
from src.world.LocationTypes import Coord

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(process)d - %(levelname)s: %(message)s (%(filename)s:%(lineno)d)', datefmt='%Y-%m-%d %H:%M:%S')


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
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    # unique ID for current simulation
    uid = uuid.uuid4()
    logging.info(f"Simulation id: {uid}")
    # names of frames
    filenames = []
    # process' lists to join
    plot_processes = []
    gif_processes = []
    # population of specimens
    # initialize_world()
    # initialize_population()

    if config.SAVE:
        save_helper = SavingHelper(uid)
        save_helper.start_writers()

    # simulation loop
    for generation in range(config.NUMBER_OF_GENERATIONS):
        logging.info(f"Gen {generation} started.")
        gen_start = time.time()
        # add population state frame before actions
        if config.SAVE_ANIMATION:
            save_path_name = os.path.join(folder_name, f'gif_{uid}_gen_{generation}_frame_0.png')
            p = Process(target=plot_world, args=(
            grid.barriers.copy(), grid.food_data.copy(), population.copy(), save_path_name))
            p.start()
            plot_processes.append(p)
            filenames.append(save_path_name)
        # every generation
        for step in range(config.STEPS_PER_GENERATION):
            # has some time (in form of steps) to do something

            count_dead = population_step()
            if count_dead == config.POPULATION_SIZE:
                break

            # execute kill actions
            drain_kill_set(kill_set)
            # execute move actions
            drain_move_queue(move_queue)
            # spread pheromones
            grid.pheromones.spread()

            # add population state frame after one generation actions
            if config.SAVE_ANIMATION:
                save_path_name = os.path.join(folder_name, f'gif_{uid}_gen_{generation}_frame_{step + 1}.png')
                p = Process(target=plot_world, args=(
                grid.barriers.copy(), grid.food_data.copy(), population.copy(), save_path_name))
                p.start()
                plot_processes.append(p)
                filenames.append(save_path_name)

            if config.SAVE_EVOLUTION_STEP:
                save_helper.save_step(generation, step, count_dead)

        probabilities, selected_idx = evaluate_and_select()
        genomes_for_new_population = reproduce(probabilities, selected_idx)

        if config.SAVE_SELECTION:
            save_helper.save_selection(generation, selected_idx)

        if config.SAVE_GENERATION:
            save_helper.save_gen(generation)

        wait_start = time.time()
        for p in plot_processes:
            p.join()
        logging.info(f"Waited {time.time() - wait_start}s for plot processes.")
        plot_processes.clear()
        # compose frames into animation
        if config.SAVE_ANIMATION:
            p = Process(target=to_gif, args=(
            os.path.join(folder_name, f'gif_{uid}_gen_{generation}'), filenames.copy()))
            p.start()
            gif_processes.append(p)

        filenames.clear()

        new_generation_initialize(genomes_for_new_population)
        logging.info(f"Gen {generation} took {time.time() - gen_start}s.")

    if config.SAVE_POPULATION:
        save_helper.save_pop()

    if config.SAVE_CONFIG:
        save_helper.save_config()

    if config.SAVE_GRID:
        save_helper.save_grid()

    wait_start = time.time()
    for p in gif_processes:
        p.join()
    logging.info(f"Waited {time.time() - wait_start}s for gif processes.")
    if config.SAVE:
        save_helper.close_writers()


def population_step() -> int:
    count_dead = 0
    for specimen_idx in range(1, config.POPULATION_SIZE + 1):
        # if it is alive
        if population[specimen_idx].alive:
            # mutation
            if probability(config.MUTATION_PROBABILITY):
                mutate(population[specimen_idx])

            # let it take some actions
            population[specimen_idx].live()
        else:
            count_dead += 1
    return count_dead
