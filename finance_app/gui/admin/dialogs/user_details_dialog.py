from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QTabWidget, QWidget, QFrame, QScrollArea)
from PyQt5.QtCore import Qt
from finance_app.gui.base.base_widget import BaseWidget
from finance_app.gui.components.statistics_panel import StatisticsPanel
from finance_app.gui.components.budget_chart import BudgetChart
from finance_app.gui.components.transaction_table import TransactionTable

class UserDetailsDialog(QDialog, BaseWidget):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data
        # Store value labels for stat cards
        self.total_transactions_value_label = None
        self.total_budgets_value_label = None
        self.total_categories_value_label = None
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle(f"Chi tiết người dùng - {self.user_data.get('username', '')}")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # User info section
        info_card = self.create_card()
        info_layout = QHBoxLayout()
        
        # Avatar and basic info
        basic_info = QVBoxLayout()
        basic_info.setSpacing(10)
        
        # Username
        username_label = self.create_label(
            f"Tên đăng nhập: {self.user_data.get('username', '')}",
            bold=True,
            size=16
        )
        basic_info.addWidget(username_label)
        
        # Full name
        name_label = self.create_label(
            f"Họ tên: {self.user_data.get('full_name', '')}",
            size=14
        )
        basic_info.addWidget(name_label)
        
        # Email
        email_label = self.create_label(
            f"Email: {self.user_data.get('email', '')}",
            size=14
        )
        basic_info.addWidget(email_label)
        
        # Role
        role = "Admin" if self.user_data.get('is_admin') else "User"
        role_label = self.create_label(
            f"Loại tài khoản: {role}",
            size=14
        )
        basic_info.addWidget(role_label)
        
        # Status
        status = "Hoạt động" if self.user_data.get('is_active', True) else "Đã khóa"
        status_label = self.create_label(
            f"Trạng thái: {status}",
            size=14,
            color="#2ecc71" if self.user_data.get('is_active', True) else "#e74c3c"
        )
        basic_info.addWidget(status_label)
        
        info_layout.addLayout(basic_info)
        info_layout.addStretch()
        
        # Quick stats
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Create stat cards
        self.total_transactions, self.total_transactions_value_label = self.create_stat_card_with_label_ref(
            "Tổng giao dịch",
            "0",
            "#1a73e8"
        )
        self.total_budgets, self.total_budgets_value_label = self.create_stat_card_with_label_ref(
            "Tổng ngân sách",
            "0",
            "#2ecc71"
        )
        self.total_categories, self.total_categories_value_label = self.create_stat_card_with_label_ref(
            "Tổng danh mục",
            "0",
            "#f39c12"
        )
        
        stats_layout.addWidget(self.total_transactions)
        stats_layout.addWidget(self.total_budgets)
        stats_layout.addWidget(self.total_categories)
        
        info_layout.addLayout(stats_layout)
        info_card.setLayout(info_layout)
        layout.addWidget(info_card)
        
        # Tabs for detailed information
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background: white;
                padding: 20px;
            }
            QTabBar::tab {
                padding: 10px 20px;
                margin-right: 5px;
                border: none;
                background: #f5f6f7;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: #1a73e8;
                color: white;
            }
        """)
        
        # Statistics tab
        stats_tab = QWidget()
        stats_layout = QVBoxLayout()
        
        # Add statistics panel
        self.stats_panel = StatisticsPanel()
        stats_layout.addWidget(self.stats_panel)
        
        # Add budget chart
        self.budget_chart = BudgetChart()
        stats_layout.addWidget(self.budget_chart)
        
        stats_tab.setLayout(stats_layout)
        tabs.addTab(stats_tab, "Thống kê")
        
        # Transactions tab
        transactions_tab = QWidget()
        transactions_layout = QVBoxLayout()
        
        # Add transactions table
        self.transactions_table = TransactionTable()
        transactions_layout.addWidget(self.transactions_table)
        
        transactions_tab.setLayout(transactions_layout)
        tabs.addTab(transactions_tab, "Giao dịch")
        
        # Add tabs to layout
        layout.addWidget(tabs)
        
        self.setLayout(layout)
        
    def create_stat_card_with_label_ref(self, title, value, color):
        """Create a statistics card and return the card and its value QLabel."""
        card = QFrame()
        card.setObjectName(f"stat_card_ud_{title.replace(' ', '_').lower()}") # Unique object name prefix
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # Title
        title_label = self.create_label(title, color="#5f6368", size=12)
        title_label.setObjectName(f"title_label_ud_{title.replace(' ', '_').lower()}")
        
        # Value
        value_label = self.create_label(value, color=color, size=24, bold=True)
        value_label.setObjectName(f"value_label_ud_{title.replace(' ', '_').lower()}")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)
        
        return card, value_label

    def create_stat_card(self, title, value, color):
        card, _ = self.create_stat_card_with_label_ref(title, value, color)
        return card
        
    def load_data(self):
        """Load user statistics and data"""
        if not self.user_data or not self.parent:
            return
            
        try:
            user_id = self.user_data.get('user_id')
            
            # Get transaction statistics
            transactions = self.parent.parent.transaction_manager.get_user_transactions(user_id)
            if self.total_transactions_value_label: self.total_transactions_value_label.setText(str(len(transactions)))
            
            # Get budget statistics
            budgets = self.parent.parent.budget_manager.get_user_budgets(user_id)
            if self.total_budgets_value_label: self.total_budgets_value_label.setText(str(len(budgets)))
            
            # Get category statistics
            # Note: get_user_categories might not exist, or might not be what's intended here.
            # Assuming it returns a list of categories specific to the user (excluding system).
            categories = self.parent.parent.category_manager.get_all_categories(user_id=user_id, active_only=True) # Or a more specific method
            if self.total_categories_value_label: self.total_categories_value_label.setText(str(len(categories)))
            
            # Update statistics panel
            self.stats_panel.update_data(user_id)
            
            # Update budget chart
            self.budget_chart.update_data(user_id)
            
            # Update transactions table
            self.transactions_table.load_transactions(user_id)
            
        except Exception as e:
            # Use a generic message box method if available, or print
            print(f"Error loading user details: {str(e)}") # Fallback
            self.show_message_box(
                "Lỗi",
                f"Không thể tải dữ liệu chi tiết người dùng: {str(e)}",
                level='critical'
            ) 