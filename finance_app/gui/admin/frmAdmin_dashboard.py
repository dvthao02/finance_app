from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QSpacerItem, QSizePolicy, QMessageBox)
from PyQt5.QtCore import Qt
from finance_app.gui.components.statistics_panel import StatisticsPanel
from finance_app.gui.components.budget_chart import BudgetChart
from finance_app.gui.components.transaction_table import TransactionTable
from finance_app.gui.components.notification_panel import NotificationPanel
from finance_app.gui.frmBase import FrmBase

class AdminDashboard(FrmBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Main layout
        main_layout = QVBoxLayout()
        self.central_widget.setLayout(main_layout)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Bảng điều khiển quản trị")
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        
        # Logout button
        logout_button = QPushButton("Đăng xuất")
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_button.clicked.connect(self.handle_logout)
        
        # Add widgets to header
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(logout_button)
        
        main_layout.addLayout(header_layout)
        
        # Statistics panel
        self.stats_panel = StatisticsPanel()
        main_layout.addWidget(self.stats_panel)
        
        # Tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 10px;
            }
            QTabBar::tab {
                background-color: #f5f6fa;
                padding: 8px 20px;
                margin-right: 2px;
                border: 1px solid #dcdde1;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: none;
            }
        """)
        
        # Users tab
        users_tab = QWidget()
        users_layout = QVBoxLayout()
        users_tab.setLayout(users_layout)
        
        # Users controls
        users_controls = QHBoxLayout()
        add_user_btn = QPushButton("Thêm người dùng")
        add_user_btn.clicked.connect(self.show_add_user_dialog)
        users_controls.addWidget(add_user_btn)
        users_controls.addStretch()
        users_layout.addLayout(users_controls)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(7)
        self.users_table.setHorizontalHeaderLabels([
            'ID', 'Tên đăng nhập', 'Họ tên', 'Email', 'SĐT', 'Trạng thái', 'Hành động'
        ])
        header = self.users_table.horizontalHeader()
        for i in range(7):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        users_layout.addWidget(self.users_table)
        
        # Categories tab
        categories_tab = QWidget()
        categories_layout = QVBoxLayout()
        categories_tab.setLayout(categories_layout)
        
        # Categories controls
        categories_controls = QHBoxLayout()
        add_category_btn = QPushButton("Thêm danh mục")
        add_category_btn.clicked.connect(self.show_add_category_dialog)
        categories_controls.addWidget(add_category_btn)
        categories_controls.addStretch()
        categories_layout.addLayout(categories_controls)
        
        # Categories table
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(4)
        self.categories_table.setHorizontalHeaderLabels([
            'ID', 'Tên danh mục', 'Loại', 'Hành động'
        ])
        header = self.categories_table.horizontalHeader()
        for i in range(4):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        categories_layout.addWidget(self.categories_table)
        
        # Reports tab
        reports_tab = QWidget()
        reports_layout = QVBoxLayout()
        reports_tab.setLayout(reports_layout)
        
        # Add budget chart
        self.budget_chart = BudgetChart()
        reports_layout.addWidget(self.budget_chart)
        
        # Add transactions table
        self.transaction_table = TransactionTable()
        reports_layout.addWidget(self.transaction_table)
        
        # Notifications tab
        notifications_tab = QWidget()
        notifications_layout = QVBoxLayout()
        notifications_tab.setLayout(notifications_layout)
        
        # Add notification panel
        self.notification_panel = NotificationPanel()
        notifications_layout.addWidget(self.notification_panel)
        
        # Add tabs
        tabs.addTab(users_tab, "Người dùng")
        tabs.addTab(categories_tab, "Danh mục")
        tabs.addTab(reports_tab, "Báo cáo")
        tabs.addTab(notifications_tab, "Thông báo")
        
        main_layout.addWidget(tabs)
        
    def init_dashboard(self):
        """Initialize dashboard data"""
        self.load_users()
        self.load_categories()
        self.load_reports()
        self.load_notifications()
        self.update_statistics()
        
    def load_users(self):
        """Load users data into table"""
        users = self.user_manager.get_all_users(active_only=False)
        self.users_table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            self.users_table.setItem(row, 0, QTableWidgetItem(user['user_id']))
            self.users_table.setItem(row, 1, QTableWidgetItem(user['username']))
            self.users_table.setItem(row, 2, QTableWidgetItem(user['full_name']))
            self.users_table.setItem(row, 3, QTableWidgetItem(user['email']))
            self.users_table.setItem(row, 4, QTableWidgetItem(user['phone']))
            self.users_table.setItem(row, 5, QTableWidgetItem(
                'Hoạt động' if user.get('is_active', True) else 'Đã khóa'
            ))
            
            # Add action buttons
            actions_layout = QHBoxLayout()
            edit_btn = QPushButton("Sửa")
            edit_btn.clicked.connect(lambda u=user: self.show_edit_user_dialog(u))
            
            delete_btn = QPushButton("Xóa")
            delete_btn.clicked.connect(lambda u=user: self.delete_user(u))
            
            toggle_btn = QPushButton("Khóa" if user.get('is_active', True) else "Mở khóa")
            toggle_btn.clicked.connect(lambda u=user: self.toggle_user_status(u))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addWidget(toggle_btn)
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.users_table.setCellWidget(row, 6, actions_widget)
            
    def load_categories(self):
        """Load categories data into table"""
        categories = self.category_manager.get_all_categories()
        self.categories_table.setRowCount(len(categories))
        
        for row, category in enumerate(categories):
            self.categories_table.setItem(row, 0, QTableWidgetItem(category['category_id']))
            self.categories_table.setItem(row, 1, QTableWidgetItem(category['name']))
            self.categories_table.setItem(row, 2, QTableWidgetItem(
                'Chi tiêu' if category['type'] == 'expense' else 'Thu nhập'
            ))
            
            # Add action buttons
            actions_layout = QHBoxLayout()
            edit_btn = QPushButton("Sửa")
            edit_btn.clicked.connect(lambda c=category: self.show_edit_category_dialog(c))
            
            delete_btn = QPushButton("Xóa")
            delete_btn.clicked.connect(lambda c=category: self.delete_category(c))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.categories_table.setCellWidget(row, 3, actions_widget)
            
    def load_reports(self):
        """Load reports data"""
        # Update budget chart with actual data
        budgets = self.budget_manager.get_all_budgets(self.current_user['user_id'])
        budget_data = {}
        for budget in budgets:
            category = self.category_manager.get_category_by_id(
                self.current_user['user_id'], 
                budget['category_id']
            )
            if category:
                budget_data[category['name']] = budget['amount']
                
        self.budget_chart.update_chart(budget_data)
        
        # Update transaction table
        transactions = self.transaction_manager.get_all_transactions()
        self.transaction_table.update_transactions(transactions)
        
    def load_notifications(self):
        """Load notifications"""
        notifications = self.notification_manager.get_all_notifications()
        for notification in notifications:
            self.notification_panel.add_notification(notification)
            
    def update_statistics(self):
        """Update statistics panel"""
        # Get actual statistics from transaction manager
        transactions = self.transaction_manager.get_all_transactions()
        
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        net_worth = total_income - total_expenses
        
        # Calculate budget status
        budgets = self.budget_manager.get_all_budgets(self.current_user['user_id'])
        over_budget = any(b['spent_amount'] > b['amount'] for b in budgets)
        near_limit = any(
            (b['spent_amount'] / b['amount'] * 100 >= b['alert_threshold'])
            for b in budgets if b['amount'] > 0
        )
        
        if over_budget:
            status = 'Vượt ngân sách'
        elif near_limit:
            status = 'Gần hạn mức'
        else:
            status = 'Tốt'
            
        stats = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_worth': net_worth,
            'budget_status': status
        }
        self.stats_panel.update_statistics(stats)
        
    def show_add_user_dialog(self):
        """Show dialog to add new user"""
        # TODO: Implement user add dialog
        pass
        
    def show_edit_user_dialog(self, user):
        """Show dialog to edit user
        
        Args:
            user (dict): User to edit
        """
        # TODO: Implement user edit dialog
        pass
        
    def delete_user(self, user):
        """Delete a user
        
        Args:
            user (dict): User to delete
        """
        if QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa người dùng {user['username']}?"
        ) == QMessageBox.Yes:
            try:
                self.user_manager.delete_user(user['username'])
                self.load_users()
                self.display_message("Đã xóa người dùng thành công")
            except Exception as e:
                self.display_message(str(e), "error")
                
    def toggle_user_status(self, user):
        """Toggle user active status
        
        Args:
            user (dict): User to toggle status
        """
        try:
            if user.get('is_active', True):
                self.user_manager.deactivate_user(user['username'])
            else:
                self.user_manager.activate_user(user['username'])
            self.load_users()
            self.display_message("Đã thay đổi trạng thái người dùng thành công")
        except Exception as e:
            self.display_message(str(e), "error")
            
    def show_add_category_dialog(self):
        """Show dialog to add new category"""
        # TODO: Implement category add dialog
        pass
        
    def show_edit_category_dialog(self, category):
        """Show dialog to edit category
        
        Args:
            category (dict): Category to edit
        """
        # TODO: Implement category edit dialog
        pass
        
    def delete_category(self, category):
        """Delete a category
        
        Args:
            category (dict): Category to delete
        """
        if QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa danh mục {category['name']}?"
        ) == QMessageBox.Yes:
            try:
                # TODO: Implement category deletion in CategoryManager
                self.load_categories()
                self.display_message("Đã xóa danh mục thành công")
            except Exception as e:
                self.display_message(str(e), "error")
                
    def handle_logout(self):
        """Handle logout button click"""
        if QMessageBox.question(
            self,
            "Xác nhận đăng xuất",
            "Bạn có chắc muốn đăng xuất?"
        ) == QMessageBox.Yes:
            self.logout()
            self.parent().show_login_frame()
