from finance_app.gui.base.base_dashboard import BaseDashboard
from finance_app.gui.admin.pages.profile_page import AdminProfilePage
from finance_app.gui.admin.pages.settings_page import AdminSettingsPage
from finance_app.gui.admin.pages.users_page import AdminUsersPage
from finance_app.gui.admin.pages.categories_page import AdminCategoriesPage
from finance_app.gui.admin.pages.statistics_page import AdminStatisticsPage
from finance_app.data_manager.user_manager import UserManager
from finance_app.data_manager.category_manager import CategoryManager
from finance_app.data_manager.budget_manager import BudgetManager
from finance_app.data_manager.transaction_manager import TransactionManager
from finance_app.data_manager.notification_manager import NotificationManager

class AdminDashboard(BaseDashboard):
    def __init__(self, parent=None, setting_manager=None): # Add setting_manager parameter
        # Initialize managers
        self.user_manager = UserManager()
        self.category_manager = CategoryManager()
        self.budget_manager = BudgetManager()
        self.transaction_manager = TransactionManager()
        self.notification_manager = NotificationManager()
        self.setting_manager = setting_manager # Store the passed setting_manager
        
        super().__init__(parent)
        
    def get_nav_items(self):
        """Get navigation items for admin dashboard"""
        return [
            {
                'text': 'Thống kê',
                'icon': 'stats.png',
                'page': 'statistics'
            },
            {
                'text': 'Quản lý người dùng',
                'icon': 'users.png',
                'page': 'users'
            },
            {
                'text': 'Danh mục',
                'icon': 'categories.png',
                'page': 'categories'
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
        """Create admin dashboard pages"""
        # Statistics page
        self.statistics_page = AdminStatisticsPage(self)
        self.stack.addWidget(self.statistics_page)
        
        # Users page
        self.users_page = AdminUsersPage(self)
        self.stack.addWidget(self.users_page)
        
        # Categories page
        self.categories_page = AdminCategoriesPage(self)
        self.stack.addWidget(self.categories_page)
        
        # Settings page
        self.settings_page = AdminSettingsPage(self)
        self.stack.addWidget(self.settings_page)
        
        # Profile page
        self.profile_page = AdminProfilePage(self)
        self.stack.addWidget(self.profile_page)
        
        # Show default page
        self.show_page('statistics')
        
    def get_dashboard_title(self):
        """Get dashboard title"""
        return "Admin Dashboard"
        
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
        
        # Update pages with user data
        self.profile_page.update_user_info(user_data)
        self.statistics_page.refresh_data()
        self.users_page.refresh_data()
        self.categories_page.refresh_data()
        
    def refresh_data(self):
        """Refresh all dashboard data"""
        if not self.current_user_id:
            return
            
        try:
            # Refresh all pages
            self.statistics_page.refresh_data()
            self.users_page.refresh_data()
            self.categories_page.refresh_data()
            self.settings_page.refresh_data()
            
        except Exception as e:
            self.show_error(
                "Lỗi",
                f"Không thể tải dữ liệu: {str(e)}"
            )