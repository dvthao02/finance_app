from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
import os

class BaseForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
        
    def show_error(self, title, message):
        """Show error message box"""
        QMessageBox.critical(self, title, message)
        
    def show_warning(self, title, message):
        """Show warning message box"""
        QMessageBox.warning(self, title, message)
        
    def show_info(self, title, message):
        """Show information message box"""
        QMessageBox.information(self, title, message)
        
    def show_question(self, title, message):
        """Show question message box"""
        return QMessageBox.question(
            self, 
            title, 
            message,
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes
        
    def get_asset_path(self, filename):
        """Get full path to an asset file"""
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'assets',
            filename
        )
        
    def center_on_screen(self):
        """Center the window on the screen"""
        frame_geometry = self.frameGeometry()
        center_point = self.screen().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
        
    def set_window_title(self, title):
        """Set window title with app name prefix"""
        self.setWindowTitle(f"Finance App - {title}")
        
    def set_window_icon(self):
        """Set window icon"""
        from PyQt5.QtGui import QIcon
        icon_path = self.get_asset_path('logo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
    def setup_window(self, title, fixed_size=None):
        """Setup basic window properties
        
        Args:
            title (str): Window title
            fixed_size (tuple, optional): Fixed window size (width, height)
        """
        self.set_window_title(title)
        self.set_window_icon()
        
        if fixed_size:
            self.setFixedSize(*fixed_size)
            
        self.center_on_screen()
        
        # Set default window style
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                font-family: Arial;
            }
        """) 