from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView

class TransactionTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'Date', 'Category', 'Description', 'Amount', 'Type', 'Balance'
        ])
        
        # Set column widths
        header = self.table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
            
        layout.addWidget(self.table)
        self.setLayout(layout)
        
    def update_transactions(self, transactions):
        """Update table with new transaction data
        Args:
            transactions: List of transaction dictionaries
        """
        self.table.setRowCount(len(transactions))
        
        for row, trans in enumerate(transactions):
            self.table.setItem(row, 0, QTableWidgetItem(trans['date']))
            self.table.setItem(row, 1, QTableWidgetItem(trans['category']))
            self.table.setItem(row, 2, QTableWidgetItem(trans['description']))
            self.table.setItem(row, 3, QTableWidgetItem(str(trans['amount'])))
            self.table.setItem(row, 4, QTableWidgetItem(trans['type']))
            self.table.setItem(row, 5, QTableWidgetItem(str(trans['balance'])))
