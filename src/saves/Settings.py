import json
import importlib
from dataclasses import dataclass, field
from typing import ClassVar

import config
from config_src import simulation_settings


@dataclass
# describes settings file
class Settings:
    population_size: int = config.POPULATION_SIZE
    number_of_generations: int = config.NUMBER_OF_GENERATIONS
    steps_per_generation: int = config.STEPS_PER_GENERATION

    mutation_probability: float = config.MUTATION_PROBABILITY
    mutate_n_genes: int = config.MUTATE_N_GENES
    mutate_n_bits: int = config.MUTATE_N_BITS

    genome_length: int = config.GENOME_LENGTH
    max_number_of_inner_neurons: int = config.MAX_NUMBER_OF_INNER_NEURONS
    disable_pheromones: bool = config.DISABLE_PHEROMONES

    entry_max_energy_level: int = config.ENTRY_MAX_ENERGY_LEVEL
    max_energy_level_supremum: int = config.MAX_ENERGY_LEVEL_SUPREMUM
    dim: int = config.DIM

    elements_to_save: list = field(default_factory=list)

    settings: ClassVar['Settings'] = None

    def to_json(self) -> str:
        """ converts Settings object to json representation """

        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(p_json: str) -> 'Settings':
        """ based on json representation creates Settings object """

        assert isinstance(p_json, str)

        return Settings(**(json.loads(p_json)))

    @staticmethod
    def read():
        """ reads current value of Settings and stores as static class field """

        try:
            with open(config.SETTINGS_PATH, 'r') as f:
                Settings.settings = Settings.from_json(f.read())
        except Exception as e:
            print(e)

        return Settings.settings

    @staticmethod
    def write() -> None:
        """  """

        with open(config.SETTINGS_PATH, 'w') as f:
            f.write(Settings.settings.to_json())

        return

    def update_configs(self):
        for key, value in self.__dict__.items():
            if key not in ["elements_to_save"]:
                setattr(simulation_settings, key.upper(), value)

        # TODO: obsługa "elements_to_save" jak będą w UI obecne

        importlib.reload(config)
