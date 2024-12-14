import random

import numpy as np

import config
from population.NeuralNetwork import NeuralNetwork
from src.external import population
from src.population.Specimen import Specimen
from src.utils.utils import probability


def mutate(p_specimen: Specimen) -> None:
    """ makes given specimen mutate """
    if len(p_specimen.genome) != config.GENOME_LENGTH:
        assert len(p_specimen.genome) == config.GENOME_LENGTH

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
        idx = random.randint(0, len(binary) - 1 - config.MUTATE_N_BITS)
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
    a_2_a_size = np.random.choice(range(config.GENOME_LENGTH - 1))
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


def reproduce(probabilities, selected_idx):
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
    return genomes_for_new_population


def evaluate_and_select_2():
    # initiate storage for energy
    current_energy = np.zeros(config.POPULATION_SIZE)
    maximum_energy = np.zeros(config.POPULATION_SIZE)
    # fill with values
    for i in range(config.POPULATION_SIZE):
        current_energy[i] = population[i + 1].energy
        maximum_energy[i] = population[i + 1].max_energy
    # selection
    # calculate weighted average
    adaptation_function_value = current_energy * 0.25 + maximum_energy * 0.75
    # calculate values for sigmoid function
    # multiply by 0 for those with 0 current energy, so their probability of selection is 0
    pre_sigmoid = np.exp(adaptation_function_value) * np.where(current_energy == 0, 0, 1)
    # calculate probabilities
    probabilities = pre_sigmoid / np.sum(pre_sigmoid)
    # acquire random indexes according to probabilities calculated step above
    selected_idx = np.random.choice(range(1, config.POPULATION_SIZE + 1), size=config.SELECT_N_SPECIMENS,
                                    replace=False,
                                    p=probabilities)
    pre_sigmoid = np.exp(adaptation_function_value[selected_idx - 1])
    print(adaptation_function_value[selected_idx - 1])
    probabilities = pre_sigmoid / np.sum(pre_sigmoid)
    return probabilities, selected_idx


def evaluate_and_select():
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
    selected_idx = select_best(adaptation_function_value, current_energy)
    pre_sigmoid = np.exp(adaptation_function_value[selected_idx])
    print(adaptation_function_value[selected_idx])
    probabilities = pre_sigmoid / np.sum(pre_sigmoid)
    return probabilities, selected_idx + 1


def select_best(adaptation_values: list, energy: list):
    non_zero = np.argwhere(energy).flatten()
    if len(non_zero) < config.SELECT_N_SPECIMENS:
        missing = config.SELECT_N_SPECIMENS - len(non_zero)
        print(missing, " missing in selection")
        return np.concatenate((non_zero, np.argsort(adaptation_values)[-missing:]))

    values = adaptation_values.copy()
    values = np.array(values * np.where(energy == 0, 0, 1))
    threshold = 0.67 * np.mean(values[np.argsort(values)[-3:]])
    selected_idx = np.argwhere(values > threshold).flatten()

    if len(selected_idx) < config.SELECT_N_SPECIMENS:
        threshold = values[np.argsort(values)[-config.SELECT_N_SPECIMENS]]
        selected_idx = np.argwhere(adaptation_values >= threshold).flatten()

    return selected_idx
