from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QSpacerItem,
                             QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
import os

class BaseWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
    def create_title_label(self, text, size=24, bold=True):
        """Create a title label
        
        Args:
            text (str): Label text
            size (int): Font size
            bold (bool): Whether to use bold font
        """
        label = QLabel(text)
        font = QFont("Arial", size)
        font.setBold(bold)
        label.setFont(font)
        label.setStyleSheet("color: #202124;")
        return label
        
    def create_input_field(self, placeholder="", password=False):
        """Create an input field
        
        Args:
            placeholder (str): Placeholder text
            password (bool): Whether this is a password field
        """
        input_field = QLineEdit()
        input_field.setMinimumHeight(45)
        input_field.setPlaceholderText(placeholder)
        if password:
            input_field.setEchoMode(QLineEdit.Password)
            
        input_field.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
            }
        """)
        return input_field
        
    def create_primary_button(self, text, height=45):
        """Create a primary button
        
        Args:
            text (str): Button text
            height (int): Button height
        """
        button = QPushButton(text)
        button.setMinimumHeight(height)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
            QPushButton:pressed {
                background-color: #104d9e;
            }
        """)
        return button
        
    def create_secondary_button(self, text, height=45):
        """Create a secondary button
        
        Args:
            text (str): Button text
            height (int): Button height
        """
        button = QPushButton(text)
        button.setMinimumHeight(height)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #1a73e8;
                border: 2px solid #1a73e8;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e8f0fe;
            }
            QPushButton:pressed {
                background-color: #d2e3fc;
            }
        """)
        return button
        
    def create_link_button(self, text):
        """Create a link-style button
        
        Args:
            text (str): Button text
        """
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet("""
            QPushButton {
                color: #1a73e8;
                border: none;
                font-size: 14px;
                padding: 10px;
                background: transparent;
            }
            QPushButton:hover {
                color: #1557b0;
                text-decoration: underline;
            }
        """)
        return button
        
    def create_card(self, padding=20):
        """Create a card frame
        
        Args:
            padding (int): Card padding
        """
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: {padding}px;
            }}
        """)
        return card
        
    def create_h_spacer(self):
        """Create a horizontal spacer"""
        return QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        
    def create_v_spacer(self):
        """Create a vertical spacer"""
        return QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        
    def create_icon_button(self, icon_path, size=45):
        """Create an icon button
        
        Args:
            icon_path (str): Path to icon file
            size (int): Button size
        """
        button = QPushButton()
        button.setFixedSize(size, size)
        button.setIcon(QIcon(icon_path))
        button.setStyleSheet("""
            QPushButton {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 5px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                border: 2px solid #1a73e8;
            }
        """)
        return button
        
    def create_label(self, text, color="#5f6368", size=14, bold=False):
        """Create a standard label
        
        Args:
            text (str): Label text
            color (str): Text color
            size (int): Font size
            bold (bool): Whether to use bold font
        """
        label = QLabel(text)
        font = QFont("Arial", size)
        font.setBold(bold)
        label.setFont(font)
        label.setStyleSheet(f"color: {color};")
        return label

    def get_asset_path(self, asset_name):
        """
        Constructs an absolute path to an asset in the 'assets' directory.
        """
        # current_dir for base_widget.py: finance_app/gui/base/
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        # package_dir: finance_app/
        package_dir = os.path.dirname(os.path.dirname(current_file_dir))
        # project_root_dir: one level above finance_app/
        project_root_dir = os.path.dirname(package_dir)
        assets_dir = os.path.join(project_root_dir, "assets")
        return os.path.join(assets_dir, asset_name) 