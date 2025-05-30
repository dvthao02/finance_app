from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QFrame, QStackedWidget,
                             QPushButton, QLabel, QScrollArea, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from finance_app.gui.base.base_form import BaseForm
from finance_app.gui.base.base_widget import BaseWidget
import os

class BaseDashboard(BaseForm, BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_user = None
        self.current_user_id = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dashboard UI"""
        # Setup window properties
        self.setup_window("Dashboard")
        
        # Create main horizontal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = self.create_sidebar()
        layout.addWidget(self.sidebar)
        
        # Create main content area
        self.content_area = self.create_content_area()
        layout.addWidget(self.content_area)
        
        # Set the layout
        self.main_layout.addLayout(layout)
        
    def create_sidebar(self):
        """Create the sidebar"""
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-right: 1px solid #e0e0e0;
            }
        """)
        
        # Create sidebar layout
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Add header
        header = self.create_sidebar_header()
        sidebar_layout.addWidget(header)
        
        # Create navigation buttons container
        nav_container = QWidget()
        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        
        # Add navigation buttons
        self.nav_buttons = {}
        for item in self.get_nav_items():
            btn = self.create_nav_button(item['text'], item['icon'])
            btn.clicked.connect(lambda checked, page=item['page']: self.show_page(page))
            self.nav_buttons[item['page']] = btn
            nav_layout.addWidget(btn)
            
        nav_layout.addStretch()
        nav_container.setLayout(nav_layout)
        
        # Add scrollable navigation
        scroll = QScrollArea()
        scroll.setWidget(nav_container)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sidebar_layout.addWidget(scroll)
        
        # Add logout button
        logout_btn = QPushButton("Đăng xuất")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #d93025;
                font-size: 14px;
                font-weight: bold;
                padding: 15px 20px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #fce8e6;
            }
        """)
        logout_btn.clicked.connect(self.handle_logout)
        sidebar_layout.addWidget(logout_btn)
        
        sidebar.setLayout(sidebar_layout)
        return sidebar
        
    def create_sidebar_header(self):
        """Create the sidebar header"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #1a73e8;
                padding: 20px;
            }
        """)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add logo
        logo_label = QLabel()
        logo_path = self.get_asset_path('logo_white.png')
        if os.path.exists(logo_path):
            logo_label.setPixmap(QIcon(logo_path).pixmap(32, 32))
            
        # Add title
        title = QLabel(self.get_dashboard_title())
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                margin-left: 10px;
            }
        """)
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header.setLayout(header_layout)
        
        return header
        
    def create_content_area(self):
        """Create the main content area"""
        content_area = QFrame()
        content_area.setStyleSheet("""
            QFrame {
                background-color: #f5f6f7;
            }
        """)
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # Create stacked widget for different pages
        self.stack = QStackedWidget()
        
        # Create pages
        self.create_pages()
        
        content_layout.addWidget(self.stack)
        content_area.setLayout(content_layout)
        
        return content_area
        
    def create_nav_button(self, text, icon_name=None):
        """Create a navigation button
        
        Args:
            text (str): Button text
            icon_name (str, optional): Icon file name
        """
        btn = QPushButton(text)
        btn.setCheckable(True)
        
        if icon_name:
            icon_path = self.get_asset_path(icon_name)
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
                
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 0;
                color: #5f6368;
                font-size: 14px;
                font-weight: bold;
                padding: 15px 20px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #f1f3f4;
                color: #1a73e8;
            }
            QPushButton:checked {
                background-color: #e8f0fe;
                color: #1a73e8;
                border-left: 4px solid #1a73e8;
            }
        """)
        
        return btn
        
    def show_page(self, page_name):
        """Show the selected page and update navigation buttons
        
        Args:
            page_name (str): Name of the page to show
        """
        # Uncheck all buttons
        for btn in self.nav_buttons.values():
            btn.setChecked(False)
            
        # Check the selected button and show page
        if page_name in self.nav_buttons:
            self.nav_buttons[page_name].setChecked(True)
            page_index = list(self.nav_buttons.keys()).index(page_name)
            self.stack.setCurrentIndex(page_index)
            
    def set_current_user(self, user_data):
        """Set the current user and load their data
        
        Args:
            user_data (dict): Dictionary containing user information
        """
        self.current_user = user_data
        if user_data:
            self.current_user_id = user_data.get('user_id')
        else:
            self.current_user_id = None
        self.refresh_data()
        
    def handle_logout(self):
        """Handle user logout"""
        self.current_user = None
        self.current_user_id = None
        if self.parent:
            self.parent.show_login_frame()
            
    def refresh_data(self):
        """Refresh dashboard data"""
        pass
        
    def get_nav_items(self):
        """Get navigation items
        
        Returns:
            list: List of dictionaries containing navigation items
        """
        return []
        
    def create_pages(self):
        """Create dashboard pages"""
        pass
        
    def get_dashboard_title(self):
        """Get dashboard title
        
        Returns:
            str: Dashboard title
        """
        return "Dashboard" 