from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QTextEdit, QPushButton, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt

class UserCategoryDialog(QDialog):
    def __init__(self, parent=None, category_data=None):
        super().__init__(parent) # parent is UserCategoriesPage
        self.parent_page = parent 
        self.category_data = category_data
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Thêm danh mục mới" if not self.category_data else "Chỉnh sửa danh mục")
        self.setMinimumSize(500, 420)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        # Basic styling, can be enhanced
        self.setStyleSheet("QDialog { background-color: white; }")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Name
        name_label = QLabel("Tên danh mục *")
        self.name_edit = QLineEdit()
        if self.category_data: self.name_edit.setText(self.category_data.get('name', ''))
        layout.addWidget(name_label)
        layout.addWidget(self.name_edit)
        
        # Type
        type_label = QLabel("Loại danh mục *")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Thu nhập", "Chi tiêu"])
        if self.category_data:
            self.type_combo.setCurrentText("Thu nhập" if self.category_data.get('type') == 'income' else "Chi tiêu")
        layout.addWidget(type_label)
        layout.addWidget(self.type_combo)
        
        # Description
        desc_label = QLabel("Mô tả")
        self.desc_edit = QTextEdit()
        if self.category_data: self.desc_edit.setText(self.category_data.get('description', ''))
        layout.addWidget(desc_label)
        layout.addWidget(self.desc_edit)

        # Icon & Color (Simplified for now, can be more sophisticated like AdminDialog)
        icon_label = QLabel("Icon (emoji/ký tự):")
        self.icon_edit = QLineEdit()
        if self.category_data: self.icon_edit.setText(self.category_data.get('icon', ''))
        layout.addWidget(icon_label)
        layout.addWidget(self.icon_edit)

        color_label = QLabel("Màu (Hex, ví dụ: #RRGGBB):")
        self.color_edit = QLineEdit()
        if self.category_data: self.color_edit.setText(self.category_data.get('color', ''))
        layout.addWidget(color_label)
        layout.addWidget(self.color_edit)

        # Is Active Checkbox (Users can deactivate their own categories)
        self.is_active_checkbox = QCheckBox("Đang hoạt động")
        self.is_active_checkbox.setChecked(True) # Default to active
        if self.category_data:
            self.is_active_checkbox.setChecked(self.category_data.get('is_active', True))
        layout.addWidget(self.is_active_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.save_category)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def save_category(self):
        name = self.name_edit.text().strip()
        type_text = self.type_combo.currentText()
        description = self.desc_edit.toPlainText().strip()
        icon = self.icon_edit.text().strip()
        color = self.color_edit.text().strip()
        is_active = self.is_active_checkbox.isChecked()

        if not name:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập tên danh mục.")
            return
            
        try:
            # UserDashboard -> UserCategoriesPage -> UserCategoryDialog
            # So, self.parent_page.parent is UserDashboard
            dashboard = self.parent_page.parent 
            category_manager = dashboard.category_manager
            current_user_id = dashboard.current_user_id
            is_admin_user = dashboard.current_user.get('is_admin', False) # Should be False for user context

            category_type_value = 'income' if type_text == "Thu nhập" else 'expense'
            
            if self.category_data: # Edit Mode
                category_id = self.category_data.get('category_id')
                update_payload = {
                    'name': name, 'type': category_type_value, 'description': description,
                    'icon': icon, 'color': color, 'is_active': is_active
                }
                # For user editing their own category, is_admin is False
                category_manager.update_category(category_id, current_user_id, is_admin_user, **update_payload)
            else: # Add Mode
                # User creates category owned by themselves
                category_manager.create_category(
                    user_id=current_user_id, 
                    name=name, category_type=category_type_value, description=description,
                    icon=icon, color=color, is_active=is_active
                )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu danh mục: {str(e)}") 