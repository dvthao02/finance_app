from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QPushButton, 
                           QHeaderView, QHBoxLayout, QWidget, QMessageBox, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal
from datetime import datetime
from finance_app.data_manager.category_manager import CategoryManager

class TransactionTable(QTableWidget):
    transaction_updated = pyqtSignal()
    transaction_deleted = pyqtSignal()
    edit_transaction = pyqtSignal(dict)
    delete_transaction = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.transactions = []
        self.category_manager = CategoryManager()
        
    def init_ui(self):
        # Set up table columns
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            'Ngày', 'Loại', 'Danh mục', 'Mô tả', 'Số tiền', 'Ghi chú', 'Hành động'
        ])

        # Set column widths
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Category
        header.setSectionResizeMode(3, QHeaderView.Stretch)          # Description
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Amount
        header.setSectionResizeMode(5, QHeaderView.Stretch)          # Notes
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions

        # Style the table
        self.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #dcdde1;
                border: 1px solid #dcdde1;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #f5f6fa;
                padding: 6px;
                border: 1px solid #dcdde1;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)

    def update_transactions(self, transactions):
        """Update transaction table with new data"""
        self.transactions = transactions if transactions else []
        self.setRowCount(0)  # Clear existing rows
        
        if not self.transactions:
            return
            
        self.setRowCount(len(self.transactions))
        
        for row, transaction in enumerate(self.transactions):
            try:
                # Date
                date_str = transaction.get('date', '')
                date_item = QTableWidgetItem(date_str)
                date_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 0, date_item)
                
                # Type
                type_str = "Thu nhập" if transaction.get('type') == 'income' else "Chi tiêu"
                type_label = QLabel(type_str)
                type_label.setAlignment(Qt.AlignCenter)
                type_label.setStyleSheet(f"""
                    QLabel {{
                        color: {'#27ae60' if transaction.get('type') == 'income' else '#e74c3c'};
                        font-weight: bold;
                        padding: 2px 8px;
                        border-radius: 3px;
                        background: {'#ebfaf0' if transaction.get('type') == 'income' else '#fdf3f2'};
                    }}
                """)
                self.setCellWidget(row, 1, type_label)
                
                # Category - now using the category_name passed from UserDashboard
                category_name = transaction.get('category_name', 'Không phân loại')
                category_item = QTableWidgetItem(category_name)
                category_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 2, category_item)
                
                # Description
                desc_item = QTableWidgetItem(transaction.get('description', ''))
                self.setItem(row, 3, desc_item)
                
                # Amount
                amount = transaction.get('amount', 0)
                amount_str = f"{amount:,.0f} đ"
                amount_item = QTableWidgetItem(amount_str)
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                amount_item.setForeground(Qt.darkGreen if transaction.get('type') == 'income' else Qt.red)
                self.setItem(row, 4, amount_item)
                
                # Notes/Tags
                tags = transaction.get('tags', [])
                notes = ", ".join(tags) if tags else ""
                notes_item = QTableWidgetItem(notes)
                self.setItem(row, 5, notes_item)
                
                # Actions
                actions_layout = QHBoxLayout()
                actions_layout.setContentsMargins(5, 0, 5, 0)
                actions_layout.setSpacing(5)
                
                edit_btn = QPushButton("Sửa")
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                edit_btn.clicked.connect(lambda checked, t=transaction: self.handle_edit_click(t))
                
                delete_btn = QPushButton("Xóa")
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, t=transaction: self.handle_delete_click(t))
                
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                
                actions_widget = QWidget()
                actions_widget.setLayout(actions_layout)
                self.setCellWidget(row, 6, actions_widget)
                
            except Exception as e:
                print(f"Error updating transaction row {row}: {str(e)}")
                continue
        
        self.resizeRowsToContents()

    def handle_edit_click(self, transaction):
        """Handle edit button click by emitting edit_transaction signal"""
        self.edit_transaction.emit(transaction)

    def handle_delete_click(self, transaction):
        """Handle delete button click by showing confirmation and emitting delete_transaction signal"""
        reply = QMessageBox.question(
            self,
            'Xác nhận xóa',
            f'Bạn có chắc chắn muốn xóa giao dịch này không?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.delete_transaction.emit(transaction)
