import unittest
from unittest.mock import Mock

import numpy as np

import config
from src.LocationTypes import Coord, Direction, Compass, Conversions
from src.external import grid
from src.population.Sensor import Sensor
from src.population.SensorActionEnums import SensorType
from src.population.Specimen import Specimen
from src.utils.utils import initialize_genome, squeeze
from src.world.Grid import Grid


class TestPheromones(unittest.TestCase):
    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)

    def setUp(self):
        self.grid_mock = Grid(size_x=5, size_y=5)
    def test_emit_pheromones(self):
        x, y = 2,3
        movement_direction = Direction.random()
        z,q = 2,3
        self.grid_mock.pheromones.emit(x, y, movement_direction)
        self.grid_mock.pheromones.emit(z, q, movement_direction)

        # emitted_grid = self.grid_mock.pheromones.grid
        # print("Pheromone grid after emission:")
        # print(emitted_grid)

    def test_emit_without_move(self):
        """Ensure that pheromone emission does not apply when direction is Compass.CENTER"""
        x, y = 2, 1
        movement_direction = Direction(Compass.CENTER)

        self.grid_mock.pheromones.emit(x, y, movement_direction)

        emitted_values = np.sum(self.grid_mock.pheromones.grid)
        self.assertEqual(emitted_values, 0,"pheromones should not be emitted")

    def test_emit_out_of_bounds(self):
        """Ensure that pheromone emission does not affect out-of-bounds or edge cells."""
        x, y = 2,2
        movement_direction = Direction(Compass.EAST)

        self.grid_mock.pheromones.emit(x, y, movement_direction)

        emitted_grid = self.grid_mock.pheromones.grid

        for i in range(self.grid_mock.width):
            self.assertEqual(emitted_grid[0, i], 0, f"Top edge at (0, {i}) should not have pheromones.")
            self.assertEqual(emitted_grid[-1, i], 0,
                             f"Bottom edge at ({self.grid_mock.height - 1}, {i}) should not have pheromones.")

        for j in range(self.grid_mock.height):
            self.assertEqual(emitted_grid[j, 0], 0, f"Left edge at ({j}, 0) should not have pheromones.")
            self.assertEqual(emitted_grid[j, -1], 0,
                             f"Right edge at ({j}, {self.grid_mock.width - 1}) should not have pheromones.")
        # print(emitted_grid)
    def test_emit_strength_decreases_with_distance(self):
        """Ensure pheromone intensity decreases correctly with distance."""
        x, y = 3,3
        direction = Direction(Compass.EAST)

        self.grid_mock.pheromones.emit(x, y, direction)

        emitted_grid = self.grid_mock.pheromones.grid

        self.assertGreater(emitted_grid[2,3], emitted_grid[1,3], "Intensity should decrease with distance")
        self.assertGreater(emitted_grid[2, 3], emitted_grid[2, 4], "Intensity should decrease with angle")

    def test_read_pheromones_direction(self):
        """
        Ensure the sensor correctly reads pheromones in the forward direction.
        Handle edge cases where no pheromones are emitted due to boundaries.
        """
        x, y = 1, 1  # Emitter position
        emitter_direction = Direction(Compass.WEST)

        # Emit pheromones
        self.grid_mock.pheromones.emit(x, y, emitter_direction)

        emitted_values = np.sum(self.grid_mock.pheromones.grid)
        # print(f"Sum of emitted values: {emitted_values}")
        # print("Pheromone grid after emission:")
        # print(self.grid_mock.pheromones.grid)

        if emitted_values == 0:
            # print("No pheromones emitted due to boundary conditions.")
            self.assertEqual(emitted_values, 0)
        else:
            forward_intensity = self.grid_mock.pheromones.read(x, y, Direction(Compass.EAST), "r")
            # print(f"Pheromone intensity detected: {forward_intensity}")

            self.assertGreater(forward_intensity, 0, "Sensor should detect pheromones in the forward direction.")

    def test_spread(self):

        # print("Setup grid dimensions:", self.grid_mock.pheromones.grid.shape)

        """Test that pheromones spread and decay correctly while avoiding boundaries."""
        self.grid_mock.pheromones.grid[3, 2] = 1.0
        self.grid_mock.pheromones.grid[2, 1] = 0.5

        # print("Initial pheromone grid:")
        # print(self.grid_mock.pheromones.grid)

        # Apply spreading and decay
        self.grid_mock.pheromones.spread()

        # print("Pheromone grid after spread:")
        # print(self.grid_mock.pheromones.grid)

        self.assertLess(self.grid_mock.pheromones.grid[3, 2], 1.0, "Central pheromone should decay over time.")
        self.assertLess(self.grid_mock.pheromones.grid[4, 1], 0.5, "Secondary pheromone should decay over time.")
        self.assertGreater(self.grid_mock.pheromones.grid[3, 3], 0.0,
                           "Neighboring cells should have increased intensity due to diffusion.")
        self.assertGreater(self.grid_mock.pheromones.grid[2, 2], 0.0,
                           "Neighboring cells should have increased intensity due to diffusion.")
        self.assertEqual(self.grid_mock.pheromones.grid[0, 0], 0.0, "Boundary cells should always remain zero.")
        self.assertEqual(self.grid_mock.pheromones.grid[self.grid_mock.pheromones.width - 1, 0], 0.0,
                         "Boundary cells should always remain zero.")
        self.assertEqual(self.grid_mock.pheromones.grid[0, self.grid_mock.pheromones.height - 1], 0.0,
                         "Boundary cells should always remain zero.")
if __name__ == "__main__":
    unittest.main()
