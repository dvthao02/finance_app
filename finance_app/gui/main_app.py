from PyQt5.QtWidgets import QMainWindow
from finance_app.gui.auth.login_form import LoginForm
from finance_app.gui.admin.admin_dashboard import AdminDashboard
from finance_app.gui.user.user_dashboard import UserDashboard
from finance_app.data_manager.user_manager import UserManager

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.admin_dashboard = None
        self.user_dashboard = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Ứng dụng Quản lý Tài chính")
        self.setMinimumSize(800, 600)
        self.center_window()
        # Initially hide the main window until login is successful
        self.hide()

        # Hiện form đăng nhập độc lập, modal (chặn)
        self.login_screen = LoginForm() # No parent, it's the top-level login UI
        self.login_screen.login_success.connect(self.on_login_success)
        
        result = self.login_screen.exec_()

        if result == LoginForm.Accepted:
            # on_login_success will be called via the signal, which then shows the main window.
            pass 
        else:
            # If login is not accepted (dialog closed or rejected), exit the application.
            # We need to import QApplication for sys.exit
            from PyQt5.QtWidgets import QApplication
            import sys
            QApplication.instance().quit() # Cleanly exits the Qt application loop
            sys.exit() # Ensure immediate exit

    def center_window(self):
        frame_geometry = self.frameGeometry()
        center_point = self.screen().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def on_login_success(self, user_id):
        user_manager = UserManager()
        user_data = user_manager.get_user_by_id(user_id)
        if not user_data:
            # Nên thêm xử lý nếu ko tìm thấy user, vd show message rồi thoát app hoặc quay lại login
            # For now, let's ensure the app exits if user data is not found after supposed success
            from PyQt5.QtWidgets import QApplication, QMessageBox
            QMessageBox.critical(self, "Lỗi người dùng", "Không tìm thấy dữ liệu người dùng sau khi đăng nhập.")
            QApplication.instance().quit()
            return

        is_admin = user_data.get('is_admin', False)

        if is_admin:
            if not self.admin_dashboard:
                self.admin_dashboard = AdminDashboard(self)
            self.setCentralWidget(self.admin_dashboard)
            self.admin_dashboard.set_current_user(user_data)
        else:
            if not self.user_dashboard:
                self.user_dashboard = UserDashboard(self)
            self.setCentralWidget(self.user_dashboard)
            self.user_dashboard.set_current_user(user_data)

        self.show()  
        # hiện cửa sổ chính khi đã login thành công
        
    def restart_app_for_login(self):
        """Hides current dashboard, re-shows login, and handles app exit or new dashboard."""
        # Hide the main window and clear central widget
        self.hide()
        if self.centralWidget():
            self.centralWidget().deleteLater() # Remove current dashboard
            self.setCentralWidget(None)

        # Reset dashboard instances if needed (optional, for a cleaner state)
        self.admin_dashboard = None
        self.user_dashboard = None

        # Re-run the login process
        self.login_screen = LoginForm() # Create a new login screen instance
        self.login_screen.login_success.connect(self.on_login_success)
        
        result = self.login_screen.exec_()

        if result == LoginForm.Accepted:
            # on_login_success will be called by the signal, which handles showing the main window and dashboard
            pass
        else:
            # If login is not accepted (dialog closed or rejected), exit the application.
            from PyQt5.QtWidgets import QApplication
            import sys
            QApplication.instance().quit()
            sys.exit() # Ensure immediate exit

    def show_login_frame(self): # This method is called by BaseDashboard on logout
        """Initiates the process of logging out and showing the login screen again."""
        self.restart_app_for_login()

            
