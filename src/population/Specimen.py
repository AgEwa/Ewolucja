import math

import numpy as np

import config
from src.external import grid, move_queue
from src.population.NeuralNetwork import NeuralNetwork
from src.population.SensorActionEnums import ActionType
from src.types import Direction, Conversions, Coord
from src.utils import squeeze, response_curve, probability


class Specimen:
    def __init__(self, index, loc, genome):
        self.alive = True
        self.index = index
        self.location = loc
        self.birth_location = loc
        self.age = 0
        self.genome = genome
        self.brain = NeuralNetwork(genome)
        self.responsiveness = 0.5
        self.osc_period = 34
        self.long_probe_dist = config.LONG_PROBE_DISTANCE
        self.last_movement_direction = Direction.random()
        self.challenge_bits = False

        return

    def think(self, step):
        """ returns dict of ActionType key : float value """

        return self.brain.run(step)

    def act(self, actions):
        if ActionType.SET_RESPONSIVENESS in actions:
            level = actions[ActionType.SET_RESPONSIVENESS]
            level = squeeze(level)
            self.responsiveness = level

        responsiveness_adj = response_curve(self.responsiveness)

        # really don't know what logic is behind this, adapted from source
        if ActionType.SET_OSCILLATOR_PERIOD in actions:
            period = actions[ActionType.SET_OSCILLATOR_PERIOD]
            period = squeeze(period)
            period = 1 + int(1.5 + math.exp(7 * period))

            if 2 <= period <= 2048:
                self.osc_period = period

        if ActionType.SET_LONGPROBE_DIST in actions:
            max_long_probe_dist = 32
            level = actions[ActionType.SET_LONGPROBE_DIST]
            level = squeeze(level)
            level = 1 + level * max_long_probe_dist
            self.long_probe_dist = int(level)

        if ActionType.EMIT_PHEROMONE in actions:
            emit_threshold = 0.5

            level = actions[ActionType.EMIT_PHEROMONE]
            level = squeeze(level)
            level *= responsiveness_adj

            if level > emit_threshold and probability(level):
                # implement pheromones

                pass

        if ActionType.KILL in actions and config.KILL_ENABLED:
            kill_threshold = 0.5

            level = actions[ActionType.KILL]
            level = squeeze(level)
            level *= responsiveness_adj

            if level > kill_threshold and probability(level):
                # implement kill

                pass

        # specimen's last movement as x and y direction
        last_move_offset = Conversions.direction_as_normalized_coord(self.last_movement_direction)
        # retrieve x movement
        move_x = 0 if ActionType.MOVE_X not in actions else actions[ActionType.MOVE_X]
        # retrieve y movement
        move_y = 0 if ActionType.MOVE_Y not in actions else actions[ActionType.MOVE_Y]
        # retrieve east movement
        move_x += 0 if ActionType.MOVE_EAST not in actions else actions[ActionType.MOVE_EAST]
        # retrieve west movement
        move_x -= 0 if ActionType.MOVE_WEST not in actions else actions[ActionType.MOVE_WEST]
        # retrieve north movement
        move_y += 0 if ActionType.MOVE_NORTH not in actions else actions[ActionType.MOVE_NORTH]
        # retrieve south movement
        move_y -= 0 if ActionType.MOVE_SOUTH not in actions else actions[ActionType.MOVE_SOUTH]

        # continue last direction movement
        if ActionType.MOVE_FORWARD in actions:
            level = actions[ActionType.MOVE_FORWARD]

            move_x += last_move_offset.x * level
            move_y += last_move_offset.y * level

        # turn around of last direction movement
        if ActionType.MOVE_REVERSE in actions:
            level = actions[ActionType.MOVE_REVERSE]

            move_x -= last_move_offset.x * level
            move_y -= last_move_offset.y * level

        # turn left respective to last direction movement
        if ActionType.MOVE_LEFT in actions:
            level = actions[ActionType.MOVE_LEFT]

            offset = Conversions.direction_as_normalized_coord(self.last_movement_direction.rotate_90_deg_ccw())

            move_x += offset.x * level
            move_y += offset.y * level

        # turn right respective to last direction movement
        if ActionType.MOVE_RIGHT in actions:
            level = actions[ActionType.MOVE_RIGHT]

            offset = Conversions.direction_as_normalized_coord(self.last_movement_direction.rotate_90_deg_cw())

            move_x += offset.x * level
            move_y += offset.y * level

        # move at random direction
        if ActionType.MOVE_RANDOM in actions:
            level = actions[ActionType.MOVE_RANDOM]

            offset = Conversions.direction_as_normalized_coord(Direction.random())

            move_x += offset.x * level
            move_y += offset.y * level

        # squeeze total x movement into [-1; 1]
        move_x = np.tanh(move_x)
        # squeeze total y movement into [-1; 1]
        move_y = np.tanh(move_y)
        # apply adjusted responsiveness
        move_x *= responsiveness_adj
        move_y *= responsiveness_adj
        #
        prob_x = int(probability(abs(move_x)))
        prob_y = int(probability(abs(move_y)))

        sign_x = -1 if move_x < 0 else 1
        sign_y = -1 if move_y < 0 else 1

        offset = Coord(sign_x * prob_x, sign_y * prob_y)

        new_location = self.location + offset

        if grid.in_bounds(new_location) and grid.is_empty_at(new_location):
            move_queue.append((self, new_location))

    def __str__(self):
        return f'{self.location} {self.genome}'

    def __repr__(self):
        return f'{self.location} {self.genome}'
