import os

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from taplt import source_directory


class WelcomeScreen(QWidget):

    def __init__(self):
        super(WelcomeScreen, self).__init__()

        self.label = QLabel()
        self.label.setText("Welcome to the \n \n"
                           "All-Purpose Labeling Tool \n \n \n"
                           "Create or open a project to get started")
        self.label.setFont(QFont("Helvetica", 20, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon = os.path.join(source_directory, 'icons', 'welcome.jpg')
        self.label.setStyleSheet(f"background-image: url({icon});"
                                 "background-repeat: no-repeat;"
                                 "background-position: center;")

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.label)
