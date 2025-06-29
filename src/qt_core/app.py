import sys
import os
from PySide6 import QtCore, QtWidgets, QtGui
from abc import ABC, abstractmethod


class ScreenStrategy(ABC):
    @abstractmethod
    def setup_ui(self):
        pass

    @abstractmethod
    def get_widget(self) -> QtWidgets.QWidget:
        pass


class MainScreenStrategy(ScreenStrategy):
    def __init__(self, controller):
        self.controller = controller
        self.widget = QtWidgets.QWidget()
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self.widget)
        self.text = QtWidgets.QLabel(
            "Select dataset folder",
            alignment=QtCore.Qt.AlignmentFlag.AlignCenter
            )
        layout.addWidget(self.text)

        self.select_folder_btn = QtWidgets.QPushButton("Select folder with images")
        layout.addWidget(self.select_folder_btn)
        self.select_folder_btn.clicked.connect(self.controller.select_directory)

    def get_widget(self):
        return self.widget


class DirectoryScreenStrategy(ScreenStrategy):
    def __init__(self, controller):
        self.controller = controller
        self.widget = QtWidgets.QWidget()

        # init scroll_area
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(5)
        self.scroll_area.setWidget(self.scroll_content)

        self.setup_ui()

    def setup_ui(self):
        dir_layout = QtWidgets.QVBoxLayout(self.widget)
        self.dir_label = QtWidgets.QLabel(
            "",
            alignment=QtCore.Qt.AlignmentFlag.AlignHCenter
            )
        dir_layout.addWidget(self.dir_label)

        self.dir_folders = QtWidgets.QLabel(
            "",
            alignment=QtCore.Qt.AlignmentFlag.AlignHCenter
            )
        dir_layout.addWidget(self.dir_folders)
        dir_layout.addWidget(self.scroll_area)

        self.back_btn = QtWidgets.QPushButton("Back")
        dir_layout.addWidget(self.back_btn)
        self.back_btn.clicked.connect(self.controller.go_to_main_screen)

        self.patients_selector = QtWidgets.QPushButton("Select patient")
        dir_layout.addWidget(self.patients_selector)
        self.patients_selector.clicked.connect(self.controller.go_to_patients_screen)

    def get_widget(self):
        return self.widget

    def update_directory_info(self, path, folders):
        # clear dirs
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for folder in folders:
            txt = QtWidgets.QLabel(f"{folder}")
            txt.setFixedHeight(40)
            txt.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
            txt.setStyleSheet(
                """
                QLabel {
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 5px;
                    background: #f8f8f8;
                }
            """
                )
            txt.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Fixed
                )
            self.scroll_layout.addWidget(txt)

class PatientsScreenStrategy(ScreenStrategy):
    def __init__(self, controller):
        self.controller = controller
        self.widget = QtWidgets.QWidget()

        # init scroll_area
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        self.setup_ui()

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self.widget)
        self.patients_label = QtWidgets.QLabel(
            "Patients found:",
            alignment=QtCore.Qt.AlignmentFlag.AlignHCenter
            )
        main_layout.addWidget(self.patients_label)

        main_layout.addWidget(self.scroll_area)

        self.back_btn = QtWidgets.QPushButton("Back")
        main_layout.addWidget(self.back_btn)
        self.back_btn.clicked.connect(self.controller.go_to_directory_screen)

    def get_widget(self):
        return self.widget

    def add_patients(self, patients):
        # clear patients
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for patient in patients:
            btn = QtWidgets.QPushButton(f"{patient}")
            btn.setFixedHeight(40)
            btn.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Fixed
                )

            self.scroll_layout.addWidget(btn)


class ScreenManager:
    def __init__(self):
        self.stacked_layout = QtWidgets.QStackedLayout()
        self.screens = {}

    def add_screen(self, name, strategy):
        self.screens[name] = strategy
        self.stacked_layout.addWidget(strategy.get_widget())

    def set_current_screen(self, name):
        self.stacked_layout.setCurrentWidget(self.screens[name].get_widget())


class AppController:
    def __init__(self, view):
        self.view = view
        self.patients_dirs = []

    def select_directory(self):
        selected_directory = QtWidgets.QFileDialog.getExistingDirectory(
            parent=self.view, caption="Select folder"
        )
        if selected_directory:
            dir_folders = os.listdir(selected_directory)
            self.patients_dirs = dir_folders.copy()
            self.view.update_directory_screen(selected_directory, dir_folders)
            self.view.set_current_screen('directory')

    def go_to_main_screen(self):
        self.view.set_current_screen('main')

    def go_to_directory_screen(self):
        self.view.set_current_screen('directory')

    def go_to_patients_screen(self):
        self.view.update_patients_screen(self.patients_dirs)
        self.view.set_current_screen('patients')


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("sneaky-vaccine-cvat")
        self.setFixedSize(1280, 800)

        self.controller = AppController(self)
        self.screen_manager = ScreenManager()

        main_screen = MainScreenStrategy(self.controller)
        directory_screen = DirectoryScreenStrategy(self.controller)
        patients_screen = PatientsScreenStrategy(self.controller)

        self.screen_manager.add_screen('main', main_screen)
        self.screen_manager.add_screen('directory', directory_screen)
        self.screen_manager.add_screen('patients', patients_screen)

        self.setLayout(self.screen_manager.stacked_layout)
        self.set_current_screen('main')

    def set_current_screen(self, screen_name):
        self.screen_manager.set_current_screen(screen_name)

    def update_directory_screen(self, path, folders):
        directory_screen = self.screen_manager.screens['directory']
        directory_screen.update_directory_info(path, folders)

    def update_patients_screen(self, patients):
        patients_screen = self.screen_manager.screens['patients']
        patients_screen.add_patients(patients)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.show()

    sys.exit(app.exec())