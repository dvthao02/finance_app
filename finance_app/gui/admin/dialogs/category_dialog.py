from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QComboBox,
                             QPushButton, QMessageBox, QColorDialog)
from PyQt5.QtCore import Qt
from finance_app.data_manager.category_manager import CategoryManager

class CategoryDialog(QDialog):
    def __init__(self, parent=None, category=None, user_id=None):
        super().__init__(parent)
        self.category = category
        self.user_id = user_id
        self.category_manager = CategoryManager()
        self.init_ui()
        
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Thêm danh mục mới" if not self.category else "Sửa danh mục")
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nhập tên danh mục")
        if self.category:
            self.name_input.setText(self.category.get('name', ''))
        layout.addRow("Tên danh mục:", self.name_input)
        
        # Type combo
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Chi tiêu", "Thu nhập"])
        if self.category:
            self.type_combo.setCurrentText(
                "Thu nhập" if self.category.get('type') == 'income' else "Chi tiêu"
            )
        layout.addRow("Loại:", self.type_combo)
        
        # Description
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Nhập mô tả")
        if self.category:
            self.description_input.setText(self.category.get('description', ''))
        layout.addRow("Mô tả:", self.description_input)
        
        # Icon input
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("Nhập tên icon (tùy chọn)")
        if self.category:
            self.icon_input.setText(self.category.get('icon', ''))
        layout.addRow("Icon:", self.icon_input)
        
        # Color picker
        self.color_btn = QPushButton("Chọn màu")
        self.color_btn.clicked.connect(self.choose_color)
        self.color = self.category.get('color', '#3498db') if self.category else '#3498db'
        self.update_color_button()
        layout.addRow("Màu sắc:", self.color_btn)
        
        # Buttons
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.save_category)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
        
    def choose_color(self):
        """Open color picker dialog"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = color.name()
            self.update_color_button()
            
    def update_color_button(self):
        """Update color button appearance"""
        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                color: white;
                padding: 5px;
                border: none;
                border-radius: 3px;
            }}
        """)
        
    def save_category(self):
        """Save category data"""
        try:
            # Validate name
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tên danh mục")
                return
            
            # Prepare category data
            category_data = {
                'name': name,
                'type': 'income' if self.type_combo.currentText() == "Thu nhập" else 'expense',
                'description': self.description_input.text().strip(),
                'icon': self.icon_input.text().strip(),
                'color': self.color
            }
            
            if self.category:  # Update existing
                result = self.category_manager.update_category(
                    self.user_id,
                    self.category['category_id'],
                    **category_data
                )
            else:  # Create new
                result = self.category_manager.create_category(
                    self.user_id,
                    **category_data
                )
                
            if isinstance(result, tuple):
                success, message = result
                if not success:
                    QMessageBox.warning(self, "Lỗi", message)
                    return
                    
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
