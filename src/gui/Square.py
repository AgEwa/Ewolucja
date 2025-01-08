from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame

from src.gui.MarkType import MarkType
from src.saves.Settings import Settings


# space on interactive map
class Square(QFrame):
    def __init__(self, p_parent, p_x, p_y, p_mark_type, p_dim):
        """ constructor, takes reference to parent QWidget, positions in grid (int) and mark type """

        # use derived constructor
        super().__init__(p_parent)

        # depending on mark type use different colour
        match p_mark_type:
            case MarkType.BARRIER:
                self.setStyleSheet('background-color: black;')
            case MarkType.FOOD:
                self.setStyleSheet('background-color: green;')
            case _:
                pass

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # store mark type
        self.mark_type = p_mark_type

        # place square on map
        self.setGeometry(round(p_x * Settings.SPACE_DIM(p_dim)), round(p_y * Settings.SPACE_DIM(p_dim)), round(Settings.SPACE_DIM(p_dim)), round(Settings.SPACE_DIM(p_dim)))
        # show square
        self.show()

        return

    def repaint(self):
        match self.mark_type:
            case MarkType.BARRIER:
                self.setStyleSheet('background-color: black;')
            case MarkType.FOOD:
                self.setStyleSheet('background-color: green;')
            case _:
                pass

        super().repaint()
