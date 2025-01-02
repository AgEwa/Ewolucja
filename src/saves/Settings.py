import json
from dataclasses import dataclass, field

import config


@dataclass
# describes settings file
class Settings:
    grid_dim: int = config.DIM
    genome_length: int = config.GENOME_LENGTH
    num_inner_neurons: int = config.MAX_NUMBER_OF_INNER_NEURONS
    start_energy: int = config.ENTRY_MAX_ENERGY_LEVEL
    max_energy: int = config.MAX_ENERGY_LEVEL_SUPREMUM
    population_size: int = config.POPULATION_SIZE
    num_generations: int = config.NUMBER_OF_GENERATIONS
    num_steps: int = config.STEPS_PER_GENERATION
    prob_mutation: float = config.MUTATION_PROBABILITY
    mutatable_genes_num: int = config.MUTATE_N_GENES
    mutatable_bits_num: int = config.MUTATE_N_BITS
    disable_pheromones: bool = False
    elements_to_save: list = field(default_factory=list)

    def to_json(self) -> str:
        """ converts Settings object to json representation """

        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(p_json: str) -> 'Settings':
        """ based on json representation creates Settings object """

        assert isinstance(p_json, str)

        return Settings(**(json.loads(p_json)))

    @staticmethod
    def read() -> None:
        """ reads current value of Settings and stores as static class field """

        try:
            with open(config.SETTINGS_PATH, 'r') as f:
                Settings.settings = Settings.from_json(f.read())
        except Exception as e:
            print(e)
