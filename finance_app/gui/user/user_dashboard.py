from PyQt5.QtWidgets import QLabel # Keep if used for placeholder pages
from finance_app.gui.base.base_dashboard import BaseDashboard
from finance_app.gui.user.pages.profile_page import UserProfilePage
from finance_app.gui.user.pages.settings_page import UserSettingsPage
from finance_app.gui.user.pages.transactions_page import TransactionsPage
from finance_app.gui.user.pages.budgets_page import BudgetsPage
from finance_app.gui.user.pages.category_page import UserCategoriesPage
from finance_app.gui.user.pages.notifications_page import NotificationsPage
from finance_app.data_manager.user_manager import UserManager
from finance_app.data_manager.category_manager import CategoryManager
from finance_app.data_manager.budget_manager import BudgetManager
from finance_app.data_manager.transaction_manager import TransactionManager
from finance_app.data_manager.notification_manager import NotificationManager

class UserDashboard(BaseDashboard):
    def __init__(self, parent=None):
        # Initialize managers
        self.user_manager = UserManager()
        self.category_manager = CategoryManager()
        self.budget_manager = BudgetManager()
        self.transaction_manager = TransactionManager(category_manager=self.category_manager)
        self.notification_manager = NotificationManager()
        
        super().__init__(parent)
        
    def setup_navigation(self):
        self.nav_tree.setHeaderHidden(True)
        # Add navigation items
        # self.nav_tree.addTopLevelItem("Trang chính") # Example if you have a main summary page
        self.nav_tree.addTopLevelItem("Giao dịch")
        self.nav_tree.addTopLevelItem("Ngân sách")
        self.nav_tree.addTopLevelItem("Danh mục")
        self.nav_tree.addTopLevelItem("Hồ sơ")
        self.nav_tree.addTopLevelItem("Cài đặt")
        self.nav_tree.expandAll()

    def init_pages(self):
        self.pages = {
            # "Trang chính": QLabel("Welcome to User Dashboard!"), # Example placeholder
            "Giao dịch": TransactionsPage(self),
            "Ngân sách": BudgetsPage(self),
            "Danh mục": UserCategoriesPage(self),
            "Hồ sơ": UserProfilePage(self),
            "Cài đặt": UserSettingsPage(self)
        }
        # Set initial page to the first item in navigation or a default like "Giao dịch"
        if self.nav_tree.topLevelItemCount() > 0:
            initial_page_text = self.nav_tree.topLevelItem(0).text(0)
            self.navigate(initial_page_text)
        elif "Giao dịch" in self.pages:
             self.navigate("Giao dịch")

    def get_nav_items(self):
        """Get navigation items for user dashboard"""
        return [
            {
                'text': 'Giao dịch',
                'icon': 'transactions.png',
                'page': 'transactions'
            },
            {
                'text': 'Ngân sách',
                'icon': 'budgets.png',
                'page': 'budgets'
            },
            {
                'text': 'Danh mục',
                'icon': 'categories.png',
                'page': 'categories'
            },
            {
                'text': 'Thông báo',
                'icon': 'notifications.png',
                'page': 'notifications',
                'badge': self.get_unread_notifications_count
            },
            {
                'text': 'Cài đặt',
                'icon': 'settings.png',
                'page': 'settings'
            },
            {
                'text': 'Hồ sơ',
                'icon': 'profile.png',
                'page': 'profile'
            }
        ]
        
    def create_pages(self):
        """Create user dashboard pages"""
        # Transactions page
        self.transactions_page = TransactionsPage(self)
        self.stack.addWidget(self.transactions_page)
        
        # Budgets page
        self.budgets_page = BudgetsPage(self)
        self.stack.addWidget(self.budgets_page)
        
        # Categories page
        self.categories_page = UserCategoriesPage(self)
        self.stack.addWidget(self.categories_page)
        
        # Notifications page
        self.notifications_page = NotificationsPage(self)
        self.stack.addWidget(self.notifications_page)
        
        # Settings page
        self.settings_page = UserSettingsPage(self)
        self.stack.addWidget(self.settings_page)
        
        # Profile page
        self.profile_page = UserProfilePage(self)
        self.stack.addWidget(self.profile_page)
        
        # Show default page
        self.show_page('transactions')
        
    def get_dashboard_title(self):
        """Get dashboard title"""
        return "User Dashboard"
        
    def set_current_user(self, user_data):
        """Set current user and update dashboard-specific elements."""
        # Call super first to set self.current_user, self.current_user_id 
        # and trigger the base refresh_data mechanism (which refreshes all pages)
        super().set_current_user(user_data)
        
        # UserDashboard specific tasks after user is set:
        if self.current_user_id: # self.current_user_id is set by super().set_current_user
            # Propagate current_user_id to managers specific to UserDashboard context if needed
            # (BaseDashboard might not know about all managers of a subclass)
            self.user_manager.set_current_user(self.current_user_id)
            self.category_manager.set_current_user(self.current_user_id)
            self.budget_manager.set_current_user(self.current_user_id)
            self.transaction_manager.set_current_user(self.current_user_id)
            self.notification_manager.set_current_user(self.current_user_id)
        
        # The page-specific refresh calls that were here are now redundant 
        # because super().set_current_user() calls self.refresh_data(), 
        # and UserDashboard.refresh_data() calls super().refresh_data() (BaseDashboard.refresh_data),
        # which iterates through self.pages and calls .refresh_data() on each page.

    def refresh_data(self):
        """Refreshes data for all relevant pages in the dashboard."""
        # This method is called by BaseDashboard.set_current_user.
        # The base implementation (super().refresh_data()) iterates through self.pages 
        # and calls refresh_data if available on each page.
        # Add any UserDashboard-specific global refresh logic here if necessary, 
        # then call super().
        # Example: self.update_user_specific_summary_widget_if_any()
        super().refresh_data()

    def get_unread_notifications_count(self):
        """Get number of unread notifications
        
        Returns:
            int: Number of unread notifications
        """
        if not self.current_user_id:
            return 0
            
        try:
            notifications = self.notification_manager.get_user_notifications(
                self.current_user_id,
                unread_only=True
            )
            return len(notifications)
        except:
            return 0
            
    def mark_notification_as_read(self, notification_id):
        """Mark notification as read
        
        Args:
            notification_id (str): Notification ID
        """
        try:
            success = self.notification_manager.mark_as_read(notification_id)
            
            if success:
                # Update notifications page and badge
                # self.notifications_page.refresh_data() # This page is likely in self.pages
                if "Thông báo" in self.pages and hasattr(self.pages["Thông báo"], 'refresh_data'):
                    self.pages["Thông báo"].refresh_data()
                self.update_nav_badges()
                
        except Exception as e:
            self.show_error(
                "Lỗi",
                f"Không thể đánh dấu đã đọc: {str(e)}"
            )
            
    def add_notification(self, title, message, notification_type='info'):
        """Add a new notification
        
        Args:
            title (str): Notification title
            message (str): Notification message
            notification_type (str): Notification type (info, warning, success, error)
        """
        if not self.current_user_id:
            return
            
        try:
            success = self.notification_manager.create_notification(
                user_id=self.current_user_id,
                title=title,
                message=message,
                type=notification_type
            )
            
            if success:
                # Update notifications page and badge
                # self.notifications_page.refresh_data()
                if "Thông báo" in self.pages and hasattr(self.pages["Thông báo"], 'refresh_data'):
                    self.pages["Thông báo"].refresh_data()
                self.update_nav_badges()
                
        except Exception as e:
            self.show_error(
                "Lỗi",
                f"Không thể tạo thông báo: {str(e)}"
            ) 