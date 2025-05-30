from finance_app.gui.base.base_dashboard import BaseDashboard
from finance_app.gui.user.pages.profile_page import UserProfilePage
from finance_app.gui.user.pages.settings_page import UserSettingsPage
from finance_app.gui.user.pages.transactions_page import TransactionsPage
from finance_app.gui.user.pages.budgets_page import BudgetsPage
from finance_app.gui.user.pages.categories_page import UserCategoriesPage
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
        self.transaction_manager = TransactionManager()
        self.notification_manager = NotificationManager()
        
        super().__init__(parent)
        
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
        """Set current user and update pages
        
        Args:
            user_data (dict): User data dictionary
        """
        super().set_current_user(user_data)
        
        if self.current_user_id:
            # Propagate current_user_id to all managers
            self.user_manager.set_current_user(self.current_user_id)
            self.category_manager.set_current_user(self.current_user_id)
            self.budget_manager.set_current_user(self.current_user_id)
            self.transaction_manager.set_current_user(self.current_user_id)
            self.notification_manager.set_current_user(self.current_user_id)
        
        # Update pages with user data is now handled by refresh_data, called by super().set_current_user()
        
    def refresh_data(self):
        """Refresh all dashboard data"""
        if not self.current_user_id:
            # TODO: Consider clearing page data or showing placeholder if no user.
            # For now, just returning prevents errors if current_user is None.
            # Example: self.profile_page.update_user_info(None) and other pages clear their views.
            return
            
        try:
            # Refresh profile page first if it relies on user_data directly
            if self.current_user:
                self.profile_page.update_user_info(self.current_user)
            else:
                # If current_user is None but current_user_id was somehow set,
                # clear profile page or handle appropriately.
                # This case should ideally not happen if current_user_id implies current_user is set.
                self.profile_page.update_user_info(None)


            # Refresh all other pages
            self.transactions_page.refresh_data()
            self.budgets_page.refresh_data()
            self.categories_page.refresh_data()
            self.notifications_page.refresh_data()
            self.settings_page.refresh_data() # Ensure settings page is consistently refreshed
            
            # Update navigation badges
            self.update_nav_badges()
            
        except Exception as e:
            self.show_error(
                "Lỗi",
                f"Không thể tải dữ liệu: {str(e)}"
            )
            
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
                self.notifications_page.refresh_data()
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
                self.notifications_page.refresh_data()
                self.update_nav_badges()
                
        except Exception as e:
            self.show_error(
                "Lỗi",
                f"Không thể tạo thông báo: {str(e)}"
            ) 