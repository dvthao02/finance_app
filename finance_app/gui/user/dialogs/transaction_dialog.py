from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
                             QDateEdit, QSpinBox)
from PyQt5.QtCore import Qt, QDate
from finance_app.gui.base.base_widget import BaseWidget
from datetime import datetime

class TransactionDialog(QDialog, BaseWidget):
    def __init__(self, parent=None, transaction_data=None):
        super().__init__(parent)
        self.parent = parent
        self.transaction_data = transaction_data
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI"""
        # Set window properties
        self.setWindowTitle("Thêm giao dịch" if not self.transaction_data else "Chỉnh sửa giao dịch")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Transaction type
        type_label = self.create_label("Loại giao dịch", bold=True)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Thu nhập", "Chi tiêu"])
        self.type_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 15px;
                background-color: white;
                min-height: 45px;
            }
            QComboBox:focus {
                border: 2px solid #1a73e8;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 15px;
            }
            QComboBox::down-arrow {
                image: url(assets/arrow_down.png);
                width: 12px;
                height: 12px;
            }
        """)
        
        if self.transaction_data:
            index = 1 if self.transaction_data.get('type') == 'expense' else 0
            self.type_combo.setCurrentIndex(index)
            
        layout.addWidget(type_label)
        layout.addWidget(self.type_combo)
        
        # Category
        category_label = self.create_label("Danh mục", bold=True)
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet(self.type_combo.styleSheet())
        
        # Load categories based on type
        self.load_categories()
        self.type_combo.currentIndexChanged.connect(self.load_categories)
        
        if self.transaction_data:
            category_id = self.transaction_data.get('category_id')
            if category_id:
                index = self.category_combo.findData(category_id)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
                    
        layout.addWidget(category_label)
        layout.addWidget(self.category_combo)
        
        # Amount
        amount_label = self.create_label("Số tiền", bold=True)
        self.amount_input = QSpinBox()
        self.amount_input.setRange(0, 1000000000)
        self.amount_input.setSingleStep(1000)
        self.amount_input.setSuffix(" đ")
        self.amount_input.setGroupSeparatorShown(True)
        self.amount_input.setStyleSheet("""
            QSpinBox {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 15px;
                background-color: white;
                min-height: 45px;
            }
            QSpinBox:focus {
                border: 2px solid #1a73e8;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0;
                border: none;
            }
        """)
        
        if self.transaction_data:
            self.amount_input.setValue(self.transaction_data.get('amount', 0))
            
        layout.addWidget(amount_label)
        layout.addWidget(self.amount_input)
        
        # Date
        date_label = self.create_label("Ngày", bold=True)
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setStyleSheet("""
            QDateEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 15px;
                background-color: white;
                min-height: 45px;
            }
            QDateEdit:focus {
                border: 2px solid #1a73e8;
            }
            QDateEdit::drop-down {
                border: none;
                padding-right: 15px;
            }
            QDateEdit::down-arrow {
                image: url(assets/calendar.png);
                width: 12px;
                height: 12px;
            }
        """)
        
        if self.transaction_data:
            date = datetime.fromisoformat(self.transaction_data.get('date'))
            self.date_input.setDate(QDate(date.year, date.month, date.day))
            
        layout.addWidget(date_label)
        layout.addWidget(self.date_input)
        
        # Budget
        budget_label = self.create_label("Ngân sách", bold=True)
        self.budget_combo = QComboBox()
        self.budget_combo.setStyleSheet(self.type_combo.styleSheet())
        
        # Load budgets based on type
        self.load_budgets()
        self.type_combo.currentIndexChanged.connect(self.load_budgets)
        
        if self.transaction_data:
            budget_id = self.transaction_data.get('budget_id')
            if budget_id:
                index = self.budget_combo.findData(budget_id)
                if index >= 0:
                    self.budget_combo.setCurrentIndex(index)
                    
        layout.addWidget(budget_label)
        layout.addWidget(self.budget_combo)
        
        # Description
        desc_label = self.create_label("Mô tả", bold=True)
        self.desc_input = self.create_input_field("Nhập mô tả (không bắt buộc)")
        if self.transaction_data:
            self.desc_input.setText(self.transaction_data.get('description', ''))
            
        layout.addWidget(desc_label)
        layout.addWidget(self.desc_input)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        cancel_btn = self.create_secondary_button("Hủy")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = self.create_primary_button("Lưu")
        save_btn.clicked.connect(self.save_transaction)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
    def load_categories(self):
        """Load categories based on selected type"""
        try:
            # Clear current items
            self.category_combo.clear()
            
            # Get categories
            category_type = 'expense' if self.type_combo.currentText() == "Chi tiêu" else 'income'
            categories = self.parent.parent.category_manager.get_user_categories(
                self.parent.parent.current_user_id,
                category_type=category_type
            )
            
            # Add categories to combo box
            for category in categories:
                self.category_combo.addItem(
                    category.get('name', ''),
                    category.get('category_id')
                )
                
        except Exception as e:
            self.parent.show_error(
                "Lỗi",
                f"Không thể tải danh sách danh mục: {str(e)}"
            )
            
    def load_budgets(self):
        """Load budgets based on selected type"""
        try:
            # Clear current items
            self.budget_combo.clear()
            
            # Add empty option
            self.budget_combo.addItem("Không có ngân sách", None)
            
            # Get budgets
            budget_type = 'expense' if self.type_combo.currentText() == "Chi tiêu" else 'income'
            budgets = self.parent.parent.budget_manager.get_user_budgets(
                self.parent.parent.current_user_id,
                budget_type=budget_type
            )
            
            # Add budgets to combo box
            for budget in budgets:
                self.budget_combo.addItem(
                    budget.get('name', ''),
                    budget.get('budget_id')
                )
                
        except Exception as e:
            self.parent.show_error(
                "Lỗi",
                f"Không thể tải danh sách ngân sách: {str(e)}"
            )
            
    def save_transaction(self):
        """Save transaction data"""
        current_user_id = self.parent.parent.current_user_id
        if not current_user_id:
            self.parent.show_error("Lỗi", "Không tìm thấy thông tin người dùng hiện tại.")
            return

        # Get form data
        transaction_type = 'expense' if self.type_combo.currentText() == "Chi tiêu" else 'income'
        category_id = self.category_combo.currentData()
        amount = self.amount_input.value()
        date = self.date_input.date().toPyDate().isoformat()
        # budget_id = self.budget_combo.currentData() # Assuming budget_id is handled by transaction manager if passed
        description = self.desc_input.text().strip()
        
        # Validate data
        if not category_id:
            self.parent.show_warning(
                "Thiếu thông tin",
                "Vui lòng chọn danh mục"
            )
            return
            
        if amount <= 0:
            self.parent.show_warning(
                "Thiếu thông tin",
                "Vui lòng nhập số tiền lớn hơn 0"
            )
            return
            
        transaction_payload = {
            'type': transaction_type,
            'category_id': category_id,
            'amount': amount,
            'date': date,
            # 'budget_id': budget_id, # Include if transaction model supports it
            'description': description
        }

        try:
            success = False
            if self.transaction_data: # Update existing transaction
                # Ensure user_id is implicitly handled by current_user_id in transaction_manager
                # or pass it explicitly if required by a future version of update_transaction.
                result = self.parent.parent.transaction_manager.update_transaction(
                    transaction_id=self.transaction_data['transaction_id'],
                    **transaction_payload
                )
                # update_transaction in manager returns the updated transaction or raises error
                success = True if result else False 
            else: # Create new transaction
                # Pass current_user_id explicitly to add_transaction
                new_txn_id = self.parent.parent.transaction_manager.add_transaction(
                    user_id=current_user_id,
                    **transaction_payload
                )
                success = True if new_txn_id else False
                
            if success:
                # Simplified budget alert check - more robust check would involve BudgetManager
                # For now, this part is commented out as get_budget_total was not defined
                # and proper budget interaction is more complex.
                # if budget_id and transaction_type == 'expense':
                #     budget = self.parent.parent.budget_manager.get_budget_by_id(current_user_id, budget_id)
                #     if budget and budget.get('alert_threshold', 0) > 0:
                #         # This needs a reliable way to get current spent amount for the budget
                #         # spent_amount_for_budget = ... 
                #         # if spent_amount_for_budget >= (budget['alert_threshold']/100 * budget['amount']):
                #         #     self.parent.parent.notification_manager.create_notification(
                #         #         user_id=current_user_id,
                #         #         title="Cảnh báo ngân sách",
                #         #         message=f"Chi tiêu cho ngân sách '{budget.get('name', '')}' có thể đã vượt ngưỡng cảnh báo.",
                #         #         notification_type='budget_alert' # Ensure this type is valid
                #         #     )

                self.parent.show_info(
                    "Thành công",
                    "Đã lưu giao dịch thành công"
                )
                self.accept()
            else:
                # Errors should ideally be raised by manager methods and caught by the generic exception handler below
                # or specific error messages returned by manager methods should be displayed.
                self.parent.show_error(
                    "Lỗi",
                    "Không thể lưu giao dịch (kiểm tra lại thông tin hoặc lỗi hệ thống)."
                )
                    
        except ValueError as ve: # Catch validation errors from managers
             self.parent.show_error("Lỗi dữ liệu", str(ve))
        except Exception as e:
            self.parent.show_error(
                "Lỗi",
                f"Không thể lưu giao dịch: {str(e)}"
            )
