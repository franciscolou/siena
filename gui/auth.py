import sys
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt6 import QtGui
from PyQt6 import QtCore
from gui import MainWindow
from gui_tools import validate_credentials, resource_path
from gui_widgets import CustomTitleBar
import time
import ctypes

myappid = u'DIC.SIENA.Login.1_0' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
version = '1.2.0'

menuBarHeight = 30
windowWidth = 650
windowHeight = 590 + menuBarHeight
input_styling = "background-color: #e0e0e0; border-radius: 5px; font-size: 15px; padding: 3px;"

relative_path = ''
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        QtGui.QFontDatabase.addApplicationFont(resource_path("assets/fonts/Ubuntu-Regular.ttf"))
        self.current_font = QtGui.QFont("Ubuntu")
        
        self.setWindowTitle("[DIC/CORE] SIENA - Login")
        self.setWindowIcon(QtGui.QIcon(resource_path('assets/images/SIENA.png')))

        screen = QApplication.primaryScreen().availableGeometry()
        x = int((screen.width() - windowWidth) / 2)
        y = int((screen.height() - windowHeight) / 2)
        self.setGeometry(x, y, windowWidth, windowHeight)
        self.setObjectName("Window")
        self.setStyleSheet("#Window {background-color: #301310;}")
        self.setFixedSize(windowWidth, windowHeight)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setMenuBar(None)
        self.title_bar = CustomTitleBar(self, color="#171717", width=windowWidth, height=menuBarHeight, title="SIENA - Login")
        self.title_bar.maximize_button.mousePressEvent = lambda event: None
        self.setMenuWidget(self.title_bar)

        self.background_image = QLabel(self)
        self.background_image.setGeometry(0, 40, windowWidth, windowHeight)
        self.background_image.setPixmap(QtGui.QPixmap(resource_path('assets/images/background.png')))
        self.background_image.setScaledContents(True)
        
        self.version_label = QLabel(f"Versão {version}", self)
        self.version_label.setFixedSize(80, 30)
        self.version_label.move(windowWidth - self.version_label.size().width() - 5, windowHeight - self.version_label.size().height() - 3)
        self.version_label.setStyleSheet("color: #cfcfcf;")
        self.current_font.setItalic(True)
        current_font_size = self.current_font.pointSize()
        self.current_font.setPointSize(9)
        self.version_label.setFont(self.current_font)
        self.current_font.setItalic(False)
        self.current_font.setPointSize(current_font_size)
        self.version_label.show()

        # self.core_image = QLabel(self)
        # self.core_image.setFixedSize(220, 220)
        # self.core_image.move(
        #     int(windowWidth/2 - self.core_image.size().width()/2),
        #     int(windowHeight/4 - self.core_image.size().height()/2 + 15)
        # )
        # self.core_image.setPixmap(QtGui.QPixmap(resource_path('assets/images/SIENA.png')))
        # self.core_image.setScaledContents(True)

        # self.siena_title = QLabel("SIENA", self)
        # self.current_font.setPointSize(70)
        # self.current_font.setBold(True)
        # self.current_font.setItalic(True)
        # self.siena_title.setFont(self.current_font)
        # self.current_font.setItalic(False)

        # font_metrics = QtGui.QFontMetrics(self.current_font)
        # text_size = font_metrics.size(0, self.siena_title.text())
        
        # self.siena_title.setFixedSize(text_size.width(), text_size.height())

        # core_image_size = self.core_image.size()
        # core_image_pos = self.core_image.pos()
        # self.siena_title.move(
        #     int(core_image_pos.x() + core_image_size.width()/2 - self.siena_title.size().width()/2 -5),
        #     int(core_image_pos.y() + core_image_size.height()/2 - self.siena_title.size().height()/2)
        # )
        # self.siena_title.setStyleSheet("color: #FFFFFF;")
        # # Create a QGraphicsDropShadowEffect for the outline
        # shadow = QGraphicsDropShadowEffect()
        # shadow.setBlurRadius(50)
        # shadow.setColor(QtGui.QColor(0, 0, 0))
        # shadow.setOffset(1, 1)

        # # Apply the shadow effect to the siena_title
        # self.siena_title.setGraphicsEffect(shadow)

        # Username label and input
        self.username_label = QLabel("Usuário:", self)
        self.username_label.setFixedSize(100, 35)
        self.username_label.move(
            int(windowWidth/3 - self.username_label.size().width()/2),
            int(windowHeight/2 - self.username_label.size().height()/2 + 10)
        )

        self.current_font.setPointSize(13)
        self.username_label.setFont(self.current_font)
        self.username_label.setStyleSheet("color: #FFFFFF;")
        
        username_label_pos = self.username_label.pos()

        self.username_input = QLineEdit(self)
        self.username_input.setFixedSize(225, 35)
        self.username_input.move(
            int(username_label_pos.x() + self.username_label.size().width()),
            username_label_pos.y()
        )
        self.username_input.setStyleSheet(input_styling)
        self.username_input.returnPressed.connect(self.handle_login)

        # Password label and input
        self.password_label = QLabel("Senha:", self)
        self.password_label.setFixedSize(100, 35)
        self.password_label.move(
            int(windowWidth/3 - self.password_label.size().width()/2),
            int(windowHeight/1.65 - self.password_label.size().height()/2 + 10)
        )
        self.current_font.setPointSize(13)
        self.password_label.setFont(self.current_font)
        self.password_label.setStyleSheet("color: #FFFFFF;")
        
        password_label_pos = self.password_label.pos()
        self.password_input = QLineEdit(self)
        self.password_input.setFixedSize(225, 35)
        self.password_input.move(
            int(password_label_pos.x() + self.password_label.size().width()),
            password_label_pos.y()
        )
        self.password_input.setStyleSheet(input_styling)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.handle_login)
        # Login button
        self.login_button = QPushButton("Confirmar", self)
        self.login_button.setFixedSize(155, 50)
        self.login_button.move(
            int(windowWidth/2 - self.login_button.size().width()/2),
            int(windowHeight/1.3 - self.login_button.size().height()/2)
        )
        self.current_font.setPointSize(11)
        self.login_button.setFont(self.current_font)
        self.login_button.setObjectName("login_button")
        self.login_button.setStyleSheet("""
            QPushButton#login_button {
                background-color: #2e0000;
                border-radius: 5px;
                color: #FFFFFF; 
                border: none;
            }
            QPushButton#login_button:hover {
                background-color: #94110f;
            }
        """)

        # Connect button to a function
        self.login_button.clicked.connect(self.handle_login)

        # Create copyright label
        self.current_font.setPointSize(9)
        self.current_font.setBold(False)
        copyright_text = "© 2024 SIENA. Todos os direitos reservados."
        self.font_metrics = QtGui.QFontMetrics(self.current_font)
        text_size = self.font_metrics.size(0, copyright_text)

        self.copyright_label = QLabel(copyright_text, self)
        self.current_font.setItalic(True)
        self.copyright_label.setFont(self.current_font)
        self.current_font.setItalic(False)
        self.copyright_label.setFixedSize(text_size.width(), text_size.height())
        self.copyright_label.move(
            int(windowWidth/2 - self.copyright_label.size().width()/2),
            int(windowHeight - text_size.height() - 10)
        )
        self.copyright_label.setStyleSheet("color: #cfcfcf;")

    def handle_login(self):
        self.darken_screen = QLabel(self)
        self.darken_screen.setGeometry(0, 0, windowWidth, windowHeight)
        self.darken_screen.setStyleSheet("background-color: rgba(0, 0, 0, 100);")  # Adjust the RGBA values for desired color and opacity
        self.darken_screen.show()
        self.gif_label = QLabel(self)
        self.gif_label.setFixedSize(80, 80)
        # self.gif_label.setFixedSize(50, 50)
        self.gif_label.move(
            int(windowWidth/2 - self.gif_label.size().width()/2),
            int(windowHeight/2 - self.gif_label.size().height()/2)
        )
        
        # Load the GIF
        self.movie = QtGui.QMovie(resource_path("/assets/images/loading.gif"))  # Replace with the path to your GIF file
        self.movie.setScaledSize(self.gif_label.size())
        
        # Set the movie to the QLabel
        self.gif_label.setMovie(self.movie)

        self.movie.start()
        self.gif_label.show()
        username = self.username_input.text()
        password = self.password_input.text()
        login_successful = validate_credentials(username, password)

        if login_successful:
            self.open_SIENA()
        else:
            self.reject_login()
            # QTimer.singleShot(2000, self.remove_loading)

    def open_SIENA(self):
        self.hide()
        self.siena = MainWindow('acesso_a_base')
        self.siena.show()
        self.close()

    def reject_login(self):
        self.gif_label.hide()
        self.darken_screen.hide()
        if not hasattr(self, 'reject_login_label'):
            self.reject_login_label = QLabel("Credenciais inválidas.", self)
            current_font_size = self.current_font.pointSize()
            current_font_bold = self.current_font.bold()
            self.current_font.setBold(False)
            self.current_font.setPointSize(11)
            self.reject_login_label.setFont(self.current_font)
            self.reject_login_label.setStyleSheet("color: #eb6363;")
            self.reject_login_label.adjustSize()
            self.reject_login_label.move(
                int(windowWidth/2 - self.reject_login_label.size().width()/2),
                int(self.password_input.pos().y() + self.password_input.size().height() + 15)
            )

            self.current_font.setPointSize(current_font_size)
            self.current_font.setBold(current_font_bold)
                                      
        self.reject_login_label.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())