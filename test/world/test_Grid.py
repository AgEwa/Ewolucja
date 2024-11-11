from unittest import TestCase

from LocationTypes import Coord
from world.Grid import Grid


class TestGrid(TestCase):

    def setUp(self):
        self.grid = Grid(2, 2)
        self.grid.data[0, 0] = Grid.FOOD
        self.grid.data[0, 1] = Grid.BARRIER
        self.specimen_id = 37
        self.grid.data[1, 0] = self.specimen_id

        self.loc_food = Coord(0, 0)
        self.loc_barrier = Coord(0, 1)
        self.loc_specimen = Coord(1, 0)
        self.loc_empty = Coord(1, 1)
        self.loc_out = Coord(0, 3)

    def test_in_bounds(self):
        # test for location in bounds
        self.assertTrue(self.grid.in_bounds(self.loc_empty))

        # test for location out of bounds
        self.assertFalse(self.grid.in_bounds(self.loc_out))

    def test_at(self):
        # test for empty location
        self.assertIn(self.grid.at(self.loc_empty), Grid.EMPTY)
        # test for specimen's location
        self.assertEqual(self.grid.at(self.loc_specimen), self.specimen_id)
        # test for food location
        self.assertEqual(self.grid.at(self.loc_food), Grid.FOOD)
        # test for barrier location
        self.assertEqual(self.grid.at(self.loc_barrier), Grid.BARRIER)

    def test_is_empty_at(self):
        # test for empty location
        self.assertTrue(self.grid.is_empty_at(self.loc_empty))
        # test for food location
        self.assertTrue(self.grid.is_empty_at(self.loc_food))

        # test for specimen's location
        self.assertFalse(self.grid.is_empty_at(self.loc_specimen))
        # test for barrier location
        self.assertFalse(self.grid.is_empty_at(self.loc_barrier))

    def test_is_barrier_at(self):
        # test for barrier location
        self.assertTrue(self.grid.is_barrier_at(self.loc_barrier))

        # test for empty location
        self.assertFalse(self.grid.is_barrier_at(self.loc_empty))
        # test for food location
        self.assertFalse(self.grid.is_barrier_at(self.loc_food))
        # test for specimen's location
        self.assertFalse(self.grid.is_barrier_at(self.loc_specimen))

    def test_is_occupied_at(self):
        # test for specimen's location
        self.assertTrue(self.grid.is_occupied_at(self.loc_specimen))

        # test for empty location
        self.assertFalse(self.grid.is_occupied_at(self.loc_empty))
        # test for food location
        self.assertFalse(self.grid.is_occupied_at(self.loc_food))
        # test for barrier location
        self.assertFalse(self.grid.is_occupied_at(self.loc_barrier))

    def test_is_food_at(self):
        # test for food location
        self.assertTrue(self.grid.is_food_at(self.loc_food))

        # test for empty location
        self.assertFalse(self.grid.is_food_at(self.loc_empty))
        # test for specimen's location
        self.assertFalse(self.grid.is_food_at(self.loc_specimen))
        # test for barrier location
        self.assertFalse(self.grid.is_food_at(self.loc_barrier))

    def test_find_empty(self):
        result = self.grid.find_empty()
        self.assertIn(self.grid.at(result), Grid.EMPTY)

    def test_in_bounds_xy(self):
        # test for location in bounds
        self.assertTrue(self.grid.in_bounds_xy(self.loc_food.x, self.loc_food.y))

        # test for location out of bounds
        self.assertFalse(self.grid.in_bounds_xy(self.loc_out.x, self.loc_out.y))

    def test_at_xy(self):
        # test for empty location
        self.assertIn(self.grid.at_xy(self.loc_empty.x, self.loc_empty.y), Grid.EMPTY)

    def test_is_empty_at_xy(self):
        # test for empty location
        self.assertTrue(self.grid.is_empty_at_xy(self.loc_empty.x, self.loc_empty.y))

    def test_is_barrier_at_xy(self):
        # test for barrier location
        self.assertTrue(self.grid.is_barrier_at_xy(self.loc_barrier.x, self.loc_barrier.y))

    def test_is_occupied_at_xy(self):
        # test for specimen's location
        self.assertTrue(self.grid.is_occupied_at_xy(self.loc_specimen.x, self.loc_specimen.y))

    def test_is_food_at_xy(self):
        # test for food location
        self.assertTrue(self.grid.is_food_at_xy(self.loc_food.x, self.loc_food.y))
