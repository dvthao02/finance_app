from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox
from finance_app.data_manager.user_manager import UserManager
from finance_app.data_manager.transaction_manager import TransactionManager
from finance_app.data_manager.category_manager import CategoryManager
from finance_app.data_manager.budget_manager import BudgetManager
from finance_app.data_manager.recurring_transaction_manager import RecurringTransactionManager
from finance_app.data_manager.notification_manager import NotificationManager
from finance_app.data_manager.setting_manager import SettingManager
from finance_app.data_manager.report_manager import ReportManager

# Base form for all windows
class FrmBase(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set window properties
        self.setMinimumSize(350, 768)
        self.setWindowTitle("Ứng dụng Quản lý Tài chính")
        
        # Create and set central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        try:
            # Initialize managers
            self.user_manager = UserManager()
            self.transaction_manager = TransactionManager()
            self.category_manager = CategoryManager()
            self.budget_manager = BudgetManager()
            self.recurring_transaction_manager = RecurringTransactionManager()
            self.notification_manager = NotificationManager()
            self.setting_manager = SettingManager()
            self.report_manager = ReportManager()
            
            # Store current user info
            self.current_user = None
            self.current_settings = None
            
            self.child_form = None  # Track the currently displayed child form
            
        except Exception as e:
            print(f"Lỗi khởi tạo managers: {str(e)}")
            self.display_message("Lỗi khởi tạo hệ thống. Vui lòng khởi động lại ứng dụng.", "error")
        
    def set_current_user(self, user_id):
        """Set current user after login
        Args:
            user_id (str): ID of logged in user
        """
        try:
            self.current_user = self.user_manager.get_user_by_id(user_id)
            if self.current_user:
                print(f"Current user set: {self.current_user['username']}")
                self.current_settings = self.setting_manager.get_user_settings(user_id)
                
                # Initialize user-specific data in managers
                self.transaction_manager.set_current_user(user_id)
                self.category_manager.set_current_user(user_id)
                self.budget_manager.set_current_user(user_id)
                self.notification_manager.set_current_user(user_id)
                self.report_manager.set_current_user(user_id)
            else:
                print("User not found with provided ID")
                self.current_settings = None
                
        except Exception as e:
            print(f"Lỗi khi thiết lập người dùng hiện tại: {str(e)}")
            self.current_user = None
            self.current_settings = None
            raise

    def get_current_user(self):
        """Get current logged in user"""
        return self.current_user

    def get_current_user_id(self):
        """Get current user ID"""
        return self.current_user['user_id'] if self.current_user else None

    def is_user_logged_in(self):
        """Check if user is logged in"""
        return self.current_user is not None

    def display_message(self, message, message_type="info"):
        """Display message to user using QMessageBox
        Args:
            message (str): Message content
            message_type (str): Message type ("info", "warning", "error")
        """
        try:
            if message_type == "info":
                QMessageBox.information(self, "Thông báo", message)
            elif message_type == "warning":
                QMessageBox.warning(self, "Cảnh báo", message)
            elif message_type == "error":
                QMessageBox.critical(self, "Lỗi", message)
            else:
                QMessageBox.information(self, "Thông báo", message)
        except Exception as e:
            print(f"Lỗi hiển thị thông báo: {str(e)}")

    def logout(self):
        """Log out current user"""
        try:
            if self.current_user:
                username = self.current_user['username']
                
                # Clear user data in managers
                self.transaction_manager.set_current_user(None)
                self.category_manager.set_current_user(None)
                self.budget_manager.set_current_user(None)
                self.notification_manager.set_current_user(None)
                self.report_manager.set_current_user(None)
                
                # Clear current user data
                self.current_user = None
                self.current_settings = None
                
                print(f"User {username} logged out")
                self.display_message("Đăng xuất thành công", "info")
            else:
                self.display_message("Không có người dùng nào đang đăng nhập", "info")
                
        except Exception as e:
            print(f"Lỗi khi đăng xuất: {str(e)}")
            self.display_message("Lỗi khi đăng xuất. Vui lòng thử lại.", "error")

    def is_admin(self):
        """Check if current user is admin"""
        try:
            if self.current_user:
                return self.user_manager.is_admin(self.current_user['user_id'])
            return False
        except Exception as e:
            print(f"Lỗi khi kiểm tra quyền admin: {str(e)}")
            return False

    def get_user_setting(self, setting_key, default_value=None):
        """Get specific user setting
        Args:
            setting_key (str): Setting key to get
            default_value: Default value if setting not found
        Returns:
            Setting value or default value
        """
        try:
            if self.current_settings:
                return self.current_settings.get(setting_key, default_value)
            return default_value
        except Exception as e:
            print(f"Lỗi khi lấy cài đặt người dùng: {str(e)}")
            return default_value

    def show_child_form(self, child_form):
        """Display a child form within the base form
        Args:
            child_form (QWidget): The child form to display
        """
        if self.child_form:
            self.child_form.close()  # Close the existing child form if any

        self.child_form = child_form
        self.child_form.setParent(self.central_widget)
        self.child_form.show()
        self.resize_child_form()

    def resize_child_form(self):
        """Resize and center the child form within the base form"""
        if self.child_form:
            child_width = self.child_form.width()
            child_height = self.child_form.height()
            base_width = self.width()
            base_height = self.height()

            x = (base_width - child_width) // 2
            y = (base_height - child_height) // 2

            self.child_form.move(x, y)

    def resizeEvent(self, event):
        """Handle resizing of the base form"""
        super().resizeEvent(event)
        self.resize_child_form()