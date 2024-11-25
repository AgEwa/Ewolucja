from unittest import TestCase
from unittest.mock import MagicMock, patch, Mock

from src.LocationTypes import Direction, Compass
from src.utils.utils import *


class TestUtils(TestCase):
    def test_initialize_genome(self):
        genome = initialize_genome(4)
        self.assertEqual(len(genome), 4)

    def test_generate_hex(self):
        gene = generate_hex()
        self.assertEqual(len(gene), 8)

    def test_bin_to_signed_int(self):
        positive_int = bin_to_signed_int('0111111111111111')
        negative_int = bin_to_signed_int('1111111111111111')
        self.assertEqual(positive_int, 32767)
        self.assertEqual(negative_int, -1)

    @patch('src.LocationTypes.Conversions')
    def test_drain_move_queue(self, mock_conversions):
        # given
        # mock the Grid
        mock_grid = grid
        mock_grid.in_bounds = Mock(side_effect=lambda coord: 0 <= coord.x < 5 and 0 <= coord.y < 5)
        mock_grid.is_empty_at = Mock(side_effect=lambda coord: coord != Coord(2, 2))  # (2,2) is occupied
        mock_grid.is_food_at = Mock(side_effect=lambda coord: coord == Coord(1, 1))  # food at (1,1)
        mock_grid.food_eaten_at = MagicMock()
        mock_grid.data = {}  # simulate a 2D grid with a dictionary
        # mock Conversions
        mock_conversions.coord_as_direction.side_effect = lambda coord: Direction(Compass.CENTER)
        # mock specimen_1
        specimen_1 = MagicMock()
        specimen_1.location = Coord(0, 0)
        specimen_1.index = 1
        specimen_1.alive = True
        specimen_1.eat = MagicMock()
        # mock specimen_2
        specimen_2 = MagicMock()
        specimen_2.location = Coord(1, 0)
        specimen_2.index = 2
        specimen_2.alive = True
        specimen_2.eat = MagicMock()

        move_queue = [
            (specimen_1, [Coord(1, 0), Coord(1, 1)]),  # specimen_1 moves from (0,0) to (1,0) and to (2,1)
            (specimen_2, [Coord(0, 1), Coord(1, 1)])  # specimen_2 moves from (1,0) to (1,1) and tries to move to (2,2)
        ]

        # when
        drain_move_queue(move_queue)

        # then
        # specimen_1 moved and updated
        self.assertEqual(specimen_1.location, Coord(2, 1))
        self.assertEqual(specimen_1.last_movement, Coord(2, 1))
        self.assertEqual(specimen_1.last_movement_direction, Direction(Compass.CENTER))
        specimen_1.eat.assert_not_called()  # specimen_1 didn't eat
        # specimen_2 moved and updated
        self.assertEqual(specimen_2.location, Coord(1, 1))
        self.assertEqual(specimen_2.last_movement, Coord(0, 1))
        specimen_2.eat.assert_called_once()  # specimen_2 found food at (1,1)
        mock_grid.food_eaten_at.assert_called_once()
        # queue cleared
        self.assertEqual(len(move_queue), 0)
        # grid updated
        self.assertEqual(mock_grid.data[(2, 1)], specimen_1.index)
        self.assertEqual(mock_grid.data[(1, 1)], specimen_2.index)
        self.assertEqual(mock_grid.data[(0, 0)], 0)
        self.assertEqual(mock_grid.data[(1, 0)], 0)
