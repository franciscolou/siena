from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6 import QtGui
from gui_tools import resource_path
import os
import sys

containerColor = "#474747"
resultsTrackerSize = 70
class SearchWidget(QtWidgets.QFrame):
    def __init__(self, ui, parent, x, y, width, height, object_name, searchbar_background_color, search_bar_width, items_type, results_tracker_text):
        super().__init__(parent)
        self.setGeometry(x, y, width, height)
        self.setObjectName(object_name)
        self.setStyleSheet(f'background-color: transparent; border-color: transparent;')
        self.show()
        self.searchBar = QtWidgets.QLineEdit(self)
        self.searchBar.setObjectName("searchBar")
        searchBarSpace = search_bar_width + 10
        self.searchBar.setGeometry(10, int(height*0.2), search_bar_width, int(height*0.6))
        self.searchBar.setStyleSheet(f"background-color: {searchbar_background_color}; color: #FFFFFF; padding-left: 3px; border: none; border-radius: 5px;")
        ui.current_font = QtGui.QFont("Ubuntu")
        ui.current_font.setPointSize(12)
        ui.current_font.setBold(False)
        self.searchBar.setFont(ui.current_font)
        self.searchBar.installEventFilter(ui)
        self.searchBar.setPlaceholderText("Buscar...")
        self.searchBar.show()

        searchNavUtilsY = int(self.height()/2 - 10)
        self.resultsTracker = QtWidgets.QLabel(self)
        self.resultsTracker.setObjectName("resultsTracker")
        ui.current_font.setPointSize(10)
        self.resultsTracker.setFont(ui.current_font)
        self.resultsTracker.setText(results_tracker_text)
        self.resultsTracker.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.resultsTracker.setFixedSize(resultsTrackerSize, int(height*0.6))
        self.resultsTracker.move(searchBarSpace + 5, int(height/2 - self.resultsTracker.height()/2))

        self.backButton = QSvgWidget(resource_path("assets/images/up_arrow_disabled.svg"), self)
        self.backButton.setObjectName("backButton")
        self.backButton.setGeometry(searchBarSpace + resultsTrackerSize + 10, searchNavUtilsY, 20, 20)
        self.backButton.mousePressEvent = lambda event: ui.highlight_selected_result(-1, items_type)
        self.backButton.show()

        self.nextButton = QSvgWidget(resource_path("assets/images/down_arrow_disabled.svg"), self)
        self.nextButton.setObjectName("nextButton")
        self.nextButton.setGeometry(searchBarSpace + 5 + resultsTrackerSize + 5 + 20 + 5, searchNavUtilsY, 20, 20)
        self.nextButton.mousePressEvent = lambda event: ui.highlight_selected_result(1, items_type)
        self.nextButton.show()

        for widget in self.findChildren(QSvgWidget):
            widget.setCursor(Qt.CursorShape.PointingHandCursor)
            widget.installEventFilter(ui)
            widget.enterEvent = lambda event, w=widget: w.setStyleSheet("border-radius: 5px; background-color: " + containerColor + ";")
            widget.leaveEvent = lambda event, w=widget: w.setStyleSheet("background-color: transparent;")

class CustomTitleBar(QtWidgets.QWidget):
    def __init__(self, ui, color, width, height, title, parent=None, img_path=resource_path('assets/images/lock.svg'), start_pos=QPoint(100, 100), complementary_widgets=[]):
        super().__init__(parent)
        self.current_font = QtGui.QFont("Ubuntu")
        self.setFixedHeight(height)
        self.setStyleSheet(f"background-color: {color}; color: white;")

        self.saved_geometry = None
        self._startPos = start_pos

        self.widget = QtWidgets.QFrame(self)
        self.widget.setGeometry(0, 0, width, height)

        ui.current_font = QtGui.QFont("Ubuntu")
        ui.current_font.setPointSize(12)
        ui.current_font.setBold(False)
        self.title_bar_layout = QtWidgets.QHBoxLayout(self.widget)
        self.title_bar_layout.setContentsMargins(10, 0, 0, 0)
        self.title_bar_layout.setSpacing(0)
        
        self.icon = QSvgWidget(img_path, self.widget)
        self.icon.setFixedSize(14, 16)
        # self.icon.move(
        #     int(height/2 - self.icon.height()/2),
        #     int(height/2 - self.icon.height()/2)
        # )
        self.title_bar_layout.addWidget(self.icon)

        self.title = QtWidgets.QLabel(title, self.widget)
        self.title.setFont(ui.current_font)
        self.title.setStyleSheet("margin-left: 10px;")
        self.title.setFixedHeight(height)
        # self.title.move(self.icon.width() + 5, int(height/2 - self.title.height()/2))
        self.title_bar_layout.addWidget(self.title)

        self.title_bar_layout.addStretch()

        for widget in complementary_widgets:
            self.title_bar_layout.addWidget(widget)

        self.minimize_button = QSvgWidget(resource_path("assets/images/minimize.svg"), self.widget)
        self.minimize_button.setFixedSize(30, 30)
        # self.minimize_button.move(
        #     int(width - self.close_button.width() - self.maximize_button.width() - self.minimize_button.width()),
        #     0
        # )
        self.minimize_button.mousePressEvent = lambda event: self.minimize()
        self.minimize_button.enterEvent = lambda event: self.minimize_button.setStyleSheet("background-color: #9c9c9c;")
        self.minimize_button.leaveEvent = lambda event: self.minimize_button.setStyleSheet("background-color: none;")

        self.title_bar_layout.addWidget(self.minimize_button)
        
        self.maximize_button = QSvgWidget(resource_path("assets/images/maximize.svg"), self.widget)
        self.maximize_button.setFixedSize(30, 30)
        # self.maximize_button.move(
        #     int(width - self.close_button.width() - self.maximize_button.width()),
        #     0
        # )
        self.maximize_button.mousePressEvent = lambda event: self.maximize()
        self.maximize_button.enterEvent = lambda event: self.maximize_button.setStyleSheet("background-color: #9c9c9c;")
        self.maximize_button.leaveEvent = lambda event: self.maximize_button.setStyleSheet("background-color: none;")
        self.title_bar_layout.addWidget(self.maximize_button)

        self.close_button = QSvgWidget(resource_path("assets/images/close_x_white.svg"), self.widget)
        self.close_button.setFixedSize(30, 30)
        # self.close_button.move(int(width - self.close_button.width()), 0)
        self.close_button.mousePressEvent = lambda event: self.close()
        self.close_button.enterEvent = lambda event: self.close_button.setStyleSheet("background-color: #f55656;")
        self.close_button.leaveEvent = lambda event: self.close_button.setStyleSheet("background-color: none;")
        self.title_bar_layout.addWidget(self.close_button)


    def minimize(self):
        self.window().showMinimized()

    def maximize(self):
        if self.window().isMaximized():
            self.window().showNormal()
            self.window().setGeometry(self.saved_geometry)
        else:
            self.saved_geometry = self.window().geometry()
            self.window().showMaximized()

    def close(self):
        self.window().close()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._startPos = event.pos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.window().move(self.window().pos() + event.pos() - self._startPos)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Resize the internal widget to match the new width of the title bar
        self.widget.setGeometry(0, 0, self.width(), self.height())