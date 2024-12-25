import math

import numpy as np
from PyQt6.QtWidgets import QFrame

import config
from src.gui.MarkType import MarkType
from src.gui.Square import Square


class Map(QFrame):
    def __init__(self):
        super().__init__()

        # track marked spaces on map
        self._grid = np.zeros((config.DIM, config.DIM), dtype=np.int16)

        # remember currently placing mark type
        self._cur_mark = MarkType.BARRIER

        self.setFixedSize(config.MAP_DIM, config.MAP_DIM)
        self.setStyleSheet('background-color: lightblue')

        return

    def mouseMoveEvent(self, e):
        super().mouseMoveEvent(e)

        x = e.pos().x()
        y = e.pos().y()

        if 0 <= x <= config.MAP_DIM and 0 <= y <= config.MAP_DIM:
            x = math.floor(x / config.SINGLE_MAP_SPACE_DIM)
            y = math.floor(y / config.SINGLE_MAP_SPACE_DIM)

            if self._grid[x, y] != self._cur_mark.value:
                self._grid[x, y] = self._cur_mark.value
                Square(self, int(x * config.SINGLE_MAP_SPACE_DIM), int(y * config.SINGLE_MAP_SPACE_DIM), self._cur_mark)

        return

    def set_cur_mark(self, cur_mark: MarkType):
        assert isinstance(cur_mark, MarkType)

        self._cur_mark = cur_mark

        return

    def get_marked_data(self):
        barrier_positions = np.argwhere(self._grid == MarkType.BARRIER.value)
        food_positions = np.argwhere(self._grid == MarkType.FOOD.value)

        return barrier_positions, food_positions
