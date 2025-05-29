# main_app.py

from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from PyQt5.QtCore import Qt
from finance_app.gui.frmLogin import LoginForm
from finance_app.gui.admin.frmAdmin_dashboard import AdminDashboard
from finance_app.gui.user.frmUser_dashboard import UserDashboard
from finance_app.gui.frmBase import FrmBase

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Thiết lập cơ bản cho cửa sổ chính
        self.setWindowTitle("Quản lý tài chính")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create stacked widget to manage different screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Initialize base frame
        self.base_frame = FrmBase()
        
        # Create and add forms
        self.login_form = LoginForm(self)
        self.admin_dashboard = AdminDashboard(self)
        self.user_dashboard = UserDashboard(self)
        
        self.stacked_widget.addWidget(self.login_form)
        self.stacked_widget.addWidget(self.admin_dashboard)
        self.stacked_widget.addWidget(self.user_dashboard)
        
        # Show login initially
        self.show_login_frame()

    def show_login_frame(self):
        """Hiển thị form đăng nhập."""
        self.stacked_widget.setCurrentWidget(self.login_form)
        
    def on_login_success(self, user_id):
        """Xử lý sau khi đăng nhập thành công."""
        self.base_frame.set_current_user(user_id)
        
        if not self.base_frame.current_user:
            self.show_message("Lỗi: Không thể tải thông tin người dùng.", QMessageBox.Critical)
            self.show_login_frame()
            return

        self.show_message(
            f"Đăng nhập thành công! Chào mừng {self.base_frame.current_user['username']}", 
            QMessageBox.Information
        )
        self.show_main_dashboard()

    def show_main_dashboard(self):
        """Hiển thị dashboard tương ứng (Admin hoặc User)."""
        if not self.base_frame.current_user:
            self.show_message("Lỗi: Người dùng chưa đăng nhập.", QMessageBox.Critical)
            self.show_login_frame()
            return

        if self.base_frame.current_user.get("is_admin", False):
            self.admin_dashboard.init_dashboard()
            self.stacked_widget.setCurrentWidget(self.admin_dashboard)
        else:
            self.user_dashboard.init_dashboard()
            self.stacked_widget.setCurrentWidget(self.user_dashboard)

    def handle_logout(self):
        """Xử lý đăng xuất."""
        if self.base_frame.is_user_logged_in():
            user_name = self.base_frame.current_user['username']
            self.base_frame.logout()
            self.show_message(f"Người dùng {user_name} đã đăng xuất.", QMessageBox.Information)
        else:
            self.show_message("Không có người dùng nào đang đăng nhập.", QMessageBox.Information)
            
        self.show_login_frame()

    def show_message(self, message, icon=QMessageBox.Information):
        """Hiển thị message box."""
        msg = QMessageBox(self)
        msg.setIcon(icon)
        msg.setWindowTitle("Thông báo" if icon == QMessageBox.Information else "Lỗi")
        msg.setText(message)
        msg.exec_()
