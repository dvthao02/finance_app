# main_app.py

from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from PyQt5.QtCore import Qt
from finance_app.gui.auth.login_form import LoginForm
from finance_app.gui.admin.admin_dashboard import AdminDashboard
from finance_app.gui.user.user_dashboard import UserDashboard
from finance_app.data_manager.user_manager import UserManager

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_frame = None
        self.login_frame = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the application UI"""
        self.setWindowTitle("Ứng dụng Quản lý Tài chính")
        self.setMinimumSize(800, 600)
        
        # Create stacked widget to manage different screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create screens
        self.login_screen = LoginForm(self)
        self.login_screen.login_success.connect(self.on_login_success)
        
        self.admin_dashboard = None
        self.user_dashboard = None
        
        # Add login screen
        self.stacked_widget.addWidget(self.login_screen)
        self.login_frame = self.login_screen
        self.current_frame = self.login_frame
        
        # Center window
        self.center_window()
        
    def center_window(self):
        """Center the window on the screen"""
        frame_geometry = self.frameGeometry()
        center_point = self.screen().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
        
    def on_login_success(self, user_id):
        """Handle successful login
        
        Args:
            user_id (str): ID of the logged in user
        """
        try:
            user_manager = UserManager()
            user_data = user_manager.get_user_by_id(user_id)
            if not user_data:
                raise ValueError("User data not found")
                
            is_admin = user_data.get('is_admin', False)
            print(f"User {user_id} logged in. Is admin: {is_admin}")
            
            if is_admin:
                # Create new admin dashboard if doesn't exist
                if not self.admin_dashboard:
                    self.admin_dashboard = AdminDashboard(self)
                    self.stacked_widget.addWidget(self.admin_dashboard)
                
                # Set up admin dashboard
                self.admin_dashboard.set_current_user(user_data)
                self.stacked_widget.setCurrentWidget(self.admin_dashboard)
                self.current_frame = self.admin_dashboard
            else:
                # Create new user dashboard if doesn't exist
                if not self.user_dashboard:
                    self.user_dashboard = UserDashboard(self)
                    self.stacked_widget.addWidget(self.user_dashboard)
                
                # Set up user dashboard
                self.user_dashboard.set_current_user(user_data)
                self.stacked_widget.setCurrentWidget(self.user_dashboard)
                self.current_frame = self.user_dashboard
                
        except Exception as e:
            print(f"Error during login: {str(e)}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi chuyển đến màn hình chính: {str(e)}")
            self.show_login_frame()
            
    def show_login_frame(self):
        """Show the login frame"""
        if self.current_frame and self.current_frame != self.login_frame:
            self.stacked_widget.setCurrentWidget(self.login_frame)
            self.current_frame = self.login_frame
