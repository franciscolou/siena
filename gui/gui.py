import sys
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt
from gui_tools import *
from PyQt6.QtSvgWidgets import QSvgWidget
from gui_widgets import *
from functools import partial


windowWidth = 1130
windowHeight = 720
menuBarHeight = 30

fontcolor = "#FFFFFF"
backgroundColor = "#2e2e2e"
containerColor = "#202020"
contrastColor = "#3e3e3e"
searchHighlightedColor = "#3b3b3b"
searchSelectedHighlightedColor = "#c2951d"

configsHeight = int(windowHeight * 0.1)
memberHeight = 80
changeHeight = 100
defaultSpacing = 2

groupsWidth = int(windowWidth * 0.5)
changesWidth = int(windowWidth * 0.4)

class SquareLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def resizeEvent(self, event):
        size = self.width()
        self.setFixedHeight(size)
        super().resizeEvent(event)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, initial_group):
        super().__init__()

        self.setStyleSheet("color: #ffffff;")
        self.setWindowTitle("SIENA - Home")
        self.setWindowIcon(QtGui.QIcon(resource_path('assets/images/SIENA.png')))
        self.resize(1150, 720)
        self.setMinimumWidth(720)

        QtGui.QFontDatabase.addApplicationFont(resource_path("assets/fonts/Ubuntu-Regular.ttf"))
        self.current_font = QtGui.QFont("Ubuntu")

        self.current_font.setPointSize(10)
        self.current_font.setBold(False)
        self.load_tracker = QtWidgets.QLabel(f"Último carregamento em: {get_formatted_datetime_now()}", self)
        self.load_tracker.setStyleSheet("color: #c7c7c7; margin-right: 20px;")
        self.load_tracker.setFont(self.current_font)

        self.title_bar = CustomTitleBar(
            self, color="#171717",
            width=self.width(),
            height=menuBarHeight,
            title="SIENA - Home",
            start_pos=QPoint(int((self.x() + self.width())/2), self.y()),
            complementary_widgets=[self.load_tracker]
        )
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setMenuBar(None)
        self.setMenuWidget(self.title_bar)

        self.setMouseTracking(True)


        self.groups = []

        self.members_filter = ["user_name"]
        self.searched_members = []

        self.changes_filter = ["changeName"]
        self.searched_changes = []

        # Main widget
        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setStyleSheet(f"background-color: {backgroundColor}; border: none;")
        self.setCentralWidget(self.main_widget)

        size_grip = QtWidgets.QSizeGrip(self.main_widget)
        size_grip.setStyleSheet("background-color: transparent;")
        size_grip.setGeometry(self.main_widget.width() - 20, self.main_widget.height() - 20, 20, 20)

        # Main layout
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_widget.setLayout(self.main_layout)

        # Scroll area for navBar
        self.navBar_scroll_area = QtWidgets.QScrollArea()
        self.navBar_scroll_area.setWidgetResizable(True)
        self.navBar_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.navBar_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.main_layout.addWidget(self.navBar_scroll_area)

        # Navbar
        self.navBar = QtWidgets.QWidget()
        self.navBar.setStyleSheet(f"background-color: {backgroundColor}; padding: 0; margin: 0;")
        self.navBar.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Expanding)
        self.navBar.setFixedWidth(int(self.width() * 0.1))
        self.navBar_scroll_area.setWidget(self.navBar)

        # Navbar layout
        self.navBar_layout = QtWidgets.QVBoxLayout()
        self.navBar_layout.setContentsMargins(0, 0, 0, 0)
        self.navBar_layout.setSpacing(0)
        self.navBar.setLayout(self.navBar_layout)

        # Add elements to the self.navBar
        for i in range(len(groups)):  # Example elements
            group = SquareLabel(self.navBar_scroll_area)
            group.setObjectName(groups[i][0])
            group.setCursor(Qt.CursorShape.PointingHandCursor)
            group.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            group.setPixmap(QtGui.QPixmap(resource_path('assets/images/') + groups[i][0] + '.png'))
            group.setStyleSheet(f"""
            QLabel {{
                background-color: {backgroundColor};
                padding: 15px;  
            }}
            QLabel:hover {{
                background-color: {containerColor};
            }}
            """)
            group.setScaledContents(True)
            group.setFixedWidth(int(self.width() * 0.1))
            group.setFixedHeight(int(self.height() * 0.1))
            group.mousePressEvent = lambda event, i=i, group=group: self.select_group(group, groups[i][0])
            # group.show()

            self.groups.append(group)

            self.navBar_layout.addWidget(group)

        self.navBar_layout.addStretch() 

        # Middle section layout container
        self.middle_section_layout = QtWidgets.QVBoxLayout()
        self.middle_section_layout.setContentsMargins(0, 0, 0, 0)
        self.middle_section_layout.setSpacing(0)
        
        # Middle section scroll area
        self.middle_scroll_area = QtWidgets.QScrollArea()
        self.style_scroll_bar(self.middle_scroll_area)
        self.middle_scroll_area.setWidgetResizable(True)

        # Middle section
        self.middle_section = QtWidgets.QWidget()
        self.middle_section.setStyleSheet(f"background-color: {backgroundColor}; margin: 0;")
        self.middle_section.setFixedWidth(int(self.width() * 0.5))
        self.middle_scroll_area.setWidget(self.middle_section)
        self.middle_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        

        # Layout for middle section (scrollable content)
        self.middle_layout = QtWidgets.QVBoxLayout()
        self.middle_layout.setContentsMargins(0, 0, 0, 0)
        self.middle_layout.setSpacing(defaultSpacing)
        self.middle_section.setLayout(self.middle_layout)

        # Add toolbar at the top of middle section
        self.members_toolbar = QtWidgets.QWidget()
        self.members_toolbar.setFixedHeight(configsHeight)
        self.members_toolbar.setStyleSheet(f"background-color: {backgroundColor}; border-bottom: 1px solid #3e3e3e;")
        # self.members_toolbar.resize(groupsWidth, int(self.height() * 0.1))

        # Add toolbar to the layout (it will stay fixed on top)
        self.middle_section_layout.addWidget(self.members_toolbar)
        self.middle_section_layout.addWidget(self.middle_scroll_area)

        # Apply middle section layout to the middle section widget
        self.middle_container_widget = QtWidgets.QWidget()
        self.middle_container_widget.setLayout(self.middle_section_layout)
        self.main_layout.addWidget(self.middle_container_widget)

        self.groupNameLabel = QtWidgets. QLabel(self.members_toolbar)
        self.groupNameLabel.setObjectName("groupNameLabel")
        self.groupNameLabel.setStyleSheet("border-color: transparent;")
        self.current_font.setPointSize(14)
        self.current_font.setBold(True)
        self.groupNameLabel.setFont(self.current_font)

        self.displayedLengthLabel = QtWidgets.QLabel(self.members_toolbar)
        self.displayedLengthLabel.setObjectName("displayedLengthLabel")
        self.displayedLengthLabel.setStyleSheet("color: #c7c7c7; background-color: none; border-color: transparent;")
        self.current_font.setPointSize(11)
        self.current_font.setBold(False)
        self.displayedLengthLabel.setFont(self.current_font)

        self.membersSearchWidget = SearchWidget(
            ui=self, 
            parent=self.members_toolbar,
            x=0,
            y=0,
            width=int(self.members_toolbar.width() * 0.47) ,
            height=configsHeight,
            object_name="membersSearchWidget",
            searchbar_background_color="#404040",
            search_bar_width=130,
            items_type="members",
            results_tracker_text="---",
        )

        self.membersSearchWidget.searchBar.textChanged.connect(partial(self.search, "members"))


        self.right_section_layout = QtWidgets.QVBoxLayout()
        self.right_section_layout.setContentsMargins(0, 0, 0, 0)
        self.right_section_layout.setSpacing(0)

        # Right section scroll area
        self.right_scroll_area = QtWidgets.QScrollArea()
        self.style_scroll_bar(self.right_scroll_area)
        self.right_scroll_area.setWidgetResizable(True)
        self.right_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.right_scroll_area.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)

        # Right section
        self.right_section = QtWidgets.QWidget()
        self.right_section.setStyleSheet(f"background-color: {backgroundColor}; margin: 0; border-color: black;")
        self.right_scroll_area.setWidget(self.right_section)

        # Right layout
        self.right_layout = QtWidgets.QVBoxLayout()
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(defaultSpacing)
        self.right_section.setLayout(self.right_layout)

        
        self.changes_toolbar = QtWidgets.QWidget()
        self.changes_toolbar.setFixedHeight(configsHeight)
        self.changes_toolbar.setStyleSheet(f"background-color: {backgroundColor}; border-bottom: 1px solid #3e3e3e;")
        self.changes_toolbar.resize(changesWidth, int(self.height() * 0.1))

        # Add toolbar to the layout (it will stay fixed on top)
        self.right_section_layout.addWidget(self.changes_toolbar)
        self.right_section_layout.addWidget(self.right_scroll_area)

        self.changes_label = QtWidgets.QLabel("Atividade", self.changes_toolbar)
        self.changes_label.setObjectName("changes_label")
        self.changes_label.setStyleSheet("border-color: transparent;")
        self.current_font.setPointSize(14)
        self.current_font.setBold(True)
        self.changes_label.setFont(self.current_font)
        self.changes_label.resize(105, 25)
        self.changes_label.move(5, int(configsHeight/2 - self.changes_label.height()/2))

        self.changesSearchWidget = SearchWidget(
            ui=self, 
            parent=self.changes_toolbar,
            x=self.changes_label.width(),
            y=0,
            width=260,
            height=configsHeight,
            object_name="changesSearchWidget",
            searchbar_background_color="#404040",
            search_bar_width=120,
            items_type="changes",
            results_tracker_text="---",
        )

        self.changesSearchWidget.searchBar.textChanged.connect(partial(self.search, "changes"))

        self.refreshButton = QSvgWidget(resource_path("assets/images/refresh_white.svg"), self.changes_toolbar)
        self.refreshButton.setObjectName("refreshButton")
        self.refreshButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refreshButton.setFixedSize(20, 20)
        self.refreshButton.mousePressEvent = lambda event: self.select_group(self.groups[find_group_index(self.current_group)], self.current_group)
        self.refreshButton.move(changesWidth - 30, int(configsHeight/2 - self.refreshButton.height()/2))  


        # Apply right section layout to the right section widget
        right_container_widget = QtWidgets.QWidget()
        right_container_widget.setLayout(self.right_section_layout)
        self.main_layout.addWidget(right_container_widget)

        self.membersFilterButton = QSvgWidget(resource_path("assets/images/filter_white.svg"), self.members_toolbar)
        self.membersFilterButton.setObjectName("membersFilterButton")
        self.membersFilterButton.setStyleSheet("border-color: transparent; background-color: transparent;")
        self.membersFilterButton.setFixedSize(20, 20)
        self.membersFilterButton.move(self.members_toolbar.width() - self.membersFilterButton.width() - 10, configsHeight//2 - self.membersFilterButton.height()//2)        
        self.membersFilterButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.membersFilterButton.mousePressEvent = lambda event: self.toggle_members_filter()

        memberConfigsContainer = QtWidgets.QWidget()
        memberConfigsContainer.setStyleSheet(f"background-color: {containerColor};")
        self.main_layout.addWidget(memberConfigsContainer)

        self.configs_division = QtWidgets.QFrame(self.members_toolbar)
        self.configs_division.setGeometry(
            self.members_toolbar.width() - 6, 
            int(self.members_toolbar.height()*0.2),
            2,
            int(self.members_toolbar.height()*0.6)
        )
        self.configs_division.setStyleSheet(f"background-color: {contrastColor};")
        self.configs_division.raise_()

        self.members_filter_container = QtWidgets.QWidget(self)
        self.members_filter_container.setObjectName("members_filter_container")
        self.members_filter_container.setStyleSheet(f" #members_filter_container {{ background-color: {backgroundColor}; border-radius: 4px; border-color: white; border-style: solid; border-width: 0px 0px 1px 1px; }}")
        self.members_filter_container.setFixedSize(170, 170)
        self.members_filter_container.move(self.navBar.width() + self.middle_section.width() - self.members_filter_container.width(), configsHeight)
        self.members_filter_container.hide()

        # Layout for the filter container
        self.members_filter_layout = QtWidgets.QVBoxLayout(self.members_filter_container)
        self.members_filter_layout.setContentsMargins(0, 0, 0, 0)
        self.members_filter_layout.setSpacing(0)

        # Add content to the filter container
        self.membersCheckboxContainer = QtWidgets.QWidget()
        self.membersCheckboxContainer.setStyleSheet("#membersCheckboxContainer { border-width: 0 0 1px 1px; border-radius: 5px; border-style: solid; border-color: white; }")
        self.membersCheckboxContainer.setFixedSize(200, 170)
        self.members_filter_layout.addWidget(self.membersCheckboxContainer)

        self.members_display_filters_label = QtWidgets.QLabel("Filtros de exibição", self.membersCheckboxContainer)
        self.members_display_filters_label.setObjectName("members_display_filters_label")

        self.show_offline = QtWidgets.QCheckBox(self.membersCheckboxContainer)
        self.show_offline.setStyleSheet("border: none;")
        self.show_offline.setText("Mostrar inativos")
        self.show_offline.setObjectName("show_offline")
        self.show_offline.mousePressEvent = lambda event: self.toggle_members_checkboxes(self.show_offline)
        self.show_offline.setChecked(True)

        self.show_admins = QtWidgets.QCheckBox(self.membersCheckboxContainer)
        self.show_admins.setStyleSheet("border: none;")
        self.show_admins.setText("Mostrar admins")
        self.show_admins.setObjectName("show_admins")
        self.show_admins.mousePressEvent = lambda event: self.toggle_members_checkboxes(self.show_admins)
        self.show_admins.setChecked(True)

        self.admins_first = QtWidgets.QCheckBox(self.membersCheckboxContainer)
        self.admins_first.setStyleSheet("border: none;")
        self.admins_first.setText("Admins primeiro")
        self.admins_first.setObjectName("admins_first")
        self.admins_first.mousePressEvent = lambda event: self.toggle_members_checkboxes(self.admins_first)
        self.admins_first.setChecked(True)

        self.search_filter_label = QtWidgets.QLabel("Pesquisar por", self.membersCheckboxContainer)
        self.search_filter_label.setObjectName("search_filter_label")

        self.members_by_name_filter = QtWidgets.QCheckBox(self.membersCheckboxContainer)
        self.members_by_name_filter.setText("Nickname")
        self.members_by_name_filter.setObjectName("members_by_name_filter")
        self.members_by_name_filter.mousePressEvent = lambda event: self.toggle_search_filter(self.members_by_name_filter)
        self.members_by_name_filter.setChecked(True)

        self.members_by_motto_filter = QtWidgets.QCheckBox(self.membersCheckboxContainer)
        self.members_by_motto_filter.setText("Missão")
        self.members_by_motto_filter.setObjectName("members_by_motto_filter")
        self.members_by_motto_filter.mousePressEvent = lambda event: self.toggle_search_filter(self.members_by_motto_filter)
        self.members_by_motto_filter.setChecked(False)

        next_members_filter_pos = 10
        
        self.members_display_filters_label.move(15, next_members_filter_pos)
        next_members_filter_pos += 20

        self.show_offline.move(15 + 10, next_members_filter_pos)
        next_members_filter_pos += 20
        
        self.show_admins.move(15 + 10, next_members_filter_pos)
        next_members_filter_pos += 20
        
        self.admins_first.move(15 + 10 + 10, next_members_filter_pos)
        next_members_filter_pos += 30
        
        self.search_filter_label.move(15, next_members_filter_pos)
        next_members_filter_pos += 20
        
        self.members_by_name_filter.move(15 + 10, next_members_filter_pos)
        next_members_filter_pos += 20
        
        self.members_by_motto_filter.move(15 + 10, next_members_filter_pos)
        next_members_filter_pos += 20

        self.changesFilterButton = QSvgWidget(resource_path("assets/images/filter_white.svg"), self.changes_toolbar)
        self.changesFilterButton.setObjectName("changesFilterButton")
        self.changesFilterButton.setStyleSheet("border-color: transparent; background-color: transparent")
        self.changesFilterButton.setFixedSize(20, 20)
        self.changesFilterButton.move(self.changes_toolbar.width() - self.refreshButton.width() - 10 - self.changesFilterButton.width() - 10, configsHeight//2 - self.changesFilterButton.height()//2)        
        self.changesFilterButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.changesFilterButton.mousePressEvent = lambda event: self.toggle_changes_filter()

        self.changes_filter_container = QtWidgets.QWidget(self)
        self.changes_filter_container.setObjectName("changes_filter_container")
        self.changes_filter_container.setStyleSheet(f" #changes_filter_container {{ background-color: {backgroundColor}; border-radius: 4px; border-color: white; border-style: solid; border-width: 0px 0px 1px 1px; }}")
        self.changes_filter_container.setFixedSize(170, 130)
        self.changes_filter_container.move(self.width() - self.changes_filter_container.width(), configsHeight)        
        self.changes_filter_container.hide()

        # Layout for the filter container
        self.changes_filter_layout = QtWidgets.QVBoxLayout(self.changes_filter_container)
        self.changes_filter_layout.setContentsMargins(0, 0, 0, 0)
        self.changes_filter_layout.setSpacing(0)

        # Add content to the filter container
        self.changesCheckboxContainer = QtWidgets.QWidget()
        self.changesCheckboxContainer.setStyleSheet("#changesCheckboxContainer { border-width: 0 0 1px 1px; border-radius: 5px; border-style: solid; border-color: white; }")
        self.changesCheckboxContainer.setFixedSize(200, 140)
        self.changes_filter_layout.addWidget(self.changesCheckboxContainer)

        self.changes_display_filters_label = QtWidgets.QLabel("Mostrar", self.changesCheckboxContainer)
        self.changes_display_filters_label.setObjectName("changes_display_filters_label")


        self.joined_filter = QtWidgets.QCheckBox(self.changesCheckboxContainer)
        self.joined_filter.setText("Entradas")
        self.joined_filter.setObjectName("joined_filter")
        self.joined_filter.mousePressEvent = lambda event: self.toggle_changes_checkboxes(self.joined_filter)
        self.joined_filter.setChecked(True)

        self.left_filter = QtWidgets.QCheckBox(self.changesCheckboxContainer)
        self.left_filter.setText("Saídas")
        self.left_filter.setObjectName("left_filter")
        self.left_filter.mousePressEvent = lambda event: self.toggle_changes_checkboxes(self.left_filter)
        self.left_filter.setChecked(True)

        self.turned_adm_filter = QtWidgets.QCheckBox(self.changesCheckboxContainer)
        self.turned_adm_filter.setText("Recebeu admin")
        self.turned_adm_filter.setObjectName("turned_adm_filter")
        self.turned_adm_filter.mousePressEvent = lambda event: self.toggle_changes_checkboxes(self.turned_adm_filter)
        self.turned_adm_filter.setChecked(True)

        self.lost_adm_filter = QtWidgets.QCheckBox(self.changesCheckboxContainer)
        self.lost_adm_filter.setText("Perdeu admin")
        self.lost_adm_filter.setObjectName("lost_adm_filter")
        self.lost_adm_filter.mousePressEvent = lambda event: self.toggle_changes_checkboxes(self.lost_adm_filter)
        self.lost_adm_filter.setChecked(True)

        self.joined_filter.setParent(self.changesCheckboxContainer)
        self.left_filter.setParent(self.changesCheckboxContainer)
        self.turned_adm_filter.setParent(self.changesCheckboxContainer)
        self.lost_adm_filter.setParent(self.changesCheckboxContainer)

        next_changes_filter_pos = 10

        self.changes_display_filters_label.move(15, next_changes_filter_pos)
        next_changes_filter_pos += 20

        self.joined_filter.move(15 + 10, next_changes_filter_pos)
        next_changes_filter_pos += 20

        self.left_filter.move(15 + 10, next_changes_filter_pos)
        next_changes_filter_pos += 20

        self.turned_adm_filter.move(15 + 10, next_changes_filter_pos)
        next_changes_filter_pos += 20

        self.lost_adm_filter.move(15 + 10, next_changes_filter_pos)
        next_changes_filter_pos += 20

        self.init_group(self.groups[find_group_index(initial_group)], initial_group)

        self.show()


    def init_group(self, group, group_name):
        self.clear_layout(self.middle_layout)
        self.clear_layout(self.right_layout)
        for g in self.groups:
            g.setStyleSheet(f"""
                QLabel {{
                    background-color: {backgroundColor};
                    padding: 15px;  
                }}
                QLabel:hover {{
                    background-color: {containerColor};
                }}
            """)

        group.setStyleSheet(f"""
            QLabel {{
                background-color: {containerColor};
                padding: 15px;  
            }}
            """)
        self.load_group_members(group_name)
        self.load_changes(group_name)

    def select_group(self, group, group_name):
        self.clear_layout(self.middle_layout)
        self.clear_layout(self.right_layout)
        for g in self.groups:
            g.setStyleSheet(f"""
                QLabel {{
                    background-color: {backgroundColor};
                    padding: 15px;  
                }}
                QLabel:hover {{
                    background-color: {containerColor};
                }}
            """)

        group.setStyleSheet(f"""
            QLabel {{
                background-color: {containerColor};
                padding: 15px;  
            }}
            """)
        self.reset_group_config()
        self.reset_changes_config()
        self.load_group_members(group_name)
        self.load_changes(group_name)
        self.load_tracker.setText(f"Último carregamento em: {get_formatted_datetime_now()}")
        self.search("members")
        self.search("changes")

    def refresh_group_members(self, group):
        self.reset_group_config()
        self.load_group_members(group)

    def refresh_changes(self, group):
        self.reset_changes_config()
        self.load_changes(group)

    def toggle_members_checkboxes(self, widget):
        widget.setChecked(not widget.isChecked())
        if widget == self.show_admins:
            self.admins_first.setEnabled(self.show_admins.isChecked())
            
        self.refresh_group_members(self.current_group)

    def toggle_changes_checkboxes(self, widget):
        widget.setChecked(not widget.isChecked())
        self.refresh_changes(self.current_group)


    def toggle_search_filter(self, widget):
        if widget == self.members_by_name_filter:
            s = "user_name"
        if widget == self.members_by_motto_filter:
            s = "motto"
        if widget.isChecked():
            widget.setChecked(False)
            if s in self.members_filter:
                self.members_filter.remove(s)
        else:
            widget.setChecked(True)
            if s not in self.members_filter:
                self.members_filter.append(s)  

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout is not None:
                    self.clear_layout(sub_layout)
    
    def reset_group_config(self):
        configsHeight = self.height() * 0.1
        self.membersSearchWidget.hide()
        self.groupMembersContainer.deleteLater()
        for member in self.current_members:
            member.deleteLater()
        self.current_members = []

    def reset_changes_config(self):
        for change in self.current_changes:
            change.deleteLater()
        self.current_changes = []

    def load_group_members(self, group):
        membersWidth = int(self.middle_section.width())
        configsHeight = int(self.height() * 0.1)
        
        self.current_group = group
        self.current_members = []

        members_data = self.consult_group(group)

        displayed_length = len(members_data) if len(members_data) < 1000 else "999+"
        s = "s" if len(members_data) != 1 else ""
        self.displayedLengthLabel.setText(f"{displayed_length} membro{s} sendo exibido{s}")
        self.displayedLengthLabel.adjustSize()
        self.displayedLengthLabel.move(10, int(configsHeight/2) + 5)

        self.groupNameLabel.setText(groups[find_group_index(group)][3])
        self.groupNameLabel.adjustSize()
        self.groupNameLabel.move(5, int(configsHeight/2 - self.groupNameLabel.height()))

        self.start_of_searchbar = self.displayedLengthLabel.width() if self.displayedLengthLabel.width() > self.groupNameLabel.width() else self.groupNameLabel.width()
        self.start_of_searchbar += 20 if self.width() >= 450 else 0

        self.membersSearchWidget.move(
            self.start_of_searchbar, 
            self.members_toolbar.height()//2 - self.membersSearchWidget.height()//2
        )
        self.membersSearchWidget.show()

        # Create a vertical layout for the group members
        self.groupMembersLayout = QtWidgets.QVBoxLayout()
        self.groupMembersLayout.setContentsMargins(0, 0, 0, 0)
        self.groupMembersLayout.setSpacing(10)
        # self.groupMembersLayout.addStretch()

        # Create a container widget for the layout
        self.groupMembersContainer = QtWidgets.QWidget()
        self.groupMembersContainer.setLayout(self.groupMembersLayout)
        self.groupMembersContainer.setStyleSheet(f"background-color: {containerColor};")
        self.main_layout.addWidget(self.groupMembersContainer)

        for i, member in enumerate(members_data):
            self.current_font.setPointSize(14)

            container = QtWidgets.QFrame(self.groupMembersContainer)
            container.setObjectName("memberContainer")
            container.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
            container.setStyleSheet("background-color: " + containerColor + ";")
            container.setFixedHeight(memberHeight)

            user_image = QtWidgets.QLabel(container)
            user_image.setGeometry(QtCore.QRect(15, 5, 70, 70))
            user_image.setPixmap(QtGui.QPixmap(resource_path('assets/images/user_white.png')))
            user_image.setScaledContents(True)
            user_image.setObjectName("userImg" + str(i))

            user_name = QtWidgets.QLabel(container)
            user_name.setObjectName("user_name")
            user_name.move(100, 10)
            user_name.setFont(self.current_font)
            user_name.setText(member['name'])
            user_name.setStyleSheet("color: #ffffff;")
            user_name.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

            self.current_font.setBold(False)
            self.current_font.setPointSize(11)
            motto = QtWidgets.QLabel(container)
            motto.setObjectName("motto")
            motto.setGeometry(100, 40, 400, 30)
            motto.setFont(self.current_font)
            motto.setStyleSheet("color: #c7c7c7;")
            motto_text = member['motto'].replace('†', '💣').replace('ª', '💀').replace('º', '⚡')
            motto.setText(motto_text)

            adm_crown_x = 100 + user_name.sizeHint().width() + 10
            adm_crown_width = 0
            if member['isAdmin']:
                adm_crown_img = QSvgWidget(resource_path('assets/images/adm.svg'), container)
                adm_crown_img.setGeometry(QtCore.QRect(adm_crown_x, 12, 20, 20))
                adm_crown_img.setObjectName("admImg" + str(i))
                adm_crown_width = adm_crown_img.width()
            
            if member['online']:
                online_img = QSvgWidget(resource_path('assets/images/online.svg'), container)
                online_img.setGeometry(QtCore.QRect(adm_crown_x + adm_crown_width + 10, 17, 10, 10))
                online_img.setObjectName("onlineImg" + str(i))

            self.current_members.append(container)
            self.middle_layout.addWidget(container)

        self.middle_layout.addStretch()
        

    def consult_group(self, group):
        members_data = get_group_members(group) # Involves a request to the server
        if members_data is not None:
            if not self.show_offline.isChecked():
                members_data = [member for member in members_data if (member['online'])]
            if not self.show_admins.isChecked():
                members_data = [member for member in members_data if not (member['isAdmin'])]
            if self.admins_first.isChecked():
                members_data = sorted(members_data, key=lambda x: x['isAdmin'], reverse=True)
        return members_data
    
    def consult_changes(self, group):
        changes_data = get_group_changes(group) # Involves a request to the server
        if changes_data is not None:
            if not self.joined_filter.isChecked():
                changes_data = [change for change in changes_data if not change['action'] == 'entrou']
            if not self.left_filter.isChecked():
                changes_data = [change for change in changes_data if not 'saiu' in change['action']]
            if not self.turned_adm_filter.isChecked():
                changes_data = [change for change in changes_data if not change['action'] == 'tornou-se admin']
            if not self.lost_adm_filter.isChecked():
                changes_data = [change for change in changes_data if not change['action'] == 'perdeu admin']
        return changes_data

    def load_changes(self, group):
        changesWidth = int(self.right_section.width())
        self.current_changes = []
        changes_data = self.consult_changes(group)
        
        def get_datetime(change):
            return datetime.strptime(f"{change['date']} {change['time']}", "%Y-%m-%d %H:%M:%S")

        # Ordenar changes_data com base no valor datetime, do mais recente para o mais antigo
        changes_data.sort(key=get_datetime, reverse=True)

        if changes_data:
            for i in range(len(changes_data)):
                change = changes_data[i]
                # Container dos dados
                container = QtWidgets.QFrame()
                container.setObjectName("changeContainer")
                container.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
                container.setFixedSize(changesWidth, changeHeight)
                container.setStyleSheet("background-color: " + containerColor + ";")

                self.current_font.setPointSize(11)
                change_img_path = "assets/images/"
                action = change['action']
                if action == 'entrou':
                    change_img_path += "joined_green.svg"
                if action == 'saiu':
                    change_img_path += "left_red.svg"
                if action == 'saiu offline':
                    change_img_path += "left_offline.svg"
                if action == 'tornou-se admin':
                    change_img_path += "turned_adm.svg"
                if action == 'perdeu admin':
                    change_img_path += "lost_adm.svg"

                changeImg = QSvgWidget(resource_path(change_img_path), container)
                changeImg.setObjectName("changeImg")
                changeImg.setFixedSize(45, 45)
                changeImg.move(container.width() // 20, 15)
                # Espaço destinado ao nome do membro
                change_nickname = change['name']
                changeName = QtWidgets.QLabel(container)
                changeName.setTextFormat(Qt.TextFormat.RichText)
                changeName.setObjectName("changeName")
                self.current_font.setBold(True)
                changeName.setFont(self.current_font)
                changeName.setText(change_nickname) # {action}')
                changeName.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                changeName.move(container.width() // 20 + 45 + 20, int(15 + (45)/2 - changeName.height()/2))

                changeAction = QtWidgets.QLabel(container)
                changeAction.setObjectName("changeAction")
                self.current_font.setBold(False)
                changeAction.setFont(self.current_font)
                changeAction.setText(action)
                changeAction.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                changeAction.move(changeName.pos().x() + changeName.sizeHint().width() + 5, changeName.pos().y())
                
                # Data da change
                self.current_font.setPointSize(11)
                datetimeLabel = QtWidgets.QLabel(container)
                datetimeLabel.setGeometry(container.width() // 20, container.height() - 30, container.width(), 30)
                datetimeLabel.setFont(self.current_font)
                datetimeLabel.setStyleSheet("color: #c7c7c7;")

                year = change['date'][0:4]
                month = date_displays[int(change['date'][5:7]) - 1]
                day = change['date'][8:10]
                time = change['time']

                datetimeLabel.setText(f'{day} {month} {year} - {time}')

                view_admlog = QSvgWidget(resource_path('assets/images/view_admlog.svg'), container)
                view_admlog.setObjectName("view_admlog")
                view_admlog.setFixedSize(25, 25)
                view_admlog.move(
                    container.width() - view_admlog.width() - 40, 
                    int(changeHeight/2 - view_admlog.height()/2)
                )
                
                change['timestamp'] = f"{change['date'][:4]}-{change['date'][5:7]}-{change['date'][8:10]} - {change['time']}"
                view_admlog.enterEvent = lambda event, w=view_admlog, timestamp=change['timestamp']: self.show_admlog(w, self.current_group, timestamp)
                view_admlog.leaveEvent = lambda event, w=view_admlog: w.load(resource_path('assets/images/view_admlog.svg'))
                view_admlog.mousePressEvent = lambda event, w=view_admlog, timestamp=change['timestamp']: self.copy_admlog(w, timestamp)
                
                self.current_changes.append(container)
                self.right_layout.addWidget(container)
            
            self.right_layout.addStretch()
        
        return True if changes_data else False
    
    def show_admlog(self, widget, group_name, timestamp):
        widget.load(resource_path('assets/images/copy.svg'))
        if not (hasattr(widget, 'admlog')):
            widget.admlog = get_admlog(group_name, timestamp)
            if widget.admlog:
                admlog_text = "\n".join(["Admins ativos:\n"] + widget.admlog)
            else:
                admlog_text = "Sem registro de admins."
            tooltip = QtWidgets.QToolTip
            self.current_font.setBold(False)
            tooltip.setFont(self.current_font)
            self.current_font.setBold(True)
            widget.setToolTip(admlog_text)
            widget.setToolTipDuration(0)  # Tooltip will stay until the mouse leaves the widget
        widget.show()

    def copy_admlog(self, widget, timestamp):
        if hasattr(widget, 'admlog'):
            admlog_text = "\n".join(widget.admlog)
            admlog_text = admlog_text.replace("Admins ativos:\n", "")
            admlog_text = generate_clipboard_text(groups[find_group_index(self.current_group)][2], admlog_text, timestamp)
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(admlog_text)
            widget.load(resource_path('assets/images/check.svg'))
    
    def toggle_members_filter(self):
        if self.members_filter_container.isVisible():
            self.members_filter_container.hide()
        else:
            self.members_filter_container.raise_()
            self.members_filter_container.show()

    def toggle_changes_filter(self):
        if self.changes_filter_container.isVisible():
            self.changes_filter_container.hide()
        else:
            self.changes_filter_container.raise_()
            self.changes_filter_container.show()

    def style_scroll_bar(self, scroll_bar):
        scroll_bar.setStyleSheet(f"""
    QScrollBar:vertical {{
        border: none;
        background: #1b1b1b;
        width: 10px;
    }}
    QScrollBar::handle:vertical {{
        background: #3e3e3e;
        min-height: 20px;
        border-radius: 3px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        background: none;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}
    """)
        
    def search(self, items_type):
        if items_type == "members":
            prompt = self.membersSearchWidget.searchBar.text()
            self.searched_members = self.match_nicknames(prompt, self.current_members, self.members_filter)
            self.highlight_results(self.searched_members)
            self.searched_highlighted_member_index = 0
            self.highlight_selected_result(0, "members")
            self.members_filter_container.raise_()
        if items_type == "changes":
            prompt = self.changesSearchWidget.searchBar.text()
            self.searched_changes = self.match_nicknames(prompt, self.current_changes, self.changes_filter)
            self.highlight_results(self.searched_changes)
            self.searched_highlighted_change_index = 0
            self.highlight_selected_result(0, "changes")
            self.changes_filter_container.raise_()

    def match_nicknames(self, prompt, lst, attributes):
        results = []
        if prompt == '':
            return results
        for container in lst:
            flag = 0
            if attributes:
                for attr in attributes:
                    if prompt.lower() in container.findChild(QtWidgets.QWidget, attr).text().lower():
                        flag = 1
                        results.append(container)
                        break
            if not flag:
                container.setStyleSheet("background-color: " + containerColor + ";")
        return results
        
    def highlight_results(self, results):
        for result in results:
            result.setStyleSheet("background-color: " + searchHighlightedColor + ";")

    def highlight_selected_result(self, step, search_type):
        if search_type == "members":
            scroll_area = self.middle_scroll_area
            container = self.members_toolbar
            current_items = self.current_members
            searched_items = self.searched_members
            searched_highlighted_index = self.searched_highlighted_member_index
            container_height = memberHeight
            list_is_reversed = False

        if search_type == "changes":
            scroll_area = self.right_scroll_area
            container = self.changes_toolbar
            current_items = self.current_changes
            searched_items = self.searched_changes
            searched_highlighted_index = self.searched_highlighted_change_index
            container_height = changeHeight
            list_is_reversed = True

        results_tracker = container.findChild(QtWidgets.QLabel, "resultsTracker")
        next_button = container.findChild(QSvgWidget, "nextButton")
        back_button = container.findChild(QSvgWidget, "backButton")

        if searched_items != []:
            if searched_highlighted_index + step == len(searched_items):
                new_shi = 0
            elif searched_highlighted_index + step < 0:
                new_shi = len(searched_items) - 1
            else:
                new_shi = searched_highlighted_index + step

            searched_items[searched_highlighted_index].setStyleSheet("background-color: " + searchHighlightedColor + ";")
            searched_items[new_shi].setStyleSheet("background-color: " + searchSelectedHighlightedColor + ";")

            index_in_items = current_items.index(searched_items[new_shi])

            container_required_height = container_height + defaultSpacing
            y_position = index_in_items * container_required_height

            scroll_area.verticalScrollBar().setValue(y_position)
            scroll_area.update()
            scroll_area.viewport().update()

            if search_type == "members":
                self.searched_highlighted_member_index = new_shi
            elif search_type == "changes":
                self.searched_highlighted_change_index = new_shi

            searched_highlighted_index = new_shi

            results_tracker.setStyleSheet("color: " + fontcolor + ";")
            
            displayed_length = str(len(searched_items)) if len(searched_items) < 1000 else "999+"

            results_tracker.setText(str(new_shi + 1) + " de " + displayed_length)
            next_button.load(resource_path('assets/images/down_arrow_white.svg'))
            back_button.load(resource_path('assets/images/up_arrow_white.svg'))
        else:
            displayed_length = str(len(current_items)) if len(current_items) < 1000 else "999+"
            # results_tracker.setStyleSheet("color: #d96868;")
            for item in current_items: item.setStyleSheet(f"background-color: {containerColor};")
            results_tracker.setText("---")
            next_button.load(resource_path('assets/images/down_arrow_disabled.svg'))
            back_button.load(resource_path('assets/images/up_arrow_disabled.svg'))

    def eventFilter(self, source, event):
        if hasattr(self, 'membersSearchWidget'):
            membersSearchBar = self.membersSearchWidget.findChild(QtWidgets.QLineEdit, 'searchBar')
        if hasattr(self, 'changesSearchWidget'):
            changesSearchBar = self.changesSearchWidget.findChild(QtWidgets.QLineEdit, 'searchBar')
        if (event.type() == QtCore.QEvent.Type.KeyPress):
            if (event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter):
                if source is membersSearchBar:
                    items_type = "members"
                if source is changesSearchBar:
                    items_type = "changes"

                if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                    self.highlight_selected_result(-1, items_type)
                else:
                    self.highlight_selected_result(1, items_type)
            if (event.key() == Qt.Key.Key_F and event.modifiers() == Qt.KeyboardModifier.ControlModifier):
                if source is membersSearchBar:
                    self.changesSearchBar.setFocus()
                elif source is changesSearchBar:
                    self.membersSearchBar.setFocus()
                else:
                    self.membersSearchBar.setFocus()
        return False

    def mousePressEvent(self, event):
        border_width = 20  # Width of the border area where resizing is allowed
        rect = self.rect()
        rect.setWidth(rect.width() - border_width)
        rect.setHeight(rect.height() - border_width)
        if event.button() == Qt.MouseButton.LeftButton and not rect.contains(event.pos()):
            self.resizing = True
            self.oldPos = event.globalPosition().toPoint()
            event.accept()
        else:
            self.resizing = False

    def mouseMoveEvent(self, event):
        border_width = 20  # Width of the border area where resizing is allowed
        rect = self.rect()
        rect.setWidth(rect.width() - border_width)
        rect.setHeight(rect.height() - border_width)
        
        if event.buttons() == Qt.MouseButton.LeftButton and self.resizing:
            delta = event.globalPosition().toPoint() - self.oldPos
            self.resize(self.width() + delta.x(), self.height() + delta.y())
            self.oldPos = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.resizing = False
            event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_size_x = self.width()
        new_size_y = self.height()
        groups_size = int(new_size_x * 0.1) if new_size_x < 1130 else int(1130 * 0.1)
        for group in self.groups:
            self.centralWidget().layout().itemAt(0).widget().setFixedWidth(groups_size)
            group.setFixedWidth(groups_size)
            group.setFixedHeight(groups_size)
        configsHeight = int(new_size_y * 0.1)
        new_members_width = int(new_size_x * 0.5)
        new_changes_width = new_size_x - new_members_width - self.groups[0].width()
        members_section = self.centralWidget().layout().itemAt(1).widget()
        changes_section = self.centralWidget().layout().itemAt(2).widget()
        members_section.setFixedWidth(new_members_width)
        changes_section.setFixedWidth(new_changes_width)
        self.middle_section.setFixedWidth(new_members_width)

        for container in self.current_members:
            container.setFixedWidth(new_members_width)

        for container in self.current_changes:
            container.setFixedSize(new_changes_width, changeHeight)

        if members_section.width() < 550:
            self.membersSearchWidget.nextButton.hide()
            self.membersSearchWidget.backButton.hide()
        else:
            self.membersSearchWidget.nextButton.show()
            self.membersSearchWidget.backButton.show()
        if members_section.width() < 480:
            self.membersSearchWidget.resultsTracker.hide()
        else:
            self.membersSearchWidget.resultsTracker.show()

        if members_section.width() < 450:
            self.membersSearchWidget.searchBar.setFixedWidth(70)
        elif members_section.width() >= 420:
            self.membersSearchWidget.searchBar.setFixedWidth(130)
        if changes_section.width() < 390:
            self.membersSearchWidget.move(self.start_of_searchbar - 20, self.membersSearchWidget.pos().y())
            for container in self.current_changes:
                change_action = container.findChild(QtWidgets.QLabel, "changeAction")
                if change_action:
                    change_name = container.findChild(QtWidgets.QLabel, "changeName")
                    change_action.move(change_name.pos().x(), change_name.y() + 25)
        elif changes_section.width() >= 390:
            self.membersSearchWidget.move(self.start_of_searchbar, self.membersSearchWidget.pos().y())
            for container in self.current_changes:
                change_action = container.findChild(QtWidgets.QLabel, "changeAction")
                if change_action:
                    change_name = container.findChild(QtWidgets.QLabel, "changeName")
                    change_action.move(change_name.pos().x() + change_name.sizeHint().width() + 5, change_name.y())
        if new_changes_width < 425:
            self.changesSearchWidget.nextButton.hide()
            self.changesSearchWidget.backButton.hide()
        else:
            self.changesSearchWidget.nextButton.show()
            self.changesSearchWidget.backButton.show()

        if new_changes_width < 380:
            self.changesSearchWidget.resultsTracker.hide()
        else:
            self.changesSearchWidget.resultsTracker.show()

        if new_changes_width < 300:
            self.changesSearchWidget.searchBar.setFixedWidth(100)
        else:
            self.changesSearchWidget.searchBar.setFixedWidth(120)

        self.membersSearchWidget.move(self.membersSearchWidget.pos().x(), configsHeight//2 - self.membersSearchWidget.height()//2)
        self.changesSearchWidget.move(self.changesSearchWidget.pos().x(), configsHeight//2 - self.changesSearchWidget.height()//2)
        self.members_toolbar.setFixedSize(members_section.width(), configsHeight)
        self.membersFilterButton.move(self.members_toolbar.width() - self.membersFilterButton.width()//2 - 30, configsHeight//2 - self.membersFilterButton.height()//2)
        self.configs_division.move(
            self.members_toolbar.width() - 6, 
            int(self.members_toolbar.height()*0.2)
        )
        self.changes_toolbar.setFixedHeight(configsHeight)
        self.changes_label.move(5, int(configsHeight/2 - self.changes_label.height()/2))
        self.groupNameLabel.move(5, int(configsHeight/2 - self.groupNameLabel.height()))
        self.displayedLengthLabel.move(10, int(configsHeight/2 + 5))

        new_changes_width = new_size_x - self.groups[0].width() - members_section.width()
        self.changes_toolbar.setFixedWidth(new_changes_width)
        self.refreshButton.move(new_changes_width - 30, int(configsHeight/2 - self.refreshButton.height()/2))  
        self.changesFilterButton.move(self.changes_toolbar.width() - self.refreshButton.width() - 10 - self.changesFilterButton.width() - 10, configsHeight//2 - self.changesFilterButton.height()//2)   
        changes_section.setFixedWidth(new_changes_width)
        self.members_filter_container.move(self.groups[0].width() + self.middle_section.width() - self.members_filter_container.width(), menuBarHeight + configsHeight)
        self.changes_filter_container.move(self.width() - self.changes_filter_container.width(), menuBarHeight + configsHeight)        
        self.title_bar.setFixedWidth(new_size_x)
        
        for container in self.current_changes:
            container.setFixedWidth(new_changes_width)
            view_admlog = container.findChild(QSvgWidget, "view_admlog")
            if view_admlog:
                view_admlog.move(
                    container.width() - view_admlog.width() - 40, 
                    int(changeHeight / 2 - view_admlog.height() / 2)
                )

        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow("acesso_a_base")
    sys.exit(app.exec())