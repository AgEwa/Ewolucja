from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QDialogButtonBox, QFrame, QGridLayout, QSpinBox, QLabel, \
    QDoubleSpinBox, QCheckBox

import config
from src.saves.Settings import Settings


class ParametersEditor(QMainWindow):
    def __init__(self):
        """ constructor """

        # use derived constructor
        super().__init__()

        # input responsible for changing population size
        self.population_size = QSpinBox()
        self.population_size.setMinimum(0)
        self.population_size.setMaximum(10000)
        self.population_size.setValue(Settings.settings.population_size)

        # input responsible for changing number of generations
        self.num_generations = QSpinBox()
        self.num_generations.setMinimum(0)
        self.num_generations.setMaximum(1000)
        self.num_generations.setValue(Settings.settings.number_of_generations)

        # input responsible for changing number of steps per generation
        self.num_steps = QSpinBox()
        self.num_steps.setMinimum(0)
        self.num_steps.setMaximum(1000)
        self.num_steps.setValue(Settings.settings.steps_per_generation)

        # input responsible for changing number of bits per gene to be mutated
        self.genome_length = QSpinBox()
        self.genome_length.setMinimum(0)
        self.genome_length.setMaximum(100)
        self.genome_length.setValue(Settings.settings.genome_length)

        # input responsible for changing number of inner neurons
        self.num_inner_neurons = QSpinBox()
        self.num_inner_neurons.setMinimum(0)
        self.num_inner_neurons.setMaximum(100)
        self.num_inner_neurons.setValue(Settings.settings.max_number_of_inner_neurons)

        # input responsible for disabling and enabling pheromones
        self.disable_pheromones = QCheckBox()
        self.disable_pheromones.setChecked(Settings.settings.disable_pheromones)

        # input responsible for changing mutation probability
        self.prob_mutation = QDoubleSpinBox()
        self.prob_mutation.setMinimum(0)
        self.prob_mutation.setMaximum(1)
        self.prob_mutation.setSingleStep(0.01)
        self.prob_mutation.setValue(Settings.settings.mutation_probability)

        # input responsible for changing number of genes to be mutated
        self.mutatable_genes_num = QSpinBox()
        self.mutatable_genes_num.setMinimum(0)
        self.genome_length.valueChanged.connect(lambda x: self.mutatable_genes_num.setMaximum(x))
        self.mutatable_genes_num.setMaximum(Settings.settings.genome_length)
        self.mutatable_genes_num.setValue(Settings.settings.mutate_n_genes)

        # input responsible for changing number of bits per gene to be mutated
        self.mutatable_bits_num = QSpinBox()
        self.mutatable_bits_num.setMinimum(0)
        # ToDo: ATTENTION! 32 bits maximum hardcoded. Maybe move to config?
        self.mutatable_bits_num.setMaximum(32)
        self.mutatable_bits_num.setValue(Settings.settings.mutate_n_bits)

        # input responsible for changing maximum achievable energy level
        self.max_energy = QSpinBox()
        self.max_energy.setMinimum(0)
        self.max_energy.setMaximum(100)
        self.max_energy.setValue(Settings.settings.max_energy_level_supremum)

        # input responsible for changing starting energy level
        self.start_energy = QSpinBox()
        self.start_energy.setMinimum(0)
        self.max_energy.valueChanged.connect(lambda x: self.start_energy.setMaximum(x))
        self.start_energy.setMaximum(Settings.settings.max_energy_level_supremum)
        self.start_energy.setValue(Settings.settings.entry_max_energy_level)

        # input responsible for changing grid dimension
        self.grid_dim = QSpinBox()
        self.grid_dim.setMinimum(0)
        self.grid_dim.setMaximum(100)
        self.grid_dim.setValue(Settings.settings.dim)

        # input responsible for disabling and enabling saving of animation
        self.save_animation = QCheckBox()
        self.save_animation.setChecked(Settings.settings.SAVE_ANIMATION)

        # input responsible for disabling and enabling saving of animation
        self.save_evolution_step = QCheckBox()
        self.save_evolution_step.setChecked(Settings.settings.SAVE_EVOLUTION_STEP)

        # input responsible for disabling and enabling saving of animation
        self.save_generation = QCheckBox()
        self.save_generation.setChecked(Settings.settings.SAVE_GENERATION)

        # input responsible for disabling and enabling saving of animation
        self.save_selection = QCheckBox()
        self.save_selection.setChecked(Settings.settings.SAVE_SELECTION)

        # input responsible for disabling and enabling saving of animation
        self.save_population = QCheckBox()
        self.save_population.setChecked(Settings.settings.SAVE_POPULATION)

        # input responsible for disabling and enabling saving of animation
        self.save_grid = QCheckBox()
        self.save_grid.setChecked(Settings.settings.SAVE_GRID)

        # input responsible for disabling and enabling saving of animation
        self.save_config = QCheckBox()
        self.save_config.setChecked(Settings.settings.SAVE_CONFIG)

        self._parameters = QFrame()
        self._container = QFrame(self)

        self.initialise()
        self.set_up_layout()

        self.setCentralWidget(self._container)

        return

    def initialise(self):
        self.setWindowTitle('Parameters editor')
        self._container.setFixedSize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        return

    def set_up_parameters(self):
        parameters_layout = QGridLayout()

        # spaces
        parameters_layout.addWidget(QFrame(width=30), 0, 2)
        parameters_layout.addWidget(QFrame(width=30), 0, 5)

        # row 0
        parameters_layout.addWidget(QLabel('Population size:'), 0, 0)
        parameters_layout.addWidget(self.population_size, 0, 1)

        parameters_layout.addWidget(QLabel('Number of generations:'), 0, 3)
        parameters_layout.addWidget(self.num_generations, 0, 4)

        parameters_layout.addWidget(QLabel('Number of steps per generation:'), 0, 6)
        parameters_layout.addWidget(self.num_steps, 0, 7)

        # row 1
        parameters_layout.addWidget(QLabel('Genome length:'), 1, 0)
        parameters_layout.addWidget(self.genome_length, 1, 1)

        parameters_layout.addWidget(QLabel('Number of inner neurons:'), 1, 3)
        parameters_layout.addWidget(self.num_inner_neurons, 1, 4)

        parameters_layout.addWidget(QLabel('Disable pheromones:'), 1, 6)
        parameters_layout.addWidget(self.disable_pheromones, 1, 7)

        # row 2
        parameters_layout.addWidget(QLabel('Mutation probability:'), 2, 0)
        parameters_layout.addWidget(self.prob_mutation, 2, 1)

        parameters_layout.addWidget(QLabel('Number of genes to be mutated:'), 2, 3)
        parameters_layout.addWidget(self.mutatable_genes_num, 2, 4)

        parameters_layout.addWidget(QLabel('Number of bits in gene to be mutated:'), 2, 6)
        parameters_layout.addWidget(self.mutatable_bits_num, 2, 7)

        # row 3
        parameters_layout.addWidget(QLabel('Starting energy level:'), 3, 0)
        parameters_layout.addWidget(self.start_energy, 3, 1)

        parameters_layout.addWidget(QLabel('Supremum energy level:'), 3, 3)
        parameters_layout.addWidget(self.max_energy, 3, 4)

        parameters_layout.addWidget(QLabel('Grid dimension:'), 3, 6)
        parameters_layout.addWidget(self.grid_dim, 3, 7)

        # row 4
        parameters_layout.addWidget(QLabel('Save animation:'), 4, 0)
        parameters_layout.addWidget(self.save_animation, 4, 1)

        parameters_layout.addWidget(QLabel('Save evolution step:'), 4, 3)
        parameters_layout.addWidget(self.save_evolution_step, 4, 4)

        parameters_layout.addWidget(QLabel('Save generation:'), 4, 6)
        parameters_layout.addWidget(self.save_generation, 4, 7)

        # row 5
        parameters_layout.addWidget(QLabel('Save selection:'), 5, 0)
        parameters_layout.addWidget(self.save_selection, 5, 1)

        parameters_layout.addWidget(QLabel('Save population:'), 5, 3)
        parameters_layout.addWidget(self.save_population, 5, 4)

        parameters_layout.addWidget(QLabel('Save grid:'), 5, 6)
        parameters_layout.addWidget(self.save_grid, 5, 7)

        # row 6
        parameters_layout.addWidget(QLabel('Save config:'), 6, 0)
        parameters_layout.addWidget(self.save_config, 6, 1)

        self._parameters.setLayout(parameters_layout)

        return

    def set_up_layout(self):
        self.set_up_parameters()

        # what submission buttons to use - save and cancel
        buttons = QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        # automatically create container for submission buttons
        submission_block = QDialogButtonBox(buttons)
        # connect method that should be triggered
        submission_block.accepted.connect(self.accept)
        # connect method that should be triggered
        submission_block.rejected.connect(self.reject)

        # create layout
        root_layout = QVBoxLayout()
        # add submission buttons
        root_layout.addWidget(self._parameters)
        # add submission buttons
        root_layout.addWidget(submission_block)

        self._container.setLayout(root_layout)

        return

    def accept(self):
        Settings.settings.population_size = self.population_size.value()
        Settings.settings.number_of_generations = self.num_generations.value()
        Settings.settings.steps_per_generation = self.num_steps.value()
        Settings.settings.mutation_probability = self.prob_mutation.value()
        Settings.settings.mutate_n_genes = self.mutatable_genes_num.value()
        Settings.settings.mutate_n_bits = self.mutatable_bits_num.value()
        Settings.settings.genome_length = self.genome_length.value()
        Settings.settings.max_number_of_inner_neurons = self.num_inner_neurons.value()
        Settings.settings.disable_pheromones = self.disable_pheromones.isChecked()
        Settings.settings.entry_max_energy_level = self.start_energy.value()
        Settings.settings.max_energy_level_supremum = self.max_energy.value()
        Settings.settings.dim = self.grid_dim.value()
        Settings.settings.SAVE_ANIMATION = self.save_animation.isChecked()
        Settings.settings.SAVE_EVOLUTION_STEP = self.save_evolution_step.isChecked()
        Settings.settings.SAVE_GENERATION = self.save_generation.isChecked()
        Settings.settings.SAVE_SELECTION = self.save_selection.isChecked()
        Settings.settings.SAVE_POPULATION = self.save_population.isChecked()
        Settings.settings.SAVE_GRID = self.save_grid.isChecked()
        Settings.settings.SAVE_CONFIG = self.save_config.isChecked()

        Settings.write()

        self.close()

        return

    def reject(self):
        self.close()

        return
