from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QTextEdit, QPushButton, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt

class CategoryDialog(QDialog):
    def __init__(self, parent=None, category_data=None):
        super().__init__(parent)
        self.parent = parent
        self.category_data = category_data
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Thêm danh mục" if not self.category_data else "Chỉnh sửa danh mục")
        self.setMinimumSize(500, 420)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                font-family: Arial;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Name
        name_layout = QVBoxLayout()
        name_label = QLabel("Tên danh mục *")
        name_label.setStyleSheet("color: #5f6368; font-size: 14px; font-weight: bold;")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nhập tên danh mục")
        self.name_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                min-height: 45px;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
            }
        """)
        if self.category_data:
            self.name_edit.setText(self.category_data.get('name', ''))
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Type
        type_layout = QVBoxLayout()
        type_label = QLabel("Loại danh mục *")
        type_label.setStyleSheet("color: #5f6368; font-size: 14px; font-weight: bold;")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Thu nhập", "Chi tiêu"])
        self.type_combo.setStyleSheet("""
            QComboBox {
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                min-height: 45px;
            }
            QComboBox:focus {
                border: 2px solid #1a73e8;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(assets/down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        if self.category_data:
            self.type_combo.setCurrentText(
                "Thu nhập" if self.category_data.get('type') == 'income' else "Chi tiêu"
            )
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Description
        desc_layout = QVBoxLayout()
        desc_label = QLabel("Mô tả")
        desc_label.setStyleSheet("color: #5f6368; font-size: 14px; font-weight: bold;")
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Nhập mô tả cho danh mục")
        self.desc_edit.setStyleSheet("""
            QTextEdit {
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                min-height: 100px;
            }
            QTextEdit:focus {
                border: 2px solid #1a73e8;
            }
        """)
        if self.category_data:
            self.desc_edit.setText(self.category_data.get('description', ''))
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_edit)
        layout.addLayout(desc_layout)
        
        # Icon
        icon_layout = QHBoxLayout()
        icon_label = QLabel("Icon:")
        self.icon_edit = QLineEdit()
        self.icon_edit.setPlaceholderText("VD: 💰 hoặc text")
        if self.category_data:
            self.icon_edit.setText(self.category_data.get('icon', ''))
        icon_layout.addWidget(icon_label)
        icon_layout.addWidget(self.icon_edit)
        layout.addLayout(icon_layout)

        # Color
        color_layout = QHBoxLayout()
        color_label = QLabel("Màu (Hex):")
        self.color_edit = QLineEdit()
        self.color_edit.setPlaceholderText("VD: #34a853")
        if self.category_data:
            self.color_edit.setText(self.category_data.get('color', ''))
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_edit)
        layout.addLayout(color_layout)

        # Is Active Checkbox
        self.is_active_checkbox = QCheckBox("Đang hoạt động")
        self.is_active_checkbox.setChecked(True)
        if self.category_data:
            self.is_active_checkbox.setChecked(self.category_data.get('is_active', True))
        layout.addWidget(self.is_active_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #1a73e8;
                border: 2px solid #1a73e8;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #e8f0fe;
            }
            QPushButton:pressed {
                background-color: #d2e3fc;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Lưu")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
            QPushButton:pressed {
                background-color: #104d9e;
            }
        """)
        save_btn.clicked.connect(self.save_category)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def save_category(self):
        """Save the category"""
        name = self.name_edit.text().strip()
        type_text = self.type_combo.currentText()
        description = self.desc_edit.toPlainText().strip()
        icon_text = self.icon_edit.text().strip()
        color_text = self.color_edit.text().strip()
        is_active_status = self.is_active_checkbox.isChecked()
        
        if not name:
            # Use show_message_box from BaseWidget, if available, or parent's show_error
            if hasattr(self, 'show_message_box'):
                 self.show_message_box("warning", "Thiếu thông tin", "Vui lòng nhập tên danh mục")
            elif self.parent and hasattr(self.parent, 'show_error'): # AdminCategoriesPage
                 self.parent.show_error("Thiếu thông tin", "Vui lòng nhập tên danh mục")
            elif self.parent and self.parent.parent and hasattr(self.parent.parent, 'show_error'): # AdminDashboard
                 self.parent.parent.show_error("Thiếu thông tin", "Vui lòng nhập tên danh mục")
            else: # Fallback
                QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập tên danh mục")
            return
            
        try:
            category_type_value = 'income' if type_text == "Thu nhập" else 'expense'
            
            # Access CategoryManager through self.parent (AdminCategoriesPage) 
            # which should have a reference to its parent dashboard's category_manager
            category_manager = self.parent.parent.category_manager

            if self.category_data: # Edit Mode
                category_id = self.category_data.get('category_id')
                if not category_id:
                    # This should not happen if dialog is opened for edit correctly
                    raise ValueError("Category ID is missing for update.")
                
                update_payload = {
                    'name': name,
                    'type': category_type_value,
                    'description': description,
                    'icon': icon_text,
                    'color': color_text,
                    'is_active': is_active_status
                }
                updated_cat = category_manager.update_category(category_id, **update_payload)
                if not updated_cat:
                    # update_category in CategoryManager should ideally raise an error or return more info
                    raise Exception("Cập nhật danh mục thất bại.") 

            else: # Add Mode
                # Assume admin creates "system" categories by default via this dialog
                # If admin-specific categories are needed, user_id should be self.parent.parent.current_user_id
                created_category = category_manager.create_category(
                    user_id="system", 
                    name=name,
                    category_type=category_type_value,
                    description=description,
                    icon=icon_text,
                    color=color_text,
                    is_active=is_active_status
                )
                if not created_category:
                     # create_category raises ValueError on issues, which will be caught by the outer except
                     # If it returned None for some failures, handle here.
                     raise Exception("Tạo danh mục mới thất bại.")
                
            self.accept()
            
        except Exception as e:
            error_message = f"Không thể lưu danh mục: {str(e)}"
            if hasattr(self, 'show_message_box'):
                 self.show_message_box("critical", "Lỗi", error_message)
            elif self.parent and hasattr(self.parent, 'show_error'):
                 self.parent.show_error("Lỗi", error_message)
            elif self.parent and self.parent.parent and hasattr(self.parent.parent, 'show_error'):
                 self.parent.parent.show_error("Lỗi", error_message)
            else:
                QMessageBox.critical(self, "Lỗi", error_message)
