from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QComboBox,
                             QDateEdit, QPushButton, QMessageBox, QSpinBox, QHBoxLayout)
from PyQt5.QtCore import QDate
from finance_app.data_manager.category_manager import CategoryManager
from finance_app.data_manager.budget_manager import BudgetManager

class BudgetDialog(QDialog):
    def __init__(self, parent=None, budget=None, user_id=None):
        super().__init__(parent)
        self.budget = budget
        self.user_id = user_id
        self.category_manager = CategoryManager()
        self.budget_manager = BudgetManager()
        self.init_ui()
        
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Thêm ngân sách mới" if not self.budget else "Sửa ngân sách")
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Category combo
        self.category_combo = QComboBox()
        self.load_categories()
        layout.addRow("Danh mục:", self.category_combo)
        
        # Amount input
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Nhập hạn mức")
        if self.budget:
            self.amount_input.setText(str(self.budget.get('amount', '')))
        layout.addRow("Hạn mức:", self.amount_input)
        
        # Alert threshold
        self.threshold_input = QSpinBox()
        self.threshold_input.setRange(1, 100)
        self.threshold_input.setValue(80)  # Default 80%
        self.threshold_input.setSuffix("%")
        if self.budget:
            self.threshold_input.setValue(self.budget.get('alert_threshold', 80))
        layout.addRow("Ngưỡng cảnh báo:", self.threshold_input)
        
        # Start date
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        if self.budget and self.budget.get('start_date'):
            self.start_date.setDate(QDate.fromString(self.budget['start_date'], "yyyy-MM-dd"))
        else:
            self.start_date.setDate(QDate.currentDate())
        layout.addRow("Ngày bắt đầu:", self.start_date)
        
        # End date
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        if self.budget and self.budget.get('end_date'):
            self.end_date.setDate(QDate.fromString(self.budget['end_date'], "yyyy-MM-dd"))
        else:
            self.end_date.setDate(QDate.currentDate().addMonths(1))
        layout.addRow("Ngày kết thúc:", self.end_date)
        
        # Notes
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Nhập ghi chú")
        if self.budget:
            self.notes_input.setText(self.budget.get('notes', ''))
        layout.addRow("Ghi chú:", self.notes_input)
        
        # Buttons
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.save_budget)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
        
    def load_categories(self):
        """Load expense categories"""
        try:
            categories = self.category_manager.get_all_categories(
                self.user_id,
                category_type='expense'
            )
            
            self.category_combo.clear()
            for category in categories:
                self.category_combo.addItem(category['name'], category['category_id'])
                
            if self.budget and self.budget.get('category_id'):
                index = self.category_combo.findData(self.budget['category_id'])
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
                    
        except Exception as e:
            print(f"Error loading categories: {str(e)}")
            
    def save_budget(self):
        """Save budget data"""
        try:
            # Validate amount
            amount_text = self.amount_input.text().strip().replace(',', '')
            if not amount_text:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập hạn mức")
                return
                
            try:
                amount = float(amount_text)
                if amount <= 0:
                    raise ValueError("Hạn mức phải lớn hơn 0")
            except ValueError as e:
                QMessageBox.warning(self, "Cảnh báo", str(e))
                return
            
            # Get category
            category_id = self.category_combo.currentData()
            if not category_id:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn danh mục")
                return
            
            # Validate dates
            start_date = self.start_date.date()
            end_date = self.end_date.date()
            if start_date > end_date:
                QMessageBox.warning(self, "Cảnh báo", "Ngày kết thúc phải sau ngày bắt đầu")
                return
            
            # Prepare budget data
            budget_data = {
                'amount': amount,
                'category_id': category_id,
                'alert_threshold': self.threshold_input.value(),
                'start_date': start_date.toString("yyyy-MM-dd"),
                'end_date': end_date.toString("yyyy-MM-dd"),
                'notes': self.notes_input.text().strip()
            }
            
            if self.budget:  # Update existing
                result = self.budget_manager.update_budget(
                    self.user_id,
                    self.budget['budget_id'],
                    **budget_data
                )
            else:  # Create new
                result = self.budget_manager.create_budget(
                    self.user_id,
                    **budget_data
                )
                
            if isinstance(result, tuple):
                success, message = result
                if not success:
                    QMessageBox.warning(self, "Lỗi", message)
                    return
                    
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
