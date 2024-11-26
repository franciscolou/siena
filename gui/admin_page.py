import sys
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QScrollArea, QHBoxLayout
from PyQt6 import QtGui
from PyQt6 import QtCore
from gui import MainWindow
from gui_tools import validate_credentials, resource_path
from gui_widgets import CustomTitleBar, SearchWidget
import time
import ctypes

myappid = u'DIC.SIENA.Login.1_0' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
version = '1.1.0'

menuBarHeight = 40
windowWidth = 650
windowHeight = 590 + menuBarHeight
input_styling = "background-color: #e0e0e0; border-radius: 5px; font-size: 15px; padding: 3px;"

relative_path = ''

# Placeholder list of users
users = ["User1", "User2", "User3", "User4", "User5"]

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        QtGui.QFontDatabase.addApplicationFont(resource_path("assets/fonts/Ubuntu-Regular.ttf"))
        self.current_font = QtGui.QFont("Ubuntu")
        
        self.setWindowTitle("[DIC/CORE] SIENA - Login")
        self.setWindowIcon(QtGui.QIcon(resource_path('assets/images/SIENA.png')))

        self.setGeometry(100, 100, 650, 590)
        self.setObjectName("Window")
        self.setStyleSheet("#Window {background-color: #301310;}")
        self.setFixedSize(windowWidth, windowHeight)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setMenuBar(None)
        self.title_bar = CustomTitleBar(self, color="#301310", width=windowWidth, height=menuBarHeight, title="SIENA - Admin Page")
        self.setMenuWidget(self.title_bar)

        # Create a central widget and set it as the central widget of the window
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a QVBoxLayout for the central widget
        layout = QVBoxLayout(central_widget)

        # Create a QScrollArea to hold the user list
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Create a QWidget to hold the user labels and set it as the widget of the scroll area
        user_list_widget = QWidget()
        user_list_widget.setStyleSheet("background-color: #5a1f1f;")  # Lighter wine background
        scroll_area.setWidget(user_list_widget)

        # Create a QVBoxLayout for the user list widget
        user_list_layout = QVBoxLayout(user_list_widget)



        # Add user labels to the user list layout
        for user in users:
            user_label = QLabel(user, self)
            user_label.setFont(self.current_font)
            user_label.setStyleSheet("color: white; font-size: 18px;")
            user_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # Center align text
            user_list_layout.addWidget(user_label)

        # Add a stretch at the end to push all items to the top
        user_list_layout.addStretch()

        # Center the user list layout horizontally
        user_list_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())