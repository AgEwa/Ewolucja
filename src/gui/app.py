from multiprocessing import set_start_method, freeze_support

from PyQt6.QtWidgets import QApplication

# the next three lines needed for application to be run from command line.
from pathlib import Path
import sys, os
# essentially points where root of project is located, so imports like src.* and config are found.
sys.path.append(Path(os.path.realpath(__file__)).parent.parent.parent.absolute().__str__())

from src.gui.MainWindow import MainWindow
from src.saves.SavesStarter import SavesStarter
from src.saves.Settings import Settings


class Main:
    @staticmethod
    def main():
        # initialise saves directory
        SavesStarter.init()

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
    freeze_support()
    set_start_method('spawn')
    Main.main()
