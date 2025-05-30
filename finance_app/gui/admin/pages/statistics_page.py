from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from finance_app.gui.base.base_widget import BaseWidget

class StatCard(QFrame):
    def __init__(self, title, value, color="#1a73e8", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #5f6368; font-size: 14px;")
        
        # Value
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Arial", 24, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        self.setLayout(layout)
        
class AdminStatisticsPage(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        """Initialize the statistics page UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Page title
        title = self.create_title_label("Thống kê tổng quan")
        layout.addWidget(title)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Create stat cards
        self.total_users_card = StatCard("Tổng số người dùng", "0")
        self.active_users_card = StatCard("Người dùng đang hoạt động", "0", "#2ecc71")
        self.total_transactions_card = StatCard("Tổng số giao dịch", "0", "#f39c12")
        self.total_budgets_card = StatCard("Tổng số ngân sách", "0", "#9b59b6")
        
        stats_layout.addWidget(self.total_users_card)
        stats_layout.addWidget(self.active_users_card)
        stats_layout.addWidget(self.total_transactions_card)
        stats_layout.addWidget(self.total_budgets_card)
        
        layout.addLayout(stats_layout)
        
        # System stats
        system_card = self.create_card()
        system_layout = QVBoxLayout()
        
        system_title = self.create_label("Thông tin hệ thống", size=18, bold=True)
        system_layout.addWidget(system_title)
        
        # Categories stats
        self.categories_label = self.create_label("Tổng số danh mục: 0")
        system_layout.addWidget(self.categories_label)
        
        # Notifications stats
        self.notifications_label = self.create_label("Tổng số thông báo: 0")
        system_layout.addWidget(self.notifications_label)
        
        system_card.setLayout(system_layout)
        layout.addWidget(system_card)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        self.setLayout(layout)
        
    def refresh_data(self):
        """Refresh statistics data"""
        if not self.parent or not self.parent.current_user_id:
            return
            
        try:
            # Get user statistics
            users = self.parent.user_manager.get_all_users()
            active_users = [u for u in users if u.get('is_active', True)]
            
            # Update user stats
            self.total_users_card.findChild(QLabel, "", Qt.FindChildOption.FindChildrenRecursively)[1].setText(str(len(users)))
            self.active_users_card.findChild(QLabel, "", Qt.FindChildOption.FindChildrenRecursively)[1].setText(str(len(active_users)))
            
            # Get transaction statistics
            transactions = self.parent.transaction_manager.get_all_transactions()
            self.total_transactions_card.findChild(QLabel, "", Qt.FindChildOption.FindChildrenRecursively)[1].setText(str(len(transactions)))
            
            # Get budget statistics
            budgets = self.parent.budget_manager.get_all_budgets()
            self.total_budgets_card.findChild(QLabel, "", Qt.FindChildOption.FindChildrenRecursively)[1].setText(str(len(budgets)))
            
            # Get category statistics
            categories = self.parent.category_manager.get_all_categories()
            self.categories_label.setText(f"Tổng số danh mục: {len(categories)}")
            
            # Get notification statistics
            notifications = self.parent.notification_manager.get_all_notifications()
            self.notifications_label.setText(f"Tổng số thông báo: {len(notifications)}")
            
        except Exception as e:
            self.parent.show_error(
                "Lỗi",
                f"Không thể tải dữ liệu thống kê: {str(e)}"
            ) 