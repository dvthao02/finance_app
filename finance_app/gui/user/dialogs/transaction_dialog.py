from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QComboBox,
                             QDateEdit, QPushButton, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import QDate
from finance_app.data_manager.category_manager import CategoryManager
from finance_app.data_manager.transaction_manager import TransactionManager

class TransactionDialog(QDialog):
    def __init__(self, parent=None, transaction=None, user_id=None):
        super().__init__(parent)
        self.transaction = transaction
        self.user_id = user_id
        self.category_manager = CategoryManager()
        self.transaction_manager = TransactionManager()
        self.init_ui()
        
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Thêm giao dịch mới" if not self.transaction else "Sửa giao dịch")
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Amount input
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Nhập số tiền")
        if self.transaction:
            self.amount_input.setText(str(self.transaction.get('amount', '')))
        layout.addRow("Số tiền:", self.amount_input)
        
        # Type combo
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Thu nhập", "Chi tiêu"])
        if self.transaction:
            self.type_combo.setCurrentText(
                "Thu nhập" if self.transaction.get('type') == 'income' else "Chi tiêu"
            )
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addRow("Loại:", self.type_combo)
        
        # Category combo
        self.category_combo = QComboBox()
        self.load_categories()
        layout.addRow("Danh mục:", self.category_combo)
        
        # Date input
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        if self.transaction and self.transaction.get('date'):
            try:
                self.date_input.setDate(QDate.fromString(self.transaction['date'], "yyyy-MM-dd"))
            except:
                self.date_input.setDate(QDate.currentDate())
        else:
            self.date_input.setDate(QDate.currentDate())
        layout.addRow("Ngày:", self.date_input)
        
        # Description
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Nhập mô tả")
        if self.transaction:
            self.description_input.setText(self.transaction.get('description', ''))
        layout.addRow("Mô tả:", self.description_input)
        
        # Tags
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Nhập tags (phân cách bởi dấu phẩy)")
        if self.transaction and self.transaction.get('tags'):
            self.tags_input.setText(", ".join(self.transaction['tags']))
        layout.addRow("Tags:", self.tags_input)
        
        # Location
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Nhập địa điểm")
        if self.transaction:
            self.location_input.setText(self.transaction.get('location', ''))
        layout.addRow("Địa điểm:", self.location_input)
        
        # Buttons
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.save_transaction)
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
                self.user_id,
                category_type=transaction_type
            )
            
            self.category_combo.clear()
            for category in categories:
                self.category_combo.addItem(category['name'], category['category_id'])
                
            if self.transaction and self.transaction.get('category_id'):
                index = self.category_combo.findData(self.transaction['category_id'])
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
                    
        except Exception as e:
            print(f"Error loading categories: {str(e)}")
            
    def on_type_changed(self):
        """Handle transaction type change"""
        self.load_categories()
        
    def save_transaction(self):
        """Save transaction data"""
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
            
            # Prepare transaction data
            transaction_data = {
                'amount': amount,
                'type': 'income' if self.type_combo.currentText() == "Thu nhập" else 'expense',
                'category_id': category_id,
                'date': self.date_input.date().toString("yyyy-MM-dd"),
                'description': self.description_input.text().strip(),
                'tags': [tag.strip() for tag in self.tags_input.text().split(',') if tag.strip()],
                'location': self.location_input.text().strip()
            }
            
            if self.transaction:  # Update existing
                result = self.transaction_manager.update_transaction(
                    self.user_id,
                    self.transaction['transaction_id'],
                    **transaction_data
                )
            else:  # Create new
                result = self.transaction_manager.create_transaction(
                    self.user_id,
                    **transaction_data
                )
                
            if isinstance(result, tuple):
                success, message = result
                if not success:
                    QMessageBox.warning(self, "Lỗi", message)
                    return
                    
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
