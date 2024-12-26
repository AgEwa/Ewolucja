from PyQt6.QtWidgets import QFrame

import config
from src.gui.MarkType import MarkType


# space on interactive map
class Square(QFrame):
    def __init__(self, p_parent, p_x, p_y, p_mark_type):
        """ constructor """

        # use derived constructor
        super().__init__(p_parent)

        # depending on mark type use diferent colour
        match p_mark_type:
            case MarkType.BARRIER:
                self.setStyleSheet('background-color: black;')
            case MarkType.FOOD:
                self.setStyleSheet('background-color: green;')
            case _:
                pass

        # store mark type
        self.mark_type = p_mark_type

        # place square on map
        self.setGeometry(p_x, p_y, round(config.SINGLE_MAP_SPACE_DIM), round(config.SINGLE_MAP_SPACE_DIM))
        # show square
        self.show()

        return
