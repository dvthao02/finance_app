from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox
from finance_app.data_manager.user_manager import UserManager
from finance_app.data_manager.transaction_manager import TransactionManager
from finance_app.data_manager.category_manager import CategoryManager
from finance_app.data_manager.budget_manager import BudgetManager
from finance_app.data_manager.recurring_transaction_manager import RecurringTransaction
from finance_app.data_manager.notification_manager import NotificationManager
from finance_app.data_manager.setting_manager import SettingManager
from finance_app.data_manager.report_manager import ReportManager

class FrmBase(QMainWindow): # Base form for all windows
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Initialize managers
        self.user_manager = UserManager()
        self.transaction_manager = TransactionManager()
        self.category_manager = CategoryManager()
        self.budget_manager = BudgetManager()
        self.recurring_transaction_manager = RecurringTransaction()
        self.notification_manager = NotificationManager()
        self.setting_manager = SettingManager()
        self.report_manager = ReportManager()
        
        # Store current user info
        self.current_user = None
        self.current_settings = None
        
    def set_current_user(self, user_id):
        """Set current user after login
        Args:
            user_id (str): ID of logged in user
        """
        self.current_user = self.user_manager.get_user_by_id(user_id)
        if self.current_user:
            print(f"Current user set: {self.current_user['username']}")
            self.current_settings = self.setting_manager.get_user_settings(user_id)
        else:
            print("User not found with provided ID")
            self.current_settings = None

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
        if message_type == "info":
            QMessageBox.information(self, "Information", message)
        elif message_type == "warning":
            QMessageBox.warning(self, "Warning", message)
        elif message_type == "error":
            QMessageBox.critical(self, "Error", message)
        else:
            QMessageBox.information(self, "Information", message)

    def logout(self):
        """Log out current user"""
        if self.current_user:
            print(f"User {self.current_user['username']} logged out")
            self.current_user = None
            self.current_settings = None
            self.display_message("You have logged out successfully", "info")
            # Add logic to return to login screen here if needed
        else:
            self.display_message("No user currently logged in", "info")

    def is_admin(self):
        """Check if current user is admin"""
        if self.current_user:
            return self.user_manager.is_admin(self.current_user['user_id'])
        return False

    def get_user_setting(self, setting_key, default_value=None):
        """Get specific user setting
        Args:
            setting_key (str): Setting key to get
            default_value: Default value if setting not found
        Returns:
            Setting value or default value
        """
        if self.current_settings:
            return self.current_settings.get(setting_key, default_value)
        return default_value