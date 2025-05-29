from PyQt5.QtWidgets import QWidget
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtGui import QPainter

class BudgetChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
    def update_chart(self, budget_data):
        """Update chart with new budget data
        Args:
            budget_data: Dictionary containing budget category and amount
        """
        series = QPieSeries()
        
        for category, amount in budget_data.items():
            series.append(category, amount)
            
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Budget Distribution")
        
        self.chart_view.setChart(chart)
