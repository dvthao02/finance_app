from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QSpacerItem, QSizePolicy, QMessageBox,
                             QComboBox, QLineEdit, QDateEdit, QDialog, QFormLayout)
from PyQt5.QtCore import Qt, QDate
from finance_app.gui.components.statistics_panel import StatisticsPanel
from finance_app.gui.components.budget_chart import BudgetChart
from finance_app.gui.components.transaction_table import TransactionTable
from finance_app.gui.components.notification_panel import NotificationPanel
from finance_app.gui.frmBase import FrmBase
from finance_app.gui.user.change_password_dialog import ChangePasswordDialog

class UserDashboard(FrmBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        self.central_widget.setLayout(main_layout)
        
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
        
        # Profile button
        profile_button = QPushButton("Hồ sơ")
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
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(profile_button)
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
        
        # Transactions tab
        transactions_tab = QWidget()
        transactions_layout = QVBoxLayout()
        transactions_tab.setLayout(transactions_layout)
        
        # Transaction controls
        transaction_controls = QHBoxLayout()
        add_transaction_btn = QPushButton("Thêm giao dịch")
        add_transaction_btn.clicked.connect(self.show_add_transaction_dialog)
        transaction_controls.addWidget(add_transaction_btn)
        transaction_controls.addStretch()
        transactions_layout.addLayout(transaction_controls)
        
        # Transaction table
        self.transaction_table = TransactionTable()
        transactions_layout.addWidget(self.transaction_table)
        
        # Budgets tab
        budgets_tab = QWidget()
        budgets_layout = QVBoxLayout()
        budgets_tab.setLayout(budgets_layout)
        
        # Budget controls
        budget_controls = QHBoxLayout()
        add_budget_btn = QPushButton("Thêm ngân sách")
        add_budget_btn.clicked.connect(self.show_add_budget_dialog)
        budget_controls.addWidget(add_budget_btn)
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
        
        # Reports tab
        reports_tab = QWidget()
        reports_layout = QVBoxLayout()
        reports_tab.setLayout(reports_layout)
        
        # TODO: Add report widgets here
        
        # Notifications tab
        notifications_tab = QWidget()
        notifications_layout = QVBoxLayout()
        notifications_tab.setLayout(notifications_layout)
        
        # Add notification panel
        self.notification_panel = NotificationPanel()
        notifications_layout.addWidget(self.notification_panel)
        
        # Add tabs
        tabs.addTab(transactions_tab, "Giao dịch")
        tabs.addTab(budgets_tab, "Ngân sách")
        tabs.addTab(reports_tab, "Báo cáo")
        tabs.addTab(notifications_tab, "Thông báo")
        
        main_layout.addWidget(tabs)
        
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
        transactions = self.transaction_manager.get_user_transactions(self.current_user['user_id'])
        self.transaction_table.update_transactions(transactions)
        
    def load_budgets(self):
        """Load user's budgets"""
        budgets = self.budget_manager.get_budgets_by_user(self.current_user['user_id'])
        self.budget_table.setRowCount(len(budgets))
        
        budget_data = {}  # For pie chart
        
        for row, budget in enumerate(budgets):
            # Get category name
            category = self.category_manager.get_category_by_id(
                self.current_user['user_id'],
                budget['category_id']
            )
            category_name = category['name'] if category else 'Unknown'
            
            # Add to pie chart data
            budget_data[category_name] = budget['amount']
            
            # Calculate status
            spent_percentage = (budget['spent_amount'] / budget['amount'] * 100) if budget['amount'] > 0 else 0
            if spent_percentage >= 100:
                status = "Vượt ngân sách"
                status_style = "color: #e74c3c;"
            elif spent_percentage >= budget['alert_threshold']:
                status = "Gần hạn mức"
                status_style = "color: #f1c40f;"
            else:
                status = "Tốt"
                status_style = "color: #2ecc71;"
            
            # Add table row
            self.budget_table.setItem(row, 0, QTableWidgetItem(category_name))
            self.budget_table.setItem(row, 1, QTableWidgetItem(f"{budget['amount']:,.0f}"))
            self.budget_table.setItem(row, 2, QTableWidgetItem(f"{budget['spent_amount']:,.0f}"))
            self.budget_table.setItem(row, 3, QTableWidgetItem(f"{budget['remaining_amount']:,.0f}"))
            
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setData(Qt.UserRole, spent_percentage)
            status_label = QLabel(status)
            status_label.setStyleSheet(status_style)
            status_label.setAlignment(Qt.AlignCenter)
            self.budget_table.setCellWidget(row, 4, status_label)
            
            # Actions
            actions_layout = QHBoxLayout()
            edit_btn = QPushButton("Sửa")
            edit_btn.clicked.connect(lambda b=budget: self.show_edit_budget_dialog(b))
            
            delete_btn = QPushButton("Xóa")
            delete_btn.clicked.connect(lambda b=budget: self.delete_budget(b))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.budget_table.setCellWidget(row, 5, actions_widget)
            
        # Update budget chart
        self.budget_chart.update_chart(budget_data)
        
    def load_notifications(self):
        """Load user's notifications"""
        notifications = self.notification_manager.get_user_notifications(self.current_user['user_id'])
        for notification in notifications:
            self.notification_panel.add_notification(notification)
            
    def update_statistics(self):
        """Update statistics panel"""
        transactions = self.transaction_manager.get_user_transactions(self.current_user['user_id'])
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        net_worth = total_income - total_expenses
        
        # Calculate budget status
        budgets = self.budget_manager.get_budgets_by_user(self.current_user['user_id'])
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
        
    def show_add_transaction_dialog(self):
        """Show dialog to add new transaction"""
        dialog = TransactionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_transactions()
            self.load_budgets()
            self.update_statistics()
            
    def show_edit_transaction_dialog(self, transaction):
        """Show dialog to edit transaction"""
        dialog = TransactionDialog(self, transaction)
        if dialog.exec_() == QDialog.Accepted:
            self.load_transactions()
            self.load_budgets()
            self.update_statistics()
            
    def show_add_budget_dialog(self):
        """Show dialog to add new budget"""
        dialog = BudgetDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_budgets()
            self.update_statistics()
            
    def show_edit_budget_dialog(self, budget):
        """Show dialog to edit budget"""
        dialog = BudgetDialog(self, budget)
        if dialog.exec_() == QDialog.Accepted:
            self.load_budgets()
            self.update_statistics()
            
    def delete_budget(self, budget):
        """Delete a budget"""
        if QMessageBox.question(
            self,
            "Xác nhận xóa",
            "Bạn có chắc muốn xóa ngân sách này?"
        ) == QMessageBox.Yes:
            try:
                self.budget_manager.delete_budget(self.current_user['user_id'], budget['budget_id'])
                self.load_budgets()
                self.update_statistics()
                self.display_message("Đã xóa ngân sách thành công")
            except Exception as e:
                self.display_message(str(e), "error")
                
    def show_profile_dialog(self):
        """Show dialog to edit user profile"""
        dialog = ProfileDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.init_dashboard()  # Reload dashboard to reflect any changes
            
    def handle_logout(self):
        """Handle logout button click"""
        if QMessageBox.question(
            self,
            "Xác nhận đăng xuất",
            "Bạn có chắc muốn đăng xuất?"
        ) == QMessageBox.Yes:
            self.logout()
            self.parent().show_login_frame()


class TransactionDialog(QDialog):
    def __init__(self, parent=None, transaction=None):
        super().__init__(parent)
        self.transaction = transaction
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Thêm giao dịch mới" if not self.transaction else "Sửa giao dịch")
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Amount
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Nhập số tiền")
        if self.transaction:
            self.amount_input.setText(str(self.transaction['amount']))
        layout.addRow("Số tiền:", self.amount_input)
          # Category  
        self.category_combo = QComboBox()
        categories = self.parent().category_manager.get_all_categories(self.parent().current_user['user_id'])
        for category in categories:
            self.category_combo.addItem(category['name'], category['category_id'])
        if self.transaction:
            index = self.category_combo.findData(self.transaction['category_id'])
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        layout.addRow("Danh mục:", self.category_combo)
        
        # Date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        if self.transaction:
            self.date_input.setDate(QDate.fromString(self.transaction['date'], "yyyy-MM-dd"))
        layout.addRow("Ngày:", self.date_input)
        
        # Description
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Nhập mô tả")
        if self.transaction:
            self.description_input.setText(self.transaction['description'])
        layout.addRow("Mô tả:", self.description_input)
        
        # Buttons
        button_box = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        button_box.addWidget(save_btn)
        button_box.addWidget(cancel_btn)
        layout.addRow(button_box)
        

class BudgetDialog(QDialog):
    def __init__(self, parent=None, budget=None):
        super().__init__(parent)
        self.budget = budget
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Thêm ngân sách mới" if not self.budget else "Sửa ngân sách")
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Category
        self.category_combo = QComboBox()
        categories = self.parent().category_manager.get_all_categories()
        for category in categories:
            self.category_combo.addItem(category['name'], category['category_id'])
        if self.budget:
            index = self.category_combo.findData(self.budget['category_id'])
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        layout.addRow("Danh mục:", self.category_combo)
        
        # Amount
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Nhập hạn mức")
        if self.budget:
            self.amount_input.setText(str(self.budget['amount']))
        layout.addRow("Hạn mức:", self.amount_input)
        
        # Alert threshold
        self.threshold_input = QLineEdit()
        self.threshold_input.setPlaceholderText("Nhập ngưỡng cảnh báo (%)")
        if self.budget:
            self.threshold_input.setText(str(self.budget['alert_threshold']))
        else:
            self.threshold_input.setText("80")  # Default value
        layout.addRow("Ngưỡng cảnh báo (%):", self.threshold_input)
        
        # Period
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Hàng tháng", "Hàng năm"])
        if self.budget:
            self.period_combo.setCurrentText(
                "Hàng năm" if self.budget['period'] == 'yearly' else "Hàng tháng"
            )
        layout.addRow("Kỳ hạn:", self.period_combo)
        
        # Auto renew
        self.auto_renew_combo = QComboBox()
        self.auto_renew_combo.addItems(["Có", "Không"])
        if self.budget:
            self.auto_renew_combo.setCurrentText("Có" if self.budget['auto_renew'] else "Không")
        layout.addRow("Tự động gia hạn:", self.auto_renew_combo)
        
        # Notes
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Nhập ghi chú")
        if self.budget:
            self.notes_input.setText(self.budget['notes'])
        layout.addRow("Ghi chú:", self.notes_input)
        
        # Buttons
        button_box = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        button_box.addWidget(save_btn)
        button_box.addWidget(cancel_btn)
        layout.addRow(button_box)


class ProfileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user = parent.current_user
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Thông tin cá nhân")
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Full name
        self.fullname_input = QLineEdit()
        self.fullname_input.setText(self.user['full_name'])
        layout.addRow("Họ và tên:", self.fullname_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setText(self.user['email'])
        layout.addRow("Email:", self.email_input)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setText(self.user['phone'])
        layout.addRow("Số điện thoại:", self.phone_input)
        
        # Date of birth
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        if self.user['date_of_birth']:
            self.dob_input.setDate(QDate.fromString(self.user['date_of_birth'], "yyyy-MM-dd"))
        layout.addRow("Ngày sinh:", self.dob_input)
        
        # Address
        self.address_input = QLineEdit()
        self.address_input.setText(self.user['address'])
        layout.addRow("Địa chỉ:", self.address_input)
        
        # Change password button
        change_pass_btn = QPushButton("Đổi mật khẩu")
        change_pass_btn.clicked.connect(self.show_change_password_dialog)
        layout.addRow(change_pass_btn)
        
        # Buttons
        button_box = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.save_profile)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        button_box.addWidget(save_btn)
        button_box.addWidget(cancel_btn)
        layout.addRow(button_box)
        
    def save_profile(self):
        """Save profile changes"""
        try:
            self.parent().user_manager.update_user_info(
                self.user['username'],
                full_name=self.fullname_input.text(),
                email=self.email_input.text(),
                phone=self.phone_input.text(),
                date_of_birth=self.dob_input.date().toString("yyyy-MM-dd"),
                address=self.address_input.text()
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
            
    def show_change_password_dialog(self):
        """Show dialog to change password"""
        dialog = ChangePasswordDialog(self)
        dialog.exec_()
