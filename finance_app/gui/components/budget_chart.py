from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt

class BudgetChart(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title label
        title = QLabel("Phân bổ ngân sách")
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Create chart
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setTheme(QChart.ChartThemeLight)
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignRight)
        
        # Create chart view
        self.chartView = QChartView(self.chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.chartView)
        
        self.setLayout(layout)
        
    def update_chart(self, budgets):
        """Update the pie chart with budget data"""
        try:
            # Clear existing series
            self.chart.removeAllSeries()
            
            if not budgets:
                # Show empty state
                self.chart.setTitle("Chưa có ngân sách nào được thiết lập")
                return
                
            # Create pie series
            series = QPieSeries()
            
            # Color palette for different categories
            colors = [
                "#2ecc71", "#3498db", "#9b59b6", "#e74c3c", "#f1c40f",
                "#1abc9c", "#34495e", "#e67e22", "#7f8c8d", "#16a085"
            ]
            
            # Add slices for each budget category
            for i, budget in enumerate(budgets):
                try:
                    # Get category name from budget data
                    category_name = budget.get('category_name', 'Unknown')
                    amount = float(budget.get('amount', 0))
                    
                    if amount <= 0:
                        continue
                        
                    slice = QPieSlice(category_name, amount)
                    color = QColor(colors[i % len(colors)])
                    slice.setBrush(color)
                    slice.setLabelVisible(True)
                    
                    # Calculate percentage
                    total = sum(float(b.get('amount', 0)) for b in budgets)
                    percentage = (amount / total) * 100 if total > 0 else 0
                    
                    # Format label with amount and percentage
                    formatted_amount = "{:,.0f}".format(amount)
                    slice.setLabel(f"{category_name}\n{formatted_amount}đ\n({percentage:.1f}%)")
                    
                    series.append(slice)
                    
                except (ValueError, KeyError) as e:
                    print(f"Error processing budget item: {str(e)}")
                    continue
            
            self.chart.addSeries(series)
            self.chart.setTitle("Phân bổ ngân sách theo danh mục")
            
        except Exception as e:
            print(f"Error updating budget chart: {str(e)}")
            self.chart.setTitle("Lỗi khi cập nhật biểu đồ ngân sách")
    
    def resizeEvent(self, event):
        """Handle widget resize event"""
        super().resizeEvent(event)
        self.chartView.setMinimumSize(self.width(), int(self.height() * 0.8))
