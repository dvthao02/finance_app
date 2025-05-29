from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QSpacerItem, QSizePolicy, QMessageBox)
from PyQt5.QtCore import Qt
from finance_app.gui.components.statistics_panel import StatisticsPanel
from finance_app.gui.components.budget_chart import BudgetChart
from finance_app.gui.components.transaction_table import TransactionTable
from finance_app.gui.components.notification_panel import NotificationPanel
from finance_app.gui.frmBase import FrmBase
from finance_app.gui.admin.user_dialogs import UserDialog, ResetPasswordDialog
from finance_app.gui.admin.category_dialog import CategoryDialog
from finance_app.gui.admin.dialogs.user_delete_dialog import UserDeleteDialog
from finance_app.data_manager.transaction_manager import TransactionManager
from finance_app.data_manager.budget_manager import BudgetManager
from finance_app.data_manager.notification_manager import NotificationManager
from finance_app.data_manager.recurring_transaction_manager import RecurringTransactionManager

class AdminDashboard(FrmBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Create the main layout after super() call
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
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
        
        self.main_layout.addLayout(header_layout)
        
        # Statistics panel
        self.stats_panel = StatisticsPanel()
        self.main_layout.addWidget(self.stats_panel)
        
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
        users_layout = QVBoxLayout(users_tab)
        
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
        categories_layout = QVBoxLayout(categories_tab)
        
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
        reports_layout = QVBoxLayout(reports_tab)
        
        # Add budget chart
        self.budget_chart = BudgetChart()
        reports_layout.addWidget(self.budget_chart)
        
        # Add transactions table
        self.transaction_table = TransactionTable()
        reports_layout.addWidget(self.transaction_table)
        
        # Notifications tab
        notifications_tab = QWidget()
        notifications_layout = QVBoxLayout(notifications_tab)
        
        # Add notification panel
        self.notification_panel = NotificationPanel()
        notifications_layout.addWidget(self.notification_panel)
        
        # Add tabs
        tabs.addTab(users_tab, "Người dùng")
        tabs.addTab(categories_tab, "Danh mục")
        tabs.addTab(reports_tab, "Báo cáo")
        tabs.addTab(notifications_tab, "Thông báo")
        
        self.main_layout.addWidget(tabs)
        
    def init_dashboard(self):
        """Initialize dashboard data"""
        self.load_users()
        self.load_categories()
        self.load_reports()
        self.load_notifications()
        self.update_statistics()
        
    def load_users(self):
        """Load users data into table"""
        try:
            users = self.user_manager.get_all_users(active_only=False)
            self.users_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                try:
                    # Store user data for row
                    user_data = {
                        'user_id': user.get('user_id', ''),
                        'username': user.get('username', ''),
                        'full_name': user.get('full_name', ''),
                        'email': user.get('email', ''),
                        'phone': user.get('phone', ''),
                        'is_active': user.get('is_active', True)
                    }
                    
                    # Set table items
                    self.users_table.setItem(row, 0, QTableWidgetItem(user_data['user_id']))
                    self.users_table.setItem(row, 1, QTableWidgetItem(user_data['username']))
                    self.users_table.setItem(row, 2, QTableWidgetItem(user_data['full_name']))
                    self.users_table.setItem(row, 3, QTableWidgetItem(user_data['email']))
                    self.users_table.setItem(row, 4, QTableWidgetItem(user_data['phone']))
                    self.users_table.setItem(row, 5, QTableWidgetItem(
                        'Hoạt động' if user_data['is_active'] else 'Đã khóa'
                    ))
                    
                    # Add action buttons
                    actions_layout = QHBoxLayout()
                    actions_layout.setContentsMargins(5, 0, 5, 0)
                    actions_layout.setSpacing(5)
                    
                    edit_btn = QPushButton("Sửa")
                    edit_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #3498db;
                            color: white;
                            border: none;
                            padding: 5px 10px;
                            border-radius: 3px;
                        }
                        QPushButton:hover {
                            background-color: #2980b9;
                        }
                    """)
                    edit_btn.clicked.connect(lambda checked, data=user_data: self.show_edit_user_dialog(data))
                    
                    delete_btn = QPushButton("Xóa")
                    delete_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #e74c3c;
                            color: white;
                            border: none;
                            padding: 5px 10px;
                            border-radius: 3px;
                        }
                        QPushButton:hover {
                            background-color: #c0392b;
                        }
                    """)
                    delete_btn.clicked.connect(lambda checked, data=user_data: self.delete_user(data))
                    
                    toggle_btn = QPushButton("Khóa" if user_data['is_active'] else "Mở khóa")
                    toggle_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #f1c40f;
                            color: white;
                            border: none;
                            padding: 5px 10px;
                            border-radius: 3px;
                        }
                        QPushButton:hover {
                            background-color: #f39c12;
                        }
                    """)
                    toggle_btn.clicked.connect(lambda checked, data=user_data: self.toggle_user_status(data))
                    
                    actions_layout.addWidget(edit_btn)
                    actions_layout.addWidget(delete_btn)
                    actions_layout.addWidget(toggle_btn)
                    
                    actions_widget = QWidget()
                    actions_widget.setLayout(actions_layout)
                    self.users_table.setCellWidget(row, 6, actions_widget)
                    
                except Exception as e:
                    print(f"Error setting up row {row}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error loading users: {str(e)}")
            self.display_message("Lỗi khi tải danh sách người dùng", "error")
        
    def load_categories(self):
        """Load categories data into table"""
        if not self.current_user:
            return
            
        categories = self.category_manager.get_all_categories(self.current_user['user_id'])
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
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            edit_btn.clicked.connect(lambda checked, c=category: self.show_edit_category_dialog(c))
            
            delete_btn = QPushButton("Xóa")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda checked, c=category: self.delete_category(c))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.categories_table.setCellWidget(row, 3, actions_widget)
            
    def load_reports(self):
        """Load reports data"""
        try:
            # Update budget chart with actual data
            budgets = self.budget_manager.get_user_budgets(self.current_user['user_id'])
            self.budget_chart.update_chart(budgets)
            
            # Update transaction table
            transactions = self.transaction_manager.get_all_transactions()
            self.transaction_table.update_transactions(transactions)
            
        except Exception as e:
            print(f"Error loading reports: {str(e)}")
            self.display_message("Lỗi khi tải dữ liệu báo cáo", "error")
        
    def load_notifications(self):
        """Load notifications"""
        notifications = self.notification_manager.get_all_notifications()
        for notification in notifications:
            self.notification_panel.add_notification(notification)
            
    def update_statistics(self):
        """Update statistics panel"""
        try:
            # Get all transactions
            transactions = self.transaction_manager.get_all_transactions()
            total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
            total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
            net_worth = total_income - total_expenses
            
            # Get budget summary
            budget_summary = self.budget_manager.get_budget_summary(self.current_user['user_id'])
            
            # Calculate budget status
            if budget_summary['over_budget_count'] > 0:
                status = 'Vượt ngân sách'
            elif any(b['spent_amount'] / b['amount'] * 100 >= b['alert_threshold'] 
                    for b in budget_summary['budgets'] if b['amount'] > 0):
                status = 'Gần hạn mức'
            else:
                status = 'Tốt'
                
            stats = {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_worth': net_worth,
                'budget_status': status,
                'remaining_budget': budget_summary['total_remaining']
            }
            
            self.stats_panel.update_statistics(stats)
            
        except Exception as e:
            print(f"Error updating statistics: {str(e)}")
            self.display_message("Lỗi khi cập nhật thống kê", "error")
        
    def show_add_user_dialog(self):
        """Show dialog to add new user"""
        dialog = UserDialog(self)
        if dialog.exec_():
            self.load_users()
            self.display_message("Đã thêm người dùng thành công")

    def show_edit_user_dialog(self, user):
        """Show dialog to edit user
        
        Args:
            user (dict): User to edit
        """
        dialog = UserDialog(self, user)
        if dialog.exec_():
            self.load_users()
            self.display_message("Đã cập nhật thông tin người dùng thành công")

    def show_reset_password_dialog(self, user):
        """Show dialog to reset user password
        
        Args:
            user (dict): User to reset password
        """
        dialog = ResetPasswordDialog(self, user['username'])
        if dialog.exec_():
            self.display_message("Đã đặt lại mật khẩu thành công")

    def show_add_category_dialog(self):
        """Show dialog to add new category"""
        dialog = CategoryDialog(self)
        if dialog.exec_():
            self.load_categories()
            self.display_message("Đã thêm danh mục thành công")

    def show_edit_category_dialog(self, category):
        """Show dialog to edit category
        
        Args:
            category (dict): Category to edit
        """
        dialog = CategoryDialog(self, category)
        if dialog.exec_():
            self.load_categories()
            self.display_message("Đã cập nhật danh mục thành công")
    def delete_user(self, user):
        """Delete a user and all associated data
        
        Args:
            user (dict): User to delete
        """
        # Don't allow deleting admin users
        if user.get('is_admin', False):
            self.display_message("Không thể xóa tài khoản quản trị viên.", "error")
            return

        # Show confirmation dialog
        dialog = UserDeleteDialog(self, user)
        if dialog.exec_():
            try:
                # Get managers for associated data
                transaction_manager = TransactionManager()
                budget_manager = BudgetManager()
                notification_manager = NotificationManager()
                recurring_transaction_manager = RecurringTransactionManager()
                
                # Delete all associated data
                try:
                    transaction_manager.delete_user_transactions(user['user_id'])
                    budget_manager.delete_user_budgets(user['user_id'])
                    notification_manager.delete_user_notifications(user['user_id'])
                    recurring_transaction_manager.delete_user_recurring_transactions(user['user_id'])
                except Exception as e:
                    print(f"Warning: Error cleaning up user data: {str(e)}")
                
                # Finally delete the user
                self.user_manager.delete_user(user['username'])
                self.load_users()
                self.display_message("Đã xóa người dùng và dữ liệu liên quan thành công")
            
            except Exception as e:
                self.display_message(f"Lỗi khi xóa người dùng: {str(e)}", "error")
                
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
            # Find the main window to show login frame
            main_window = self.window()
            if main_window:
                main_window.show_login_frame()
