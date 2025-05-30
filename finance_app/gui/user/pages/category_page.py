from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QWidget,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView, QMenu, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from finance_app.gui.base.base_widget import BaseWidget
from finance_app.gui.user.dialogs.user_category_dialog import UserCategoryDialog # Uncommented
import os

class UserCategoriesPage(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent # UserDashboard
        self.income_categories_label = None
        self.expense_categories_label = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Page header
        header_layout = QHBoxLayout()
        title = self.create_title_label("Danh mục của bạn")
        header_layout.addWidget(title)

        add_btn = self.create_primary_button("Thêm danh mục mới")
        add_btn.clicked.connect(self.add_category)
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)

        # Statistics cards (Simplified for user: just income/expense counts)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        income_card, self.income_categories_label = self.create_stat_card_with_label_ref(
            "Danh mục thu", "0", "income_icon.png", "#34a853")
        stats_layout.addWidget(income_card)

        expense_card, self.expense_categories_label = self.create_stat_card_with_label_ref(
            "Danh mục chi", "0", "expense_icon.png", "#ea4335")
        stats_layout.addWidget(expense_card)
        layout.addLayout(stats_layout)

        # Categories table
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(6) # Icon, Name, Type, Description, Owner, Actions
        self.categories_table.setHorizontalHeaderLabels([
            "Icon", "Tên danh mục", "Loại", "Mô tả", "Nguồn", "Thao tác"
        ])
        self.categories_table.horizontalHeader().setStretchLastSection(True)
        self.categories_table.setColumnWidth(0, 60)  # Icon
        self.categories_table.setColumnWidth(1, 200) # Name
        self.categories_table.setColumnWidth(2, 100) # Type
        self.categories_table.setColumnWidth(3, 250) # Description
        self.categories_table.setColumnWidth(4, 100) # Owner
        # Column 5 (Actions) will take remaining space

        self.categories_table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 10px; }
            QTableWidget::item { padding: 10px; }
            QHeaderView::section { background-color: #f8f9fa; padding: 10px; border: none; font-weight: bold; color: #333; }
        """)
        layout.addWidget(self.categories_table)
        self.setLayout(layout)

    def create_stat_card_with_label_ref(self, title, value, icon_name, color):
        # This method can be copied or referenced from AdminCategoriesPage or BaseWidget if generic enough
        # For now, a simplified version or assume it exists in BaseWidget
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
        icon_label = QLabel()
        # Simplified icon logic for now, ideally use get_asset_path from BaseWidget
        # Attempt to use get_asset_path if available, otherwise default text
        if hasattr(self, 'get_asset_path'):
            icon_path = self.get_asset_path(icon_name)
            if icon_path and os.path.exists(icon_path):
                icon_label.setPixmap(QIcon(icon_path).pixmap(32,32))
            else:
                icon_label.setText("?") # Fallback if path is bad or icon not found
        else:
            icon_label.setText("?") 
        layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        value_label = QLabel(value)
        value_label.setObjectName(f"value_label_{title.replace(' ', '_').lower()}")
        value_label.setStyleSheet(f"QLabel {{ color: {color}; font-size: 24px; font-weight: bold; }}")
        title_label_widget = QLabel(title)
        title_label_widget.setStyleSheet("QLabel {{ color: #5f6368; font-size: 14px; }}")
        
        text_layout.addWidget(value_label)
        text_layout.addWidget(title_label_widget)
        layout.addLayout(text_layout)
        layout.addStretch()
        card.setLayout(layout)
        return card, value_label

    def load_categories(self):
        try:
            if not self.parent or not hasattr(self.parent, 'category_manager') or not hasattr(self.parent, 'current_user_id'):
                # print("UserCategoriesPage: Parent, category_manager, or current_user_id not available.")
                return

            current_user_id = self.parent.current_user_id
            categories = self.parent.category_manager.get_all_categories(user_id=current_user_id, active_only=False)
            
            income_count = len([c for c in categories if c.get('type') == 'income'])
            expense_count = len([c for c in categories if c.get('type') == 'expense'])
            if self.income_categories_label: self.income_categories_label.setText(str(income_count))
            if self.expense_categories_label: self.expense_categories_label.setText(str(expense_count))

            self.categories_table.setRowCount(0)
            for category in categories:
                row = self.categories_table.rowCount()
                self.categories_table.insertRow(row)
                
                self.categories_table.setItem(row, 0, QTableWidgetItem(category.get('icon', '📝')))
                self.categories_table.setItem(row, 1, QTableWidgetItem(category.get('name', '')))
                type_text = "Thu nhập" if category.get('type') == 'income' else "Chi tiêu"
                self.categories_table.setItem(row, 2, QTableWidgetItem(type_text))
                self.categories_table.setItem(row, 3, QTableWidgetItem(category.get('description', '')))
                
                owner = "Hệ thống" if category.get('user_id') == "system" else "Của bạn"
                owner_item = QTableWidgetItem(owner)
                self.categories_table.setItem(row, 4, owner_item)

                self.add_actions_to_row(row, category, current_user_id)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh mục: {str(e)}")

    def add_actions_to_row(self, row_num, category_data, current_user_id):
        actions_widget = QWidget()
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0,0,0,0)
        actions_layout.setSpacing(5)

        is_user_owned = category_data.get('user_id') == current_user_id
        # System categories are not editable by non-admins, CategoryManager handles this for edit/delete attempts.
        # UserCategoriesPage should still disable buttons for system categories for better UX.
        can_modify = is_user_owned # Only user-owned categories can be modified by user from this page

        edit_btn = QPushButton("Sửa")
        edit_btn.setIcon(QIcon(self.get_asset_path('edit_icon.png')))
        edit_btn.setToolTip("Chỉnh sửa danh mục")
        edit_btn.setEnabled(can_modify)
        edit_btn.clicked.connect(lambda _, cat=category_data: self.edit_category(cat))
        actions_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Xóa")
        delete_btn.setIcon(QIcon(self.get_asset_path('delete_icon.png')))
        delete_btn.setToolTip("Xóa danh mục")
        delete_btn.setEnabled(can_modify)
        delete_btn.clicked.connect(lambda _, cat=category_data: self.delete_category(cat))
        actions_layout.addWidget(delete_btn)
        
        actions_layout.addStretch()
        actions_widget.setLayout(actions_layout)
        self.categories_table.setCellWidget(row_num, 5, actions_widget)

    def add_category(self):
        dialog = UserCategoryDialog(self) 
        if dialog.exec_() == UserCategoryDialog.Accepted:
            self.load_categories()
        # QMessageBox.information(self, "Thông báo", "Chức năng thêm danh mục cho người dùng sẽ được triển khai.")

    def edit_category(self, category):
        dialog = UserCategoryDialog(self, category_data=category)
        if dialog.exec_() == UserCategoryDialog.Accepted:
            self.load_categories()
        # QMessageBox.information(self, "Thông báo", "Chức năng sửa danh mục cho người dùng sẽ được triển khai.")

    def delete_category(self, category):
        reply = QMessageBox.question(self, "Xác nhận xóa", 
                                   f"Bạn có chắc muốn xóa danh mục '{category.get('name')}'?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                # Permission already checked by CategoryManager
                # User is admin = False for UserDashboard context
                self.parent.category_manager.delete_category(category.get('category_id'), self.parent.current_user_id, False)
                self.load_categories()
                QMessageBox.information(self, "Thành công", "Đã xóa danh mục.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa danh mục: {str(e)}")

    def refresh_data(self):
        if hasattr(self.parent, 'current_user') and self.parent.current_user:
            self.load_categories()
        else:
            # print("UserCategoriesPage: current_user not available in parent for refresh_data.")
            self.categories_table.setRowCount(0) # Clear table if no user
            if self.income_categories_label: self.income_categories_label.setText("0")
            if self.expense_categories_label: self.expense_categories_label.setText("0")

# REMOVE ANY TRAILING MARKERS LIKE </rewritten_file> THAT MIGHT HAVE BEEN ACCIDENTALLY INSERTED 