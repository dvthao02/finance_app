from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView, QMenu)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from finance_app.gui.admin.dialogs.category_dialog import CategoryDialog
import os
from finance_app.gui.base.base_widget import BaseWidget

class AdminCategoriesPage(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.total_categories_label = None
        self.income_categories_label = None
        self.expense_categories_label = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the categories page UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Page header
        header_layout = QHBoxLayout()
        
        # Title
        title = self.create_title_label("Quản lý danh mục")
        header_layout.addWidget(title)
        
        # Add Category button
        add_btn = self.create_primary_button("Thêm danh mục")
        add_btn.clicked.connect(self.add_category)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Statistics cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Total Categories
        total_categories_card, self.total_categories_label = self.create_stat_card_with_label_ref(
            "Tổng danh mục",
            "0",
            "categories_icon.png",
            "#1a73e8"
        )
        stats_layout.addWidget(total_categories_card)
        
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
        self.categories_table.setColumnCount(7)
        self.categories_table.setHorizontalHeaderLabels([
            "Icon", "Tên danh mục", "Loại", "Mô tả", 
            "Màu (Hex)", "Trạng thái", "Thao tác" 
        ])
        
        # Set column widths
        self.categories_table.horizontalHeader().setStretchLastSection(True)
        self.categories_table.setColumnWidth(0, 80)   # Icon (Increased width for larger icon)
        self.categories_table.setColumnWidth(1, 200)  # Name
        self.categories_table.setColumnWidth(2, 100)  # Type
        self.categories_table.setColumnWidth(3, 250)  # Description
        self.categories_table.setColumnWidth(4, 100)  # Color
        self.categories_table.setColumnWidth(5, 100)  # Status
        # Column 6 (Actions) will take remaining space
        
        self.categories_table.horizontalHeader().setVisible(True) # Explicitly show header

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
                color: #333;
            }
        """)
        
        layout.addWidget(self.categories_table) # Add table directly
        
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
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
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
            # Admin should see all their categories and system categories, including inactive ones.
            categories = self.parent.category_manager.get_all_categories(
                user_id=self.parent.current_user_id, 
                active_only=False
            )
            
            if not categories:
                print("AdminCategoriesPage.load_categories: No categories returned from manager.") # Add log
            
            # Update statistics
            total_categories = len(categories)
            income_categories = len([c for c in categories if c.get('type') == 'income'])
            expense_categories = len([c for c in categories if c.get('type') == 'expense'])
            
            # Update stat cards
            if self.total_categories_label:
                self.total_categories_label.setText(str(total_categories))
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
                
                # Column 0: Icon (moved from column 4)
                icon_text = category.get('icon', '📝') # Default icon if none
                icon_item = QTableWidgetItem(icon_text)
                icon_item.setTextAlignment(Qt.AlignCenter)
                font = icon_item.font()
                font.setPointSize(16) # Increase point size for icon
                icon_item.setFont(font)
                self.categories_table.setItem(row, 0, icon_item)

                # Column 1: Name (was column 1)
                self.categories_table.setItem(row, 1, QTableWidgetItem(category.get('name', '')))
                
                # Column 2: Type (was column 2)
                type_text = "Thu nhập" if category.get('type') == 'income' else "Chi tiêu"
                type_item = QTableWidgetItem(type_text)
                type_item.setTextAlignment(Qt.AlignCenter)
                if category.get('type') == 'income':
                    type_item.setForeground(Qt.darkGreen)
                else:
                    type_item.setForeground(Qt.red)
                self.categories_table.setItem(row, 2, type_item)
                
                # Column 3: Description (was column 3)
                self.categories_table.setItem(row, 3, QTableWidgetItem(category.get('description', '')))

                # Column 4: Color (was column 5)
                color_item = QTableWidgetItem(category.get('color', ''))
                color_item.setTextAlignment(Qt.AlignCenter)
                self.categories_table.setItem(row, 4, color_item)

                # Column 5: Status (was column 6)
                status_text = "Hoạt động" if category.get('is_active', True) else "Không hoạt động"
                status_item = QTableWidgetItem(status_text)
                status_item.setTextAlignment(Qt.AlignCenter)
                if category.get('is_active', True):
                    status_item.setForeground(Qt.darkGreen) # Or some other indication
                else:
                    status_item.setForeground(Qt.red) # Or some other indication
                self.categories_table.setItem(row, 5, status_item)
                
                # Column 6: Actions (was column 7)
                self.add_actions_to_row(row, category)
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể tải danh sách danh mục: {str(e)}",
                QMessageBox.Ok
            )
            
    def add_category(self):
        """Add a new category"""
        dialog = CategoryDialog(self)
        if dialog.exec_() == CategoryDialog.Accepted:
            self.load_categories()
            
    def edit_category(self, category):
        """Edit a category
        
        Args:
            category (dict): Category data dictionary
        """
        dialog = CategoryDialog(self, category)
        if dialog.exec_() == CategoryDialog.Accepted:
            self.load_categories()
            
    def delete_category(self, category):
        """Delete a category
        
        Args:
            category (dict): Category data dictionary
        """
        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa danh mục '{category.get('name')}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                current_user_id = self.parent.current_user_id
                is_admin = self.parent.current_user.get('is_admin', False)
                self.parent.category_manager.delete_category(category.get('category_id'), current_user_id, is_admin)
                self.load_categories()
                QMessageBox.information(
                    self,
                    "Thành công",
                    "Đã xóa danh mục thành công",
                    QMessageBox.Ok
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Lỗi",
                    f"Không thể xóa danh mục: {str(e)}",
                    QMessageBox.Ok
                )
                
    def add_actions_to_row(self, row_num, category_data):
        """Add Edit/Delete action buttons to the specified row."""
        actions_btn = QPushButton("...")
        actions_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f1f3f4;
                border-radius: 4px;
            }
        """)
        
        menu = QMenu()
        edit_action = menu.addAction("Chỉnh sửa")
        edit_action.triggered.connect(lambda checked, c=category_data: self.edit_category(c))
        
        menu.addSeparator()
        delete_action = menu.addAction("Xóa")
        delete_action.triggered.connect(lambda checked, c=category_data: self.delete_category(c))
        
        actions_btn.setMenu(menu)
        self.categories_table.setCellWidget(row_num, 6, actions_btn) # Column 6 for actions

    def refresh_data(self):
        """Refresh category data, called when dashboard user context is set or updated."""
        if not self.parent or not self.parent.category_manager:
            print("AdminCategoriesPage: Cannot refresh data, parent or category_manager not available.")
            return
        self.load_categories() 