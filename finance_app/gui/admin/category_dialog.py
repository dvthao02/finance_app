from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit,
                            QPushButton, QHBoxLayout, QMessageBox, QComboBox)

class CategoryDialog(QDialog):
    def __init__(self, parent=None, category=None):
        super().__init__(parent)
        self.category = category
        self.category_manager = parent.category_manager if parent else None
        self.current_user = parent.current_user if parent else None
        self.init_ui()
        
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Thêm danh mục mới" if not self.category else "Sửa danh mục")
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Category name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nhập tên danh mục")
        if self.category:
            self.name_input.setText(self.category['name'])
        layout.addRow("Tên danh mục:", self.name_input)
        
        # Category type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Chi tiêu", "Thu nhập"])
        if self.category:
            self.type_combo.setCurrentText(
                "Thu nhập" if self.category['type'] == 'income' else "Chi tiêu"
            )
        layout.addRow("Loại:", self.type_combo)
        
        # Description
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Nhập mô tả danh mục")
        if self.category:
            self.description_input.setText(self.category.get('description', ''))
        layout.addRow("Mô tả:", self.description_input)
        
        # Buttons
        button_box = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.save_category)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        button_box.addWidget(save_btn)
        button_box.addWidget(cancel_btn)
        layout.addRow(button_box)
        
    def save_category(self):
        """Save category data"""
        try:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tên danh mục")
                return
                
            category_type = 'income' if self.type_combo.currentText() == "Thu nhập" else 'expense'
            description = self.description_input.text().strip()
            
            if self.category:  # Update existing category
                self.category_manager.update_category(
                    self.current_user['user_id'],
                    self.category['category_id'],
                    name=name,
                    type=category_type,
                    description=description
                )
            else:  # Add new category
                self.category_manager.create_category(
                    self.current_user['user_id'],
                    name=name,
                    type=category_type,
                    description=description
                )
                
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
