import random

import config
from src.external import move_queue, grid, kill_set
from src.population.NeuralNetwork import NeuralNetwork
from src.population.SensorActionEnums import ActionType
from src.utils.Plot import visualize_neural_network
from src.utils.utils import squeeze, response_curve, probability
from src.world.LocationTypes import Direction, Conversions, Coord

max_long_probe_dist = 32


def get_max_energy_level_from_genome(hex_gene: str) -> int:
    return int(hex_gene, 16) % config.MAX_ENERGY_LEVEL_SUPREMUM


move_actions = {
    ActionType.MOVE_X,
    ActionType.MOVE_Y,
    ActionType.MOVE_EAST,
    ActionType.MOVE_WEST,
    ActionType.MOVE_NORTH,
    ActionType.MOVE_SOUTH,
    ActionType.MOVE_FORWARD,
    ActionType.MOVE_REVERSE,
    ActionType.MOVE_LEFT,
    ActionType.MOVE_RIGHT,
    ActionType.MOVE_RANDOM
}


class Specimen:
    def __init__(self, p_index: int, p_birth_location: Coord, p_genome: list):
        self.alive = True
        self.index = p_index
        self.birth_location = p_birth_location
        self.location = self.birth_location
        self.age = 0
        self.responsiveness = 0.5
        self.responsiveness_adj = response_curve(self.responsiveness)
        self.oscillator = None
        self.long_probe_dist = config.LONG_PROBE_DISTANCE
        # Direction object with compass field
        self.last_movement_direction = Direction.random()
        # Coord object with x/y values of movement in that direction
        self.last_movement = Coord(0, 0)
        self.max_energy = config.ENTRY_MAX_ENERGY_LEVEL
        self.energy = self.max_energy  # or always start with ENTRY_MAX_ENERGY_LEVEL or other set value
        self.genome = p_genome
        self.brain = NeuralNetwork(p_genome, self)

        return

    def can_move(self):
        return self.energy >= config.ENERGY_PER_ONE_UNIT_OF_MOVE

    def use_energy(self, value: float):
        self.energy -= value

        if self.energy < min(config.ENERGY_PER_ONE_UNIT_OF_MOVE, config.ENERGY_DECREASE_IN_TIME):
            self.energy = 0
            self.alive = False

    def eat(self):
        # try to increase max energy level
        if self.max_energy < config.MAX_ENERGY_LEVEL_SUPREMUM:
            self.max_energy += config.FOOD_INCREASED_MAX_LEVEL
        # update energy
        self.energy += config.FOOD_ADDED_ENERGY
        # if it ate more than allowed, then trim
        if self.energy > self.max_energy:
            self.energy = self.max_energy

    def live(self):
        """ age the specimen and simulate living"""
        self.age += 1
        self.use_energy(config.ENERGY_DECREASE_IN_TIME)

        if not self.alive:
            return

        actions = self.think()
        self.act(actions)

    def think(self) -> dict[ActionType, float]:
        """ returns dict of ActionType key : float value """

        return self.brain.run()

    def act(self, p_actions: dict[ActionType, float]) -> None:
        """ acts based on passed actions and their activation level values """

        p_move = {k: p_actions.pop(k) for k in list(p_actions) if k in move_actions}

        self._execute_actions(p_actions)

        self._move(p_move)

    def _execute_actions(self, p_actions):
        """Executes non-move actions"""
        for key, value in p_actions.items():
            method_name = f"_{key.name.lower()}"
            method = getattr(self, method_name, None)
            if method:
                method(value)

    def _set_responsiveness(self, value):
        self.responsiveness = squeeze(value)
        self.responsiveness_adj = response_curve(self.responsiveness)  # Myślę że można przerobić żeby symulować starzenie się (mniejsza responsywność z czasem)

    def _set_oscillator_period(self, value):
        if not self.oscillator:
            return  # no osc sensor
        period = squeeze(value)

        if 0.016 <= period:
            self.oscillator.set_frequency(1 / period)

    def _set_longprobe_dist(self, value):
        level = squeeze(value)
        level = 1 + level * max_long_probe_dist
        self.long_probe_dist = int(level)

    def _emit_pheromone(self, value):
        emit_threshold = 0.1
        level = squeeze(value)
        level *= self.responsiveness_adj

        if level > emit_threshold and probability(level) or config.FORCE_EMISSION_TEST:
            grid.pheromones.emit(self.location.x, self.location.y, self.last_movement_direction)

    def _kill(self, value):
        kill_threshold = 0.5

        level = squeeze(value)
        level *= self.responsiveness_adj

        if level > kill_threshold and probability(level):
            for x in range(self.location.x - 1, self.location.x + 2):
                for y in range(self.location.y - 1, self.location.y + 2):
                    if x == self.location.x and y == self.location.y:
                        continue
                    if grid.in_bounds_xy(x, y) and grid.is_occupied_at_xy(x, y):
                        specimen_idx = grid.at_xy(x, y)
                        kill_set.add(specimen_idx)

    def _move(self, p_move):
        """Accumulates movements from `p_move` into a path and queues the movement"""
        if self.energy < config.ENERGY_PER_ONE_UNIT_OF_MOVE:
            return

        # specimen's last movement as x and y direction
        last_move_offset = Conversions.direction_as_normalized_coord(self.last_movement_direction)
        path = []

        for key, value in p_move.items():
            method_name = f"_{key.name.lower()}"
            method = getattr(self, method_name, None)
            if probability(squeeze(value)) and method:
                step = method(last_move_offset)
                if isinstance(step, Coord):
                    path.append(step)

        # if there are any steps
        if path:
            # add movement to movement queue
            move_queue.append((self, path))

    @staticmethod
    def _move_x(_):
        return Coord(random.choice([1, -1]), 0)

    @staticmethod
    def _move_y(_):
        return Coord(0, random.choice([1, -1]))

    @staticmethod
    def _move_east(_):
        return Coord(1, 0)

    @staticmethod
    def _move_west(_):
        return Coord(-1, 0)

    @staticmethod
    def _move_north(_):
        return Coord(0, 1)

    @staticmethod
    def _move_south(_):
        return Coord(0, -1)

    @staticmethod
    def _move_forward(offset: Coord):
        return offset

    @staticmethod
    def _move_reverse(offset: Coord):
        return Conversions.direction_as_normalized_coord(Conversions.coord_as_direction(offset).rotate_180_deg())

    @staticmethod
    def _move_left(offset: Coord):
        return Conversions.direction_as_normalized_coord(Conversions.coord_as_direction(offset).rotate_90_deg_ccw())

    @staticmethod
    def _move_right(offset: Coord):
        return Conversions.direction_as_normalized_coord(Conversions.coord_as_direction(offset).rotate_90_deg_cw())

    @staticmethod
    def _move_random(_):
        return Conversions.direction_as_normalized_coord(Direction.random())

    def plot_brain_graph(self):
        visualize_neural_network(self.brain.layers.to_graph())

    def __str__(self):
        return f'{self.location} {self.genome}'

    def __repr__(self):
        return self.__str__()
