import math

from PyQt6.QtWidgets import QFrame

import config
from src.gui.MarkType import MarkType
from src.gui.Square import Square
from src.saves.MapSave import MapSave
from src.saves.Settings import Settings


# interactive map
class Map(QFrame):
    def __init__(self, p_map_save: MapSave = None):
        """ constructor, takes optional parameter p_map_save which places default spaces on map """

        # use derived constructor
        super().__init__()

        self._dim = Settings.settings.dim if p_map_save is None else p_map_save.dim

        # track marked spaces on map
        self._grid: list[list[Square | None]] = [[None for j in range(self._dim)] for i in range(self._dim)]

        # if new plane creator was opened to edit existing plane
        if p_map_save is not None:
            # go through barriers:
            for barrier in p_map_save.barrier_positions:
                # place it on map
                self._grid[barrier[0]][barrier[1]] = Square(self, barrier[0], barrier[1], MarkType.BARRIER, self._dim)

            # go through food:
            for food in p_map_save.food_positions:
                # place it on map
                self._grid[food[0]][food[1]] = Square(self, food[0], food[1], MarkType.FOOD, self._dim)

        # remember currently placing mark type
        self._cur_mark = MarkType.BARRIER

        # set map's size
        self.setFixedSize(config.MAP_DIM, config.MAP_DIM)
        # set map's background color
        self.setStyleSheet('background-color: lightblue')

        return

    def draw(self, p_x, p_y) -> None:
        try:
            # if position is in bounds of map
            if 0 <= p_x < config.MAP_DIM and 0 <= p_y < config.MAP_DIM:
                # calculate indexes of grid to be marked
                x = math.floor(p_x / Settings.SPACE_DIM(self._dim))
                y = math.floor(p_y / Settings.SPACE_DIM(self._dim))

                # mark grid
                self._grid[x][y] = Square(self, x, y, self._cur_mark, self._dim)
        except Exception as e:
            print(e)

        return

    def mouseReleaseEvent(self, e) -> None:
        """ event is called every time mouse button is released """

        # draw square based on cursor current position
        self.draw(e.pos().x(), e.pos().y())

        # use derived method
        super().mouseReleaseEvent(e)

        return

    def mouseMoveEvent(self, e) -> None:
        """ event is called every time mouse moves (while either mouse button is pressed down) """

        # draw square based on cursor current position
        self.draw(e.pos().x(), e.pos().y())

        # use derived method
        super().mouseMoveEvent(e)

        return

    def set_cur_mark(self, cur_mark: MarkType) -> None:
        """ changes currently placing object type """

        assert isinstance(cur_mark, MarkType)

        # set new value
        self._cur_mark = cur_mark

        return

    def get_marked_data(self) -> MapSave:
        """ returns positions of places of barriers and food sources """

        # stores barriers positions
        barrier_positions = []
        # stores food positions
        food_positions = []

        # go through the grid
        for x in range(self._dim):
            for y in range(self._dim):
                # if cell is not None, then it is marked space
                if self._grid[x][y] is not None:
                    # if its type is barrier
                    if self._grid[x][y].mark_type == MarkType.BARRIER:
                        # add to barriers positions list
                        barrier_positions.append((x, y))
                    # if its type is food
                    elif self._grid[x][y].mark_type == MarkType.FOOD:
                        # add to food positions list
                        food_positions.append((x, y))

        res = MapSave(self._dim, barrier_positions, food_positions)

        return res
