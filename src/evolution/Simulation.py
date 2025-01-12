import time
from multiprocessing import Process

from src.evolution.Operators import *
from src.external import move_queue, kill_set, grid
from src.population.Specimen import Specimen
from src.utils.Plot import *
from src.utils.Save import SavingHelper, save_stats
from src.utils.utils import drain_move_queue, drain_kill_set, probability
from src.world.Grid import Grid
from src.world.LocationTypes import Coord

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(process)d - %(levelname)s: %(message)s (%(filename)s:%(lineno)d)',
                    datefmt='%Y-%m-%d %H:%M:%S')


def new_generation_initialize(p_genomes: list) -> None:
    """ initializes new population from given genomes and randomly places them across the grid """

    grid.reset()
    population.clear()
    population.append(None)
    killers_count = 0

    # look for empty spaces
    initials = np.argwhere(grid.data == Grid.EMPTY)
    # randomly select sufficient amount of spaces for population
    selected = initials[np.random.choice(initials.shape[0], size=Settings.settings.population_size, replace=False)]

    for i in range(Settings.settings.population_size):
        # create specimen and add it to population. Save its index (in population list), location (in grid) and
        # randomly generated genome
        population.append(Specimen(i + 1, Coord(selected[i, 0].item(), selected[i, 1].item()), p_genomes[i][1:]))
        killers_count += 1 if population[-1].is_killer else 0
        # place index (reference to population list) on grid
        grid.data[selected[i][0], selected[i][1]] = i + 1
        # set max energy
        population[i + 1].max_energy = p_genomes[i][0]
        population[i + 1].energy = population[i + 1].max_energy

    return killers_count


def simulation(uid) -> None:
    """ main simulation function """

    # path to saves for current simulation
    sim_folder_path = os.path.join(config.SIMULATION_SAVES_FOLDER_PATH, f'{uid}')
    # create saves directory for current simulation
    if not os.path.exists(sim_folder_path):
        os.mkdir(sim_folder_path)
    # path to saved frames of generations of current simulation
    sim_frames_folder_path = os.path.join(sim_folder_path, 'animation')
    # create directory for frames of generations of current simulation
    if not os.path.exists(sim_frames_folder_path):
        os.mkdir(sim_frames_folder_path)

    # unique ID for current simulation
    logging.info(f"Simulation id: {uid}")
    # names of frames
    filenames = []
    # process' lists to join
    plot_processes = []
    gif_processes = []
    # population of specimens
    # initialize_world()
    # initialize_population()

    if Settings.settings.SAVE:
        save_helper = SavingHelper(uid)
        save_helper.start_writers()

    killers_count = 0
    for specimen in population[1:]:
        killers_count += 1 if specimen.is_killer else 0

    # simulation loop
    for generation in range(Settings.settings.number_of_generations):
        logging.info(f"Gen {generation} started.")
        gen_start = time.time()
        # add population state frame before actions
        if Settings.settings.SAVE_ANIMATION:
            save_path_name = os.path.join(sim_frames_folder_path, f'generation_{generation}_frame_0.png')
            p = Process(target=plot_world, args=(
                grid.barriers.copy(), grid.food_data.copy(), population.copy(), save_path_name))
            p.start()
            plot_processes.append(p)
            filenames.append(save_path_name)
        # every generation
        for step in range(Settings.settings.steps_per_generation):
            # has some time (in form of steps) to do something

            count_dead = population_step()
            if count_dead == Settings.settings.population_size:
                break

            # execute kill actions
            drain_kill_set(kill_set)
            # execute move actions
            drain_move_queue(move_queue)
            # spread pheromones
            grid.pheromones.spread()

            # add population state frame after one generation actions
            if Settings.settings.SAVE_ANIMATION:
                save_path_name = os.path.join(sim_frames_folder_path, f'generation_{generation}_frame_{step + 1}.png')
                p = Process(target=plot_world, args=(
                    grid.barriers.copy(), grid.food_data.copy(), population.copy(), save_path_name))
                p.start()
                plot_processes.append(p)
                filenames.append(save_path_name)

            if Settings.settings.SAVE_EVOLUTION_STEP:
                save_helper.save_step(generation, step, count_dead)

        probabilities, selected_idx = evaluate_and_select()
        genomes_for_new_population = reproduce(probabilities, selected_idx)

        # save survivred, selected and with kill neuron
        survived = Settings.settings.population_size - count_dead
        selected = len(selected_idx)
        save_stats(uid, generation, survived, selected, killers_count)

        if Settings.settings.SAVE_SELECTION:
            save_helper.save_selection(generation, selected_idx)

        if Settings.settings.SAVE_GENERATION:
            save_helper.save_gen(generation)

        wait_start = time.time()
        for p in plot_processes:
            p.join()
        logging.info(f"Waited {time.time() - wait_start}s for plot processes.")
        plot_processes.clear()
        # compose frames into animation
        if Settings.settings.SAVE_ANIMATION:
            p = Process(target=to_gif, args=(
                os.path.join(sim_frames_folder_path, f'generation_{generation}'), filenames.copy()))
            p.start()
            gif_processes.append(p)

        filenames.clear()

        killers_count = new_generation_initialize(genomes_for_new_population)
        logging.info(f"Gen {generation} took {time.time() - gen_start}s.")

    if Settings.settings.SAVE_POPULATION:
        save_helper.save_pop()

    if Settings.settings.SAVE_CONFIG:
        save_helper.save_config()

    wait_start = time.time()
    for p in gif_processes:
        p.join()
    logging.info(f"Waited {time.time() - wait_start}s for gif processes.")
    if Settings.settings.SAVE:
        save_helper.close_writers()

    return


def population_step() -> int:
    count_dead = 0
    for specimen_idx in range(1, Settings.settings.population_size + 1):
        # if it is alive
        if population[specimen_idx].alive:
            # mutation
            if probability(Settings.settings.mutation_probability):
                mutate(population[specimen_idx])

            # let it take some actions
            population[specimen_idx].live()
        else:
            count_dead += 1
    return count_dead
