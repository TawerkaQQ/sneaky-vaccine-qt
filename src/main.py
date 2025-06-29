import sys

from PySide6 import QtWidgets
from src.qt_core.app import MyWidget








if __name__ == "__main__":

    applictation = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(applictation.exec())