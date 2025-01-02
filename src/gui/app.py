from PyQt6.QtWidgets import QApplication

from src.gui.MainWindow import MainWindow
from src.saves.Saves import Saves
from src.saves.Settings import Settings


class Main:
    @staticmethod
    def main():
        # initialise saves directory
        Saves.init()

        # read settings and store them in class, so they can be accessed everywhere without circular import error
        Settings.read()

        # creating application object. you can pass sys.args as argument to it
        # if you want your application to support starting arguments
        # we don't need that (for now?) so pass empty list
        app = QApplication([])
        # create main window of application
        window = MainWindow()
        # show it most definitely
        window.show()
        # start application loop
        app.exec()

        window.shut()
        return


if __name__ == '__main__':
    Main.main()
