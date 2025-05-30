from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from finance_app.gui.base.base_widget import BaseWidget
import os

class UserCategoriesPage(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.income_categories_label = None
        self.expense_categories_label = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the categories page UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Page title
        title = self.create_title_label("Danh mục")
        layout.addWidget(title)
        
        # Statistics cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Income Categories
        income_categories_card, self.income_categories_label = self.create_stat_card_with_label_ref(
            "Danh mục thu",
            "0",
            "income_icon.png",
            "#34a853"
        )
        stats_layout.addWidget(income_categories_card)
        
        # Expense Categories
        expense_categories_card, self.expense_categories_label = self.create_stat_card_with_label_ref(
            "Danh mục chi",
            "0",
            "expense_icon.png",
            "#ea4335"
        )
        stats_layout.addWidget(expense_categories_card)
        
        layout.addLayout(stats_layout)
        
        # Categories table
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(4)
        self.categories_table.setHorizontalHeaderLabels([
            "ID", "Tên danh mục", "Loại", "Mô tả"
        ])
        
        # Set column widths
        self.categories_table.horizontalHeader().setStretchLastSection(True)
        self.categories_table.setColumnWidth(0, 100)  # ID
        self.categories_table.setColumnWidth(1, 200)  # Name
        self.categories_table.setColumnWidth(2, 100)  # Type
        
        # Style the table
        self.categories_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Table container
        table_container = QFrame()
        table_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        table_layout = QVBoxLayout()
        table_layout.addWidget(self.categories_table)
        table_container.setLayout(table_layout)
        
        layout.addWidget(table_container)
        self.setLayout(layout)
        
        # Load categories - This will be called by refresh_data after user context is set
        # self.load_categories()
        
    def create_stat_card_with_label_ref(self, title, value, icon_name, color):
        """Create a statistics card and return the card and its value QLabel.
        
        Args:
            title (str): Card title
            value (str): Statistic value
            icon_name (str): Icon file name
            color (str): Accent color
        
        Returns:
            tuple: (QFrame, QLabel) The card frame and the value label
        """
        card = QFrame()
        card.setObjectName(f"stat_card_{title.replace(' ', '_').lower()}")
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        # Icon
        icon_label = QLabel()
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        icon_path = os.path.join(project_root, 'assets', icon_name)

        if os.path.exists(icon_path):
            icon_label.setPixmap(QIcon(icon_path).pixmap(32, 32))
        else:
            print(f"Warning: Icon not found at {icon_path}")
            icon_label.setText("?")

        layout.addWidget(icon_label)
        
        # Text
        text_layout = QVBoxLayout()
        
        value_label = QLabel(value)
        value_label.setObjectName(f"value_label_{title.replace(' ', '_').lower()}")
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        
        title_label = QLabel(title)
        title_label.setObjectName(f"title_label_{title.replace(' ', '_').lower()}")
        title_label.setStyleSheet("""
            QLabel {
                color: #5f6368;
                font-size: 14px;
            }
        """)
        
        text_layout.addWidget(value_label)
        text_layout.addWidget(title_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        card.setLayout(layout)
        return card, value_label

    def create_stat_card(self, title, value, icon_name, color):
        card, _ = self.create_stat_card_with_label_ref(title, value, icon_name, color)
        return card
        
    def load_categories(self):
        """Load categories into the table"""
        try:
            categories = self.parent.category_manager.get_all_categories(user_id=self.parent.current_user_id)
            
            # Update statistics
            income_categories = len([c for c in categories if c.get('type') == 'income'])
            expense_categories = len([c for c in categories if c.get('type') == 'expense'])
            
            # Update stat cards
            if self.income_categories_label:
                self.income_categories_label.setText(str(income_categories))
            if self.expense_categories_label:
                self.expense_categories_label.setText(str(expense_categories))
            
            # Clear table
            self.categories_table.setRowCount(0)
            
            # Add categories to table
            for category in categories:
                row = self.categories_table.rowCount()
                self.categories_table.insertRow(row)
                
                # Add category data
                self.categories_table.setItem(row, 0, QTableWidgetItem(category.get('category_id', '')))
                self.categories_table.setItem(row, 1, QTableWidgetItem(category.get('name', '')))
                
                # Type
                type_text = "Thu nhập" if category.get('type') == 'income' else "Chi tiêu"
                type_item = QTableWidgetItem(type_text)
                type_item.setTextAlignment(Qt.AlignCenter)
                if category.get('type') == 'income':
                    type_item.setForeground(Qt.darkGreen)
                else:
                    type_item.setForeground(Qt.red)
                self.categories_table.setItem(row, 2, type_item)
                
                # Description
                self.categories_table.setItem(row, 3, QTableWidgetItem(category.get('description', '')))
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể tải danh sách danh mục: {str(e)}",
                QMessageBox.Ok
            )
            
    def refresh_data(self):
        """Refresh category data, called when dashboard user context is set or updated."""
        if not self.parent or not self.parent.category_manager:
            print("UserCategoriesPage: Cannot refresh data, parent or category_manager not available.")
            return
        self.load_categories() 