from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QSpacerItem, QSizePolicy, QMessageBox,
                             QComboBox, QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from finance_app.gui.components.statistics_panel import StatisticsPanel
from finance_app.gui.components.budget_chart import BudgetChart
from finance_app.gui.components.transaction_table import TransactionTable
from finance_app.gui.components.notification_panel import NotificationPanel
from finance_app.gui.user.dialogs.transaction_dialog import TransactionDialog
from finance_app.gui.user.dialogs.budget_dialog import BudgetDialog
from finance_app.gui.user.dialogs.recurring_dialog import RecurringTransactionDialog
from finance_app.gui.user.dialogs.profile_dialog import ProfileDialog
from finance_app.gui.user.change_password_dialog import ChangePasswordDialog
from finance_app.data_manager.transaction_manager import TransactionManager
from finance_app.data_manager.category_manager import CategoryManager
from finance_app.data_manager.budget_manager import BudgetManager
from finance_app.data_manager.notification_manager import NotificationManager
from finance_app.gui.frmBase import FrmBase

class UserDashboard(FrmBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.transaction_manager = TransactionManager()
        self.category_manager = CategoryManager()
        self.budget_manager = BudgetManager()
        self.notification_manager = NotificationManager()
        
        # Initialize UI
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Header
        header_layout = QHBoxLayout()
        
        # Title with welcome message
        self.title_label = QLabel()
        self.title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(self.title_label)
        
        # Right side buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Profile button
        profile_button = QPushButton("Hồ sơ")
        profile_button.setIcon(QIcon("finance_app/assets/user.png"))
        profile_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        profile_button.clicked.connect(self.show_profile_dialog)
        
        # Change password button
        change_pwd_button = QPushButton("Đổi mật khẩu")
        change_pwd_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #d68910;
            }
        """)
        change_pwd_button.clicked.connect(self.show_change_password_dialog)
        
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
        
        buttons_layout.addWidget(profile_button)
        buttons_layout.addWidget(change_pwd_button)
        buttons_layout.addWidget(logout_button)
        
        header_layout.addLayout(buttons_layout)
        self.main_layout.addLayout(header_layout)
        
        # Add tabs
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
        
        # Statistics panel
        self.stats_panel = StatisticsPanel()
        self.main_layout.addWidget(self.stats_panel)

        # Transactions tab
        transactions_tab = QWidget()
        transactions_layout = QVBoxLayout(transactions_tab)
        
        # Transaction controls
        transaction_controls = QHBoxLayout()
        
        # Add transaction button
        add_transaction_btn = QPushButton("Thêm giao dịch mới")
        add_transaction_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        add_transaction_btn.clicked.connect(self.show_add_transaction_dialog)
        transaction_controls.addWidget(add_transaction_btn)
        
        # Add recurring button
        add_recurring_btn = QPushButton("Thêm giao dịch định kỳ")
        add_recurring_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        add_recurring_btn.clicked.connect(self.show_add_recurring_dialog)
        transaction_controls.addWidget(add_recurring_btn)
        
        # Transaction filter
        self.transaction_filter = QComboBox()
        self.transaction_filter.addItems(["Tất cả", "Thu nhập", "Chi tiêu"])
        self.transaction_filter.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                min-width: 120px;
            }
        """)
        self.transaction_filter.currentTextChanged.connect(self.filter_transactions)
        transaction_controls.addWidget(QLabel("Lọc:"))
        transaction_controls.addWidget(self.transaction_filter)
        
        transactions_layout.addLayout(transaction_controls)
        
        # Transaction table
        self.transaction_table = TransactionTable()
        transactions_layout.addWidget(self.transaction_table)
        
        # Connect table signals
        self.transaction_table.edit_transaction.connect(self.show_edit_transaction_dialog)
        self.transaction_table.delete_transaction.connect(self.delete_transaction)
        
        # Add tabs
        tabs.addTab(transactions_tab, "Giao dịch")
        self.init_budget_tab(tabs)
        self.init_notification_tab(tabs)
        
        self.main_layout.addWidget(tabs)

    def init_budget_tab(self, tabs):
        """Initialize the budget tab"""
        budgets_tab = QWidget()
        budgets_layout = QVBoxLayout(budgets_tab)
        
        # Budget controls
        budget_controls = QHBoxLayout()
        
        # Add budget button
        add_budget_btn = QPushButton("Thêm ngân sách mới")
        add_budget_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        add_budget_btn.clicked.connect(self.show_add_budget_dialog)
        budget_controls.addWidget(add_budget_btn)
        
        # Budget period filter
        self.budget_period_filter = QComboBox()
        self.budget_period_filter.addItems(["Tháng này", "Năm nay", "Tất cả"])
        self.budget_period_filter.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                min-width: 120px;
            }
        """)
        self.budget_period_filter.currentTextChanged.connect(self.filter_budgets)
        budget_controls.addWidget(QLabel("Kỳ hạn:"))
        budget_controls.addWidget(self.budget_period_filter)
        
        budget_controls.addStretch()
        budgets_layout.addLayout(budget_controls)
        
        # Budget chart
        self.budget_chart = BudgetChart()
        budgets_layout.addWidget(self.budget_chart)
        
        # Budget table
        self.budget_table = QTableWidget()
        self.budget_table.setColumnCount(6)
        self.budget_table.setHorizontalHeaderLabels([
            'Danh mục', 'Hạn mức', 'Đã chi', 'Còn lại', 'Trạng thái', 'Hành động'
        ])
        header = self.budget_table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        budgets_layout.addWidget(self.budget_table)

        tabs.addTab(budgets_tab, "Ngân sách")

    def init_notification_tab(self, tabs):
        """Initialize the notification tab"""
        notifications_tab = QWidget()
        notifications_layout = QVBoxLayout(notifications_tab)
        
        # Add notification panel
        self.notification_panel = NotificationPanel()
        notifications_layout.addWidget(self.notification_panel)

        tabs.addTab(notifications_tab, "Thông báo")

    def filter_transactions(self):
        """Filter transactions based on type"""
        try:
            filter_type = self.transaction_filter.currentText()
            user_id = self.current_user['user_id']
            
            # Get filtered transactions
            if filter_type == "Tất cả":
                transactions = self.transaction_manager.get_all_transactions(user_id)
            else:
                transaction_type = 'income' if filter_type == "Thu nhập" else 'expense'
                transactions = self.transaction_manager.get_all_transactions(
                    user_id, 
                    transaction_type=transaction_type
                )
            
            # Load categories for each transaction
            for transaction in transactions:
                category_id = transaction.get('category_id')
                if category_id:
                    try:
                        category = self.category_manager.get_category_by_id(user_id, category_id)
                        if category:
                            transaction['category_name'] = category['name']
                        else:
                            transaction['category_name'] = 'Không phân loại'
                    except Exception as e:
                        print(f"Error getting category {category_id}: {str(e)}")
                        transaction['category_name'] = 'Không phân loại'
                else:
                    transaction['category_name'] = 'Không phân loại'
                    
            # Update table with enriched data
            self.transaction_table.update_transactions(transactions)
        except Exception as e:
            print(f"Error filtering transactions: {str(e)}")
            self.display_message(str(e), "error")

    def filter_budgets(self):
        """Filter budgets based on period"""
        filter_period = self.budget_period_filter.currentText()
        # Implementation will depend on your budget manager's capabilities
        self.load_budgets(period=filter_period.lower())

    def filter_notifications(self):
        """Filter notifications based on status"""
        filter_type = self.notification_filter.currentText()
        if filter_type == "Tất cả":
            self.load_notifications()
        else:
            filter_status = 'unread' if filter_type == "Chưa đọc" else 'important'
            notifications = self.notification_manager.get_user_notifications(
                self.current_user['user_id'],
                status=filter_status
            )
            self.notification_panel.clear()
            for notification in notifications:
                self.notification_panel.add_notification(notification)

    def mark_all_notifications_read(self):
        """Mark all notifications as read"""
        try:
            self.notification_manager.mark_all_as_read(self.current_user['user_id'])
            self.load_notifications()
            self.display_message("Đã đánh dấu tất cả thông báo là đã đọc")
        except Exception as e:
            self.display_message(str(e), "error")

    def update_report(self):
        """Update report content based on selected type and period"""
        report_type = self.report_type.currentText()
        period = self.report_period.currentText()
        
        try:
            report_data = self.report_manager.generate_report(
                self.current_user['user_id'],
                report_type=report_type,
                period=period
            )
            # Implementation of report visualization will depend on your reporting system
            self.display_report(report_data)
        except Exception as e:
            self.display_message(str(e), "error")

    def display_report(self, report_data):
        """Display report data in the report content area"""
        # Implementation will depend on your reporting system and visualization library
        pass

    def init_dashboard(self):
        """Initialize dashboard data"""
        if self.current_user:
            self.title_label.setText(f"Xin chào, {self.current_user['full_name']}")
            self.load_transactions()
            self.load_budgets()
            self.load_notifications()
            self.update_statistics()
            
    def load_transactions(self):
        """Load user's transactions"""
        try:
            # Get transactions
            transactions = self.transaction_manager.get_all_transactions(self.current_user['user_id'])
            
            # Load categories for each transaction
            for transaction in transactions:
                category_id = transaction.get('category_id')
                if category_id:
                    try:
                        category = self.category_manager.get_category_by_id(
                            self.current_user['user_id'], 
                            category_id
                        )
                        if category:
                            transaction['category_name'] = category['name']
                        else:
                            transaction['category_name'] = 'Không phân loại'
                    except Exception as e:
                        print(f"Error getting category {category_id}: {str(e)}")
                        transaction['category_name'] = 'Không phân loại'
                else:
                    transaction['category_name'] = 'Không phân loại'
            
            # Update the transaction table with the enriched data
            self.transaction_table.update_transactions(transactions)
        except Exception as e:
            print(f"Error loading transactions: {str(e)}")
            self.display_message("Lỗi khi tải dữ liệu giao dịch", "error")

    def load_budgets(self):
        """Load user's budgets"""
        try:
            budgets = self.budget_manager.get_user_budgets(self.current_user['user_id'])
            self.budget_table.setRowCount(len(budgets))
            
            for row, budget in enumerate(budgets):
                # Get category name
                category_name = budget.get('category_name', 'Unknown')
                
                # Calculate status
                spent_percentage = (budget.get('spent_amount', 0) / budget.get('amount', 1) * 100) if budget.get('amount', 0) > 0 else 0
                if spent_percentage >= 100:
                    status = "Vượt ngân sách"
                    status_style = "color: #e74c3c;"
                elif spent_percentage >= budget.get('alert_threshold', 80):
                    status = "Gần hạn mức"
                    status_style = "color: #f1c40f;"
                else:
                    status = "Tốt"
                    status_style = "color: #2ecc71;"
                
                # Add table row
                self.budget_table.setItem(row, 0, QTableWidgetItem(category_name))
                self.budget_table.setItem(row, 1, QTableWidgetItem(f"{budget.get('amount', 0):,.0f}"))
                self.budget_table.setItem(row, 2, QTableWidgetItem(f"{budget.get('spent_amount', 0):,.0f}"))
                self.budget_table.setItem(row, 3, QTableWidgetItem(f"{budget.get('remaining_amount', 0):,.0f}"))
                
                status_label = QLabel(status)
                status_label.setStyleSheet(status_style)
                status_label.setAlignment(Qt.AlignCenter)
                self.budget_table.setCellWidget(row, 4, status_label)
                
                # Actions
                actions_layout = QHBoxLayout()
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_layout.setSpacing(5)
                
                edit_btn = QPushButton("Sửa")
                edit_btn.clicked.connect(lambda checked, b=budget: self.show_edit_budget_dialog(b))
                
                delete_btn = QPushButton("Xóa")
                delete_btn.clicked.connect(lambda checked, b=budget: self.delete_budget(b))
                
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                
                actions_widget = QWidget()
                actions_widget.setLayout(actions_layout)
                self.budget_table.setCellWidget(row, 5, actions_widget)
            
            # Update budget chart
            self.budget_chart.update_chart(budgets)
            
        except Exception as e:
            print(f"Error loading budgets: {str(e)}")
            self.display_message("Lỗi khi tải dữ liệu ngân sách", "error")
        
    def load_notifications(self):
        """Load user's notifications"""
        notifications = self.notification_manager.get_user_notifications(self.current_user['user_id'])
        for notification in notifications:
            self.notification_panel.add_notification(notification)
            
    def update_statistics(self):
        """Update statistics panel"""
        try:
            # Get transactions
            transactions = self.transaction_manager.get_user_transactions(self.current_user['user_id'])
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
        
    def show_profile_dialog(self):
        """Show dialog to edit user profile"""
        dialog = ProfileDialog(self, self.current_user)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh dashboard data
            self.init_dashboard()
            self.display_message("Đã cập nhật thông tin thành công")

    def show_add_transaction_dialog(self):
        """Show dialog to add new transaction"""
        dialog = TransactionDialog(self, user_id=self.current_user['user_id'])
        if dialog.exec_() == QDialog.Accepted:
            self.load_transactions()
            self.load_budgets()
            self.update_statistics()
            self.display_message("Đã thêm giao dịch thành công")

    def show_edit_transaction_dialog(self, transaction):
        """Show dialog to edit transaction"""
        dialog = TransactionDialog(self, transaction, self.current_user['user_id'])
        if dialog.exec_() == QDialog.Accepted:
            self.load_transactions()
            self.load_budgets()
            self.update_statistics()
            self.display_message("Đã cập nhật giao dịch thành công")

    def delete_transaction(self, transaction):
        """Delete a transaction"""
        if QMessageBox.question(
            self,
            "Xác nhận xóa",
            "Bạn có chắc muốn xóa giao dịch này?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        ) == QMessageBox.Yes:
            try:
                if self.transaction_manager.delete_transaction(
                    self.current_user['user_id'],
                    transaction['transaction_id']
                ):
                    self.load_transactions()
                    self.load_budgets()
                    self.update_statistics()
                    self.display_message("Đã xóa giao dịch thành công")
                else:
                    self.display_message("Không thể xóa giao dịch.", "error")
            except Exception as e:
                self.display_message(str(e), "error")

    def show_add_budget_dialog(self):
        """Show dialog to add new budget"""
        dialog = BudgetDialog(self, user_id=self.current_user['user_id'])
        if dialog.exec_() == QDialog.Accepted:
            self.load_budgets()
            self.update_statistics()
            self.display_message("Đã thêm ngân sách thành công")

    def show_edit_budget_dialog(self, budget):
        """Show dialog to edit budget"""
        dialog = BudgetDialog(self, budget, self.current_user['user_id'])
        if dialog.exec_() == QDialog.Accepted:
            self.load_budgets()
            self.update_statistics()
            self.display_message("Đã cập nhật ngân sách thành công")

    def delete_budget(self, budget):
        """Delete a budget"""
        if QMessageBox.question(
            self,
            "Xác nhận xóa",
            "Bạn có chắc muốn xóa ngân sách này?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        ) == QMessageBox.Yes:
            try:
                if self.budget_manager.delete_budget(
                    self.current_user['user_id'],
                    budget['budget_id']
                ):
                    self.load_budgets()
                    self.update_statistics()
                    self.display_message("Đã xóa ngân sách thành công")
                else:
                    self.display_message("Không thể xóa ngân sách.", "error")
            except Exception as e:
                self.display_message(str(e), "error")

    def show_add_recurring_dialog(self):
        """Show dialog to add new recurring transaction"""
        dialog = RecurringTransactionDialog(self, user_id=self.current_user['user_id'])
        if dialog.exec_() == QDialog.Accepted:
            self.load_transactions()
            self.load_budgets()
            self.update_statistics()
            self.display_message("Đã thêm giao dịch định kỳ thành công")

    def show_change_password_dialog(self):
        """Show the change password dialog"""
        dialog = ChangePasswordDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.display_message("Đã đổi mật khẩu thành công")

    def handle_logout(self):
        """Handle logout button click"""
        if QMessageBox.question(
            self,
            "Xác nhận đăng xuất",
            "Bạn có chắc muốn đăng xuất?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        ) == QMessageBox.Yes:
            self.logout()  # Call base class logout method
            # Find the main window to show login frame
            main_window = self.window()
            if main_window:
                main_window.show_login_frame()
