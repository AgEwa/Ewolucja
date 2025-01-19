from math import ceil

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
        # TODO: obsługa błędu jeśli populacja jest większa iż ilość pustych miejsc na gridzie (raczej później w programie, bo też dla loaded pop)
        self.population_size = QSpinBox()
        self.population_size.setMinimum(0)
        self.population_size.setMaximum(1000)
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
        self.num_inner_neurons.setMinimum(1)
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
        self.max_energy.setMinimum(10)
        self.max_energy.setMaximum(100)
        self.max_energy.setValue(Settings.settings.max_energy_level_supremum)

        # input responsible for changing starting energy level
        self.start_energy = QSpinBox()
        self.start_energy.setMinimum(5)
        self.max_energy.valueChanged.connect(lambda x: self.start_energy.setMaximum(x))
        self.start_energy.setMaximum(Settings.settings.max_energy_level_supremum)
        self.start_energy.setValue(Settings.settings.entry_max_energy_level)

        # input responsible for min food per source
        self.min_food = QSpinBox()
        self.min_food.setMinimum(1)
        self.min_food.setMaximum(100)
        self.min_food.setValue(Settings.settings.min_food_per_source)

        # input responsible for max food per source
        self.max_food = QSpinBox()
        self.max_food.setMinimum(1)
        self.max_food.setMaximum(100)
        self.max_food.setValue(Settings.settings.max_food_per_source)
        # update limits per change
        self.min_food.valueChanged.connect(lambda x: self.max_food.setMinimum(x))
        self.max_food.valueChanged.connect(lambda x: self.min_food.setMaximum(x))

        # input responsible for food_added_energy
        self.food_added_energy = QDoubleSpinBox()
        self.food_added_energy.setMinimum(1)
        self.food_added_energy.setMaximum(10)
        self.food_added_energy.setSingleStep(0.5)
        self.food_added_energy.setValue(Settings.settings.food_added_energy)

        # input responsible for energy_per_move
        self.energy_per_move = QDoubleSpinBox()
        self.energy_per_move.setMinimum(0.01)
        self.food_added_energy.valueChanged.connect(lambda x: self.energy_per_move.setMaximum(x))
        self.energy_per_move.setMaximum(10)
        self.energy_per_move.setSingleStep(0.1)
        self.energy_per_move.setValue(Settings.settings.energy_per_move)

        # input responsible for changing grid dimension
        self.grid_dim = QSpinBox()
        self.grid_dim.setMinimum(10)
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
        self.enable_kill = QCheckBox()
        self.enable_kill.setChecked(Settings.settings.enable_kill)

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
        self._container.setFixedSize(ceil(config.WINDOW_WIDTH * 1.1), ceil(config.WINDOW_HEIGHT * 1.1))

        return

    def set_up_parameters(self):
        parameters_layout = QGridLayout()

        # title row 0
        sim_title = '<span style="color:#6c9286; font-size: 15px;"><b>Population</b></span>'
        parameters_layout.addWidget(QLabel(sim_title), 0, 0, 1, 7)

        # spaces
        parameters_layout.addWidget(QFrame(width=5), 1, 2)
        parameters_layout.addWidget(QFrame(width=5), 1, 5)

        # row 1
        parameters_layout.addWidget(QLabel('Population size:'), 1, 0)
        parameters_layout.addWidget(self.population_size, 1, 1)

        parameters_layout.addWidget(QLabel('Number of generations:'), 1, 3)
        parameters_layout.addWidget(self.num_generations, 1, 4)

        parameters_layout.addWidget(QLabel('Number of steps per generation:'), 1, 6)
        parameters_layout.addWidget(self.num_steps, 1, 7)

        # title row 2
        gen_title = '<span style="color:#6c9286; font-size: 15px;"><b>Genome</b></span>'
        parameters_layout.addWidget(QLabel(gen_title), 2, 0, 1, 7)
        # row 3
        parameters_layout.addWidget(QLabel('Genome length:'), 3, 0)
        parameters_layout.addWidget(self.genome_length, 3, 1)

        parameters_layout.addWidget(QLabel('Number of inner neurons:'), 3, 3)
        parameters_layout.addWidget(self.num_inner_neurons, 3, 4)

        parameters_layout.addWidget(QLabel('Disable pheromones:'), 3, 6)
        parameters_layout.addWidget(self.disable_pheromones, 3, 7)
        # row 4
        parameters_layout.addWidget(QLabel('Enable kill action:'), 4, 0)
        parameters_layout.addWidget(self.enable_kill, 4, 1)

        # title row 5
        mut_title = '<span style="color:#6c9286; font-size: 15px;"><b>Mutation</b></span>'
        parameters_layout.addWidget(QLabel(mut_title), 5, 0, 1, 7)
        # row 6
        parameters_layout.addWidget(QLabel('Mutation probability:'), 6, 0)
        parameters_layout.addWidget(self.prob_mutation, 6, 1)

        parameters_layout.addWidget(QLabel('Number of genes to be mutated:'), 6, 3)
        parameters_layout.addWidget(self.mutatable_genes_num, 6, 4)

        parameters_layout.addWidget(QLabel('Number of bits in gene to be mutated:'), 6, 6)
        parameters_layout.addWidget(self.mutatable_bits_num, 6, 7)

        # title row 7
        en_title = '<span style="color:#6c9286; font-size: 15px;"><b>Energy</b></span>'
        parameters_layout.addWidget(QLabel(en_title), 7, 0, 1, 7)
        # row 8
        parameters_layout.addWidget(QLabel('Starting energy level:'), 8, 0)
        parameters_layout.addWidget(self.start_energy, 8, 1)

        parameters_layout.addWidget(QLabel('Supremum energy level:'), 8, 3)
        parameters_layout.addWidget(self.max_energy, 8, 4)

        parameters_layout.addWidget(QLabel('Energy per food:'), 8, 6)
        parameters_layout.addWidget(self.food_added_energy, 8, 7)
        # row 9
        parameters_layout.addWidget(QLabel('Energy per unit of move:'), 9, 0)
        parameters_layout.addWidget(self.energy_per_move, 9, 1)

        # title row 10
        w_title = '<span style="color:#6c9286; font-size: 15px;"><b>World</b></span>'
        parameters_layout.addWidget(QLabel(w_title), 10, 0, 1, 7)
        # row 11
        parameters_layout.addWidget(QLabel('Grid dimension:'), 11, 0)
        parameters_layout.addWidget(self.grid_dim, 11, 1)

        parameters_layout.addWidget(QLabel('Range of food amount per source:'), 11, 3)
        parameters_layout.addWidget(self.min_food, 11, 4)
        parameters_layout.addWidget(self.max_food, 11, 5)

        # title row 12
        save_title = '<span style="color:#6c9286; font-size: 15px;"><b>Data Capture</b></span>'
        parameters_layout.addWidget(QLabel(save_title), 12, 0, 1, 7)
        # row 13
        parameters_layout.addWidget(QLabel('Save animation:'), 13, 0)
        parameters_layout.addWidget(self.save_animation, 13, 1)

        parameters_layout.addWidget(QLabel('Save evolution step:'), 13, 3)
        parameters_layout.addWidget(self.save_evolution_step, 13, 4)

        parameters_layout.addWidget(QLabel('Save generation:'), 13, 6)
        parameters_layout.addWidget(self.save_generation, 13, 7)

        # row 14
        parameters_layout.addWidget(QLabel('Save selection:'), 14, 0)
        parameters_layout.addWidget(self.save_selection, 14, 1)

        parameters_layout.addWidget(QLabel('Save population:'), 14, 3)
        parameters_layout.addWidget(self.save_population, 14, 4)

        parameters_layout.addWidget(QLabel('Save config:'), 14, 6)
        parameters_layout.addWidget(self.save_config, 14, 7)

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
        Settings.settings.enable_kill = self.enable_kill.isChecked()
        Settings.settings.SAVE_CONFIG = self.save_config.isChecked()
        Settings.settings.food_added_energy = self.food_added_energy.value()
        Settings.settings.energy_per_move = self.energy_per_move.value()
        Settings.settings.min_food_per_source = self.min_food.value()
        Settings.settings.max_food_per_source = self.max_food.value()

        Settings.write()

        self.close()

        return

    def reject(self):
        self.close()

        return
