import math

from PyQt6.QtWidgets import QFrame

import config
from src.gui.MarkType import MarkType
from src.gui.Square import Square


# interactive map
class Map(QFrame):
    def __init__(self):
        """ constructor """

        # use derived constructor
        super().__init__()

        # track marked spaces on map
        self._grid: list[list[Square | None]] = [[None for j in range(config.DIM)] for i in range(config.DIM)]

        # remember currently placing mark type
        self._cur_mark = MarkType.BARRIER

        # set map's size
        self.setFixedSize(config.MAP_DIM, config.MAP_DIM)
        # set map's background color
        self.setStyleSheet('background-color: lightblue')

        return

    def draw2(self, p_x, p_y):
        # process only coordinates in-bounds (on map)
        if 0 <= p_x < config.MAP_DIM and 0 <= p_y < config.MAP_DIM:
            # counts how many full spaces fit on x, y axes until detected cursor position
            # and also corresponds to coordinates in self._grid that should be marked!
            x = math.floor(p_x / config.SPACE_DIM)
            y = math.floor(p_y / config.SPACE_DIM)

            # if space was empty, and we do not currently clear plane
            if self._grid[x][y] is None and self._cur_mark != MarkType.EMPTY:
                # create new space at given position and current mark type
                self._grid[x][
                    y] = Square(self, round(x * config.SPACE_DIM), round(y * config.SPACE_DIM), self._cur_mark)
            # if space was not empty, and we do not currently clear plane
            elif self._grid[x][y] is not None and self._cur_mark != MarkType.EMPTY:
                # if used mark type is different from what is already present in space
                if self._grid[x][y].mark_type != self._cur_mark:
                    self._grid[x][y].mark_type = self._cur_mark
                    self._grid[x][y].repaint()
            # if space was not empty, and want to clear plane
            elif self._grid[x][y] is not None and self._cur_mark == MarkType.EMPTY:
                # destruct existing object
                # del self._grid[x][y]
                self._grid[x][y].close()
                # and set value to None
                self._grid[x][y] = None

        return

    def draw(self, p_x, p_y) -> None:
        try:
            if 0 <= p_x < config.MAP_DIM and 0 <= p_y < config.MAP_DIM:
                x = math.floor(p_x / config.SPACE_DIM)
                y = math.floor(p_y / config.SPACE_DIM)

                self._grid[x][y] = Square(self, round(x * config.SPACE_DIM), round(y * config.SPACE_DIM), self._cur_mark)
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

    def get_marked_data(self) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
        """ returns positions of places of barriers and food sources """

        # stores barriers positions
        barrier_positions = []
        # stores food positions
        food_positions = []

        # go through the grid
        for x in range(config.DIM):
            for y in range(config.DIM):
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

        return barrier_positions, food_positions
