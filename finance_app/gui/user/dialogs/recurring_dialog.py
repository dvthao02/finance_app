from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QComboBox,
                             QDateEdit, QPushButton, QMessageBox, QSpinBox, QCheckBox, QHBoxLayout)
from PyQt5.QtCore import QDate
from finance_app.data_manager.category_manager import CategoryManager
from finance_app.data_manager.recurring_transaction_manager import RecurringTransactionManager

class RecurringTransactionDialog(QDialog):
    def __init__(self, parent=None, recurring=None, user_id=None):
        super().__init__(parent)
        self.recurring = recurring
        self.user_id = user_id
        self.parent_widget = parent

        self.category_manager = CategoryManager()
        self.recurring_manager = RecurringTransactionManager()

        if self.user_id:
            self.category_manager.set_current_user(self.user_id)
            self.recurring_manager.set_current_user(self.user_id)
        else:
            print("Error: RecurringTransactionDialog initialized without user_id.")

        self.init_ui()
        
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Thêm giao dịch định kỳ" if not self.recurring else "Sửa giao dịch định kỳ")
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Amount input
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Nhập số tiền")
        if self.recurring:
            self.amount_input.setText(str(self.recurring.get('amount', '')))
        layout.addRow("Số tiền:", self.amount_input)
        
        # Type combo
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Thu nhập", "Chi tiêu"])
        if self.recurring:
            self.type_combo.setCurrentText(
                "Thu nhập" if self.recurring.get('type') == 'income' else "Chi tiêu"
            )
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addRow("Loại:", self.type_combo)
        
        # Category combo
        self.category_combo = QComboBox()
        self.load_categories()
        layout.addRow("Danh mục:", self.category_combo)
        
        # Frequency combo
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["Hàng ngày", "Hàng tuần", "Hàng tháng", "Hàng năm"])
        if self.recurring:
            freq_map = {
                'daily': "Hàng ngày",
                'weekly': "Hàng tuần",
                'monthly': "Hàng tháng",
                'yearly': "Hàng năm"
            }
            self.frequency_combo.setCurrentText(freq_map.get(self.recurring.get('frequency'), "Hàng tháng"))
        layout.addRow("Tần suất:", self.frequency_combo)
        
        # Start date
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        if self.recurring and self.recurring.get('start_date'):
            self.start_date.setDate(QDate.fromString(self.recurring['start_date'], "yyyy-MM-dd"))
        else:
            self.start_date.setDate(QDate.currentDate())
        layout.addRow("Ngày bắt đầu:", self.start_date)
        
        # End date
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        if self.recurring and self.recurring.get('end_date'):
            self.end_date.setDate(QDate.fromString(self.recurring['end_date'], "yyyy-MM-dd"))
        else:
            self.end_date.setDate(QDate.currentDate().addYears(1))
        layout.addRow("Ngày kết thúc:", self.end_date)
        
        # Description
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Nhập mô tả")
        if self.recurring:
            self.description_input.setText(self.recurring.get('description', ''))
        layout.addRow("Mô tả:", self.description_input)
        
        # Tags
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Nhập tags (phân cách bởi dấu phẩy)")
        if self.recurring and self.recurring.get('tags'):
            self.tags_input.setText(", ".join(self.recurring['tags']))
        layout.addRow("Tags:", self.tags_input)
        
        # Auto create checkbox
        self.auto_create = QCheckBox("Tự động tạo giao dịch")
        self.auto_create.setChecked(True)
        if self.recurring:
            self.auto_create.setChecked(self.recurring.get('auto_create', True))
        layout.addRow("", self.auto_create)
        
        # Buttons
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.save_recurring)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
        
    def load_categories(self):
        """Load categories based on selected type"""
        try:
            transaction_type = 'income' if self.type_combo.currentText() == "Thu nhập" else 'expense'
            categories = self.category_manager.get_all_categories(
                category_type=transaction_type
            )
            
            self.category_combo.clear()
            for category in categories:
                self.category_combo.addItem(category['name'], category['category_id'])
                
            if self.recurring and self.recurring.get('category_id'):
                index = self.category_combo.findData(self.recurring['category_id'])
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
                    
        except Exception as e:
            if hasattr(self.parent_widget, 'show_error'):
                 self.parent_widget.show_error("Lỗi tải danh mục", str(e))
            else:
                print(f"Error loading categories: {str(e)}")
            
    def on_type_changed(self):
        """Handle transaction type change"""
        self.load_categories()
        
    def save_recurring(self):
        """Save recurring transaction data"""
        try:
            # Validate amount
            amount_text = self.amount_input.text().strip().replace(',', '')
            if not amount_text:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập số tiền")
                return
                
            try:
                amount = float(amount_text)
                if amount <= 0:
                    raise ValueError("Số tiền phải lớn hơn 0")
            except ValueError as e:
                QMessageBox.warning(self, "Cảnh báo", str(e))
                return
            
            # Get category
            category_id = self.category_combo.currentData()
            if not category_id:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn danh mục")
                return
            
            # Get frequency
            freq_map = {
                "Hàng ngày": "daily",
                "Hàng tuần": "weekly",
                "Hàng tháng": "monthly",
                "Hàng năm": "yearly"
            }
            frequency = freq_map[self.frequency_combo.currentText()]
            
            # Validate dates
            start_date = self.start_date.date()
            end_date = self.end_date.date()
            if start_date > end_date:
                QMessageBox.warning(self, "Cảnh báo", "Ngày kết thúc phải sau ngày bắt đầu")
                return
            
            # Prepare recurring data
            recurring_data = {
                'amount': amount,
                'type': 'income' if self.type_combo.currentText() == "Thu nhập" else 'expense',
                'category_id': category_id,
                'frequency': frequency,
                'start_date': start_date.toString("yyyy-MM-dd"),
                'end_date': end_date.toString("yyyy-MM-dd"),
                'description': self.description_input.text().strip(),
                'tags': [tag.strip() for tag in self.tags_input.text().split(',') if tag.strip()],
                'auto_create': self.auto_create.isChecked()
            }
            
            if self.recurring:  # Update existing
                result = self.recurring_manager.update(
                    recurring_id=self.recurring['recurring_id'],
                    **recurring_data
                )
            else:  # Create new
                result = self.recurring_manager.create(
                    **recurring_data
                )
                
            if isinstance(result, tuple):
                success, message = result
                if not success:
                    QMessageBox.warning(self, "Lỗi", message)
                    return
                    
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
