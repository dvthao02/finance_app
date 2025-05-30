from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from datetime import datetime, timedelta

class StatisticsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the statistics panel UI"""
        layout = QHBoxLayout()
        layout.setSpacing(20)
        
        # Create stat boxes
        self.balance_box = self.create_stat_box("Số dư hiện tại", "0đ", "#2ecc71")
        self.income_box = self.create_stat_box("Thu nhập tháng này", "0đ", "#3498db")
        self.expense_box = self.create_stat_box("Chi tiêu tháng này", "0đ", "#e74c3c")
        self.budget_box = self.create_stat_box("Ngân sách còn lại", "0đ", "#f1c40f")
        
        # Store value labels for easy access
        self.balance_value = self.balance_box.findChild(QLabel, "value")
        self.income_value = self.income_box.findChild(QLabel, "value")
        self.expense_value = self.expense_box.findChild(QLabel, "value")
        self.budget_value = self.budget_box.findChild(QLabel, "value")
        self.budget_title = self.budget_box.findChild(QLabel, "title")
        
        layout.addWidget(self.balance_box)
        layout.addWidget(self.income_box)
        layout.addWidget(self.expense_box)
        layout.addWidget(self.budget_box)
        
        self.setLayout(layout)
        
        # Set panel style
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """)
        
    def create_stat_box(self, title, value, color):
        """Create a styled box for displaying a statistic"""
        box = QWidget()
        box.setObjectName("statBox")
        box.setStyleSheet(f"""
            QWidget#statBox {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 8px;
                padding: 15px;
                min-width: 200px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(title)
        title_label.setObjectName("title")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        
        # Value
        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.setAlignment(Qt.AlignCenter)
        box.setLayout(layout)
        
        return box
        
    def update_statistics(self, stats):
        """Update statistics display with new data"""
        try:
            # Update balance
            balance = stats.get('net_worth', 0)
            if self.balance_value:
                self.balance_value.setText(f"{balance:+,.0f}đ")
            
            # Update income
            income = stats.get('total_income', 0)
            if self.income_value:
                self.income_value.setText(f"{income:+,.0f}đ")
            
            # Update expenses
            expenses = stats.get('total_expenses', 0)
            if self.expense_value:
                self.expense_value.setText(f"{expenses:+,.0f}đ")
            
            # Update budget status
            budget_status = stats.get('budget_status', 'Tốt')
            remaining_budget = stats.get('remaining_budget', 0)
            
            if self.budget_title and self.budget_value:
                # Update budget box style
                if budget_status == 'Vượt ngân sách':
                    self.budget_box.setStyleSheet("""
                        QWidget#statBox {
                            background-color: #f8d7da;
                            border: 1px solid #f5c6cb;
                            border-radius: 4px;
                            padding: 10px;
                        }
                    """)
                elif budget_status == 'Gần hạn mức':
                    self.budget_box.setStyleSheet("""
                        QWidget#statBox {
                            background-color: #fff3cd;
                            border: 1px solid #ffeeba;
                            border-radius: 4px;
                            padding: 10px;
                        }
                    """)
                else:
                    self.budget_box.setStyleSheet("""
                        QWidget#statBox {
                            background-color: #d4edda;
                            border: 1px solid #c3e6cb;
                            border-radius: 4px;
                            padding: 10px;
                        }
                    """)
                
                # Update budget labels
                self.budget_title.setText(budget_status)
                self.budget_value.setText(f"{remaining_budget:+,.0f}đ")
            
        except Exception as e:
            print(f"Error updating statistics: {str(e)}")
            # Show error state
            error_text = "Lỗi cập nhật"
            for value_label in [self.balance_value, self.income_value, self.expense_value, self.budget_value]:
                if value_label:
                    value_label.setText(error_text)
