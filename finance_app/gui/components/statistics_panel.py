from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class StatisticsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Grid for statistics
        grid = QGridLayout()
        
        # Create labels
        self.total_income = self._create_stat_label("Total Income", "0")
        self.total_expenses = self._create_stat_label("Total Expenses", "0")
        self.net_worth = self._create_stat_label("Net Worth", "0")
        self.budget_status = self._create_stat_label("Budget Status", "On Track")
        
        # Add to grid
        grid.addLayout(self.total_income, 0, 0)
        grid.addLayout(self.total_expenses, 0, 1)
        grid.addLayout(self.net_worth, 1, 0)
        grid.addLayout(self.budget_status, 1, 1)
        
        layout.addLayout(grid)
        self.setLayout(layout)
        
    def _create_stat_label(self, title, value):
        """Create a statistics label with title and value
        Args:
            title: Title of the statistic
            value: Value to display
        Returns:
            QVBoxLayout containing the labels
        """
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 10))
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return layout
        
    def update_statistics(self, stats):
        """Update statistics panel with new data
        Args:
            stats: Dictionary containing statistics data
        """
        self.total_income.itemAt(1).widget().setText(f"${stats['total_income']:,.2f}")
        self.total_expenses.itemAt(1).widget().setText(f"${stats['total_expenses']:,.2f}")
        self.net_worth.itemAt(1).widget().setText(f"${stats['net_worth']:,.2f}")
        self.budget_status.itemAt(1).widget().setText(stats['budget_status'])
