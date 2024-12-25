from PyQt6.QtWidgets import QFrame

import config
from src.gui.MarkType import MarkType


class Square(QFrame):
    def __init__(self, p_parent, p_x, p_y, p_mark_type):
        super().__init__(p_parent)

        match p_mark_type:
            case MarkType.BARRIER:
                self.setStyleSheet('background-color: black;')
            case MarkType.FOOD:
                self.setStyleSheet('background-color: green;')
            case _:
                pass

        self.setGeometry(p_x, p_y, int(config.SINGLE_MAP_SPACE_DIM), int(config.SINGLE_MAP_SPACE_DIM))
        self.show()

        return
