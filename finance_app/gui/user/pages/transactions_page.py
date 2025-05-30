from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView, QMenu)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from finance_app.gui.base.base_widget import BaseWidget
from finance_app.gui.user.dialogs.transaction_dialog import TransactionDialog
from finance_app.gui.components.period_filter import PeriodFilter
from finance_app.gui.components.statistics_panel import StatisticsPanel
from datetime import datetime

class TransactionsPage(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_period = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the transactions page UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Page header
        header_layout = QHBoxLayout()
        
        # Title
        title = self.create_title_label("Quản lý giao dịch")
        header_layout.addWidget(title)
        
        # Add transaction button
        add_btn = self.create_primary_button("Thêm giao dịch")
        add_btn.clicked.connect(self.add_transaction)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Statistics panel
        self.stats_panel = StatisticsPanel()
        layout.addWidget(self.stats_panel)
        
        # Period filter
        filter_layout = QHBoxLayout()
        
        filter_label = self.create_label("Lọc theo thời gian:", bold=True)
        filter_layout.addWidget(filter_label)
        
        self.period_filter = PeriodFilter()
        self.period_filter.filter_changed.connect(self.on_filter_changed)
        filter_layout.addWidget(self.period_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Transactions table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(7)
        self.transactions_table.setHorizontalHeaderLabels([
            "Ngày", "Danh mục", "Mô tả", "Số tiền",
            "Loại", "Ngân sách", "Thao tác"
        ])
        
        # Set column widths
        self.transactions_table.horizontalHeader().setStretchLastSection(True)
        self.transactions_table.setColumnWidth(0, 100)  # Date
        self.transactions_table.setColumnWidth(1, 150)  # Category
        self.transactions_table.setColumnWidth(2, 200)  # Description
        self.transactions_table.setColumnWidth(3, 120)  # Amount
        self.transactions_table.setColumnWidth(4, 100)  # Type
        self.transactions_table.setColumnWidth(5, 150)  # Budget
        
        # Style the table
        self.transactions_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.transactions_table)
        self.setLayout(layout)
        
    def refresh_data(self):
        """Refresh transactions table data"""
        if not self.parent or not self.parent.current_user_id:
            return
            
        try:
            # Get transactions for current period
            transactions = self.parent.transaction_manager.get_transactions_by_date_range(
                user_id=self.parent.current_user_id,
                start_date=self.current_start_date_str,
                end_date=self.current_end_date_str
            )
            
            # Clear existing items
            self.transactions_table.setRowCount(0)
            
            # Add transactions to table
            for transaction in transactions:
                row = self.transactions_table.rowCount()
                self.transactions_table.insertRow(row)
                
                # Date
                date = datetime.fromisoformat(transaction.get('date')).strftime('%d/%m/%Y')
                self.transactions_table.setItem(row, 0, QTableWidgetItem(date))
                
                # Category
                category = self.parent.category_manager.get_category_by_id(
                    transaction.get('category_id')
                )
                category_name = category.get('name', '') if category else ''
                self.transactions_table.setItem(row, 1, QTableWidgetItem(category_name))
                
                # Description
                self.transactions_table.setItem(row, 2, QTableWidgetItem(transaction.get('description', '')))
                
                # Amount
                amount = f"{transaction.get('amount', 0):,.0f} đ"
                amount_item = QTableWidgetItem(amount)
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if transaction.get('type') == 'expense':
                    amount_item.setForeground(Qt.red)
                else:
                    amount_item.setForeground(Qt.darkGreen)
                self.transactions_table.setItem(row, 3, amount_item)
                
                # Type
                transaction_type = "Chi tiêu" if transaction.get('type') == 'expense' else "Thu nhập"
                type_item = QTableWidgetItem(transaction_type)
                type_item.setTextAlignment(Qt.AlignCenter)
                self.transactions_table.setItem(row, 4, type_item)
                
                # Budget
                budget = self.parent.budget_manager.get_budget_by_id(
                    transaction.get('budget_id')
                )
                budget_name = budget.get('name', '') if budget else ''
                self.transactions_table.setItem(row, 5, QTableWidgetItem(budget_name))
                
                # Actions button
                actions_btn = QPushButton("...")
                actions_btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        padding: 5px 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #f1f3f4;
                        border-radius: 4px;
                    }
                """)
                
                # Create actions menu
                menu = QMenu(self)
                
                edit_action = menu.addAction("Chỉnh sửa")
                edit_action.triggered.connect(lambda checked, t=transaction: self.edit_transaction(t))
                
                menu.addSeparator()
                
                delete_action = menu.addAction("Xóa")
                delete_action.triggered.connect(lambda checked, t=transaction: self.delete_transaction(t))
                
                actions_btn.setMenu(menu)
                
                self.transactions_table.setCellWidget(row, 6, actions_btn)
                
            # Update statistics panel
            self.stats_panel.update_data(
                user_id=self.parent.current_user_id,
                start_date=self.current_start_date_str,
                end_date=self.current_end_date_str
            )
                
        except Exception as e:
            self.parent.show_error(
                "Lỗi",
                f"Không thể tải danh sách giao dịch: {str(e)}"
            )
            
    def add_transaction(self):
        """Show dialog to add new transaction"""
        dialog = TransactionDialog(self, user_id=self.parent.current_user_id if self.parent else None)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_data()
            
    def edit_transaction(self, transaction_data):
        """Show dialog to edit transaction
        
        Args:
            transaction_data (dict): Transaction data dictionary
        """
        dialog = TransactionDialog(self, transaction_data, user_id=self.parent.current_user_id if self.parent else None)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_data()
            
    def delete_transaction(self, transaction_data):
        """Delete transaction
        
        Args:
            transaction_data (dict): Transaction data dictionary
        """
        transaction_id = transaction_data.get('transaction_id')
        if not transaction_id:
            return
            
        if self.parent.show_question(
            "Xóa giao dịch",
            "Bạn có chắc chắn muốn xóa giao dịch này? Hành động này không thể hoàn tác."
        ):
            try:
                success = self.parent.transaction_manager.delete_transaction(transaction_id)
                
                if success:
                    self.parent.show_info(
                        "Thành công",
                        "Đã xóa giao dịch thành công"
                    )
                    self.refresh_data()
                else:
                    self.parent.show_error(
                        "Lỗi",
                        "Không thể xóa giao dịch"
                    )
                    
            except Exception as e:
                self.parent.show_error(
                    "Lỗi",
                    f"Không thể xóa giao dịch: {str(e)}"
                )
                
    def on_filter_changed(self, start_date, end_date):
        """Handle period filter change
        
        Args:
            start_date (QDate): Selected start date from the filter
            end_date (QDate): Selected end date from the filter
        """
        self.current_start_date_str = start_date.toString("yyyy-MM-dd")
        self.current_end_date_str = end_date.toString("yyyy-MM-dd")
        self.refresh_data() 