from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget, QTableWidget,
                             QTableWidgetItem, QPushButton, QDialog, QLabel,
                             QLineEdit, QComboBox, QMessageBox, QMenu, QFrame, QWidget,
                             QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from finance_app.gui.base.base_widget import BaseWidget
from finance_app.gui.user.dialogs.budget_dialog import BudgetDialog
from finance_app.gui.components.period_filter import PeriodFilter
from datetime import datetime

class BudgetCard(QFrame):
    def __init__(self, budget_data, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.budget_data = budget_data
        self.init_ui()
        
    def init_ui(self):
        """Initialize the budget card UI"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Card style
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Title and type
        title_layout = QVBoxLayout()
        
        name_label = QLabel(self.budget_data.get('name', ''))
        name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_layout.addWidget(name_label)
        
        budget_type = "Chi tiêu" if self.budget_data.get('type') == 'expense' else "Thu nhập"
        type_label = QLabel(budget_type)
        type_label.setStyleSheet("color: #5f6368;")
        title_layout.addWidget(type_label)
        
        header_layout.addLayout(title_layout)
        
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
        edit_action.triggered.connect(lambda: self.parent.edit_budget(self.budget_data))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("Xóa")
        delete_action.triggered.connect(lambda: self.parent.delete_budget(self.budget_data))
        
        actions_btn.setMenu(menu)
        header_layout.addWidget(actions_btn)
        
        layout.addLayout(header_layout)
        
        # Progress bar
        progress_layout = QVBoxLayout()
        
        # Get total amount and limit
        total = self.parent.parent.transaction_manager.get_budget_total(
            self.budget_data.get('budget_id')
        )
        limit = self.budget_data.get('limit', 0)
        
        # Progress percentage
        progress = min(int((total / limit * 100) if limit > 0 else 0), 100)
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(progress)
        
        # Style based on progress
        if progress >= 100:
            color = "#e74c3c"  # Red
        elif progress >= 80:
            color = "#f39c12"  # Orange
        else:
            color = "#2ecc71"  # Green
            
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 5px;
                background-color: #f5f6f7;
                height: 10px;
                text-align: center;
            }}
            
            QProgressBar::chunk {{
                border-radius: 5px;
                background-color: {color};
            }}
        """)
        
        progress_layout.addWidget(progress_bar)
        
        # Amount labels
        amount_layout = QHBoxLayout()
        
        # Total amount
        total_label = QLabel(f"{total:,.0f} đ")
        total_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        amount_layout.addWidget(total_label)
        
        # Limit amount
        limit_label = QLabel(f"/ {limit:,.0f} đ")
        limit_label.setStyleSheet("color: #5f6368;")
        amount_layout.addWidget(limit_label)
        
        amount_layout.addStretch()
        
        # Remaining amount
        remaining = max(limit - total, 0)
        remaining_label = QLabel(f"Còn lại: {remaining:,.0f} đ")
        remaining_label.setStyleSheet("color: #5f6368;")
        amount_layout.addWidget(remaining_label)
        
        progress_layout.addLayout(amount_layout)
        layout.addLayout(progress_layout)
        
        # Categories
        categories_layout = QVBoxLayout()
        
        categories_label = QLabel("Danh mục:")
        categories_label.setStyleSheet("color: #5f6368; margin-top: 10px;")
        categories_layout.addWidget(categories_label)
        
        category_ids = self.budget_data.get('category_ids', [])
        if category_ids:
            categories = []
            for category_id in category_ids:
                category = self.parent.parent.category_manager.get_category_by_id(category_id)
                if category:
                    categories.append(category.get('name', ''))
                    
            category_list = QLabel(", ".join(categories))
            category_list.setWordWrap(True)
            categories_layout.addWidget(category_list)
        else:
            no_categories = QLabel("Chưa có danh mục")
            no_categories.setStyleSheet("color: #5f6368; font-style: italic;")
            categories_layout.addWidget(no_categories)
            
        layout.addLayout(categories_layout)
        
        # Period
        period_layout = QVBoxLayout()
        
        period_label = QLabel("Thời gian:")
        period_label.setStyleSheet("color: #5f6368; margin-top: 10px;")
        period_layout.addWidget(period_label)
        
        start_date = datetime.fromisoformat(self.budget_data.get('start_date')).strftime('%d/%m/%Y')
        end_date = datetime.fromisoformat(self.budget_data.get('end_date')).strftime('%d/%m/%Y')
        date_label = QLabel(f"{start_date} - {end_date}")
        period_layout.addWidget(date_label)
        
        layout.addLayout(period_layout)
        
        self.setLayout(layout)

class BudgetsPage(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_period = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the budgets page UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Page header
        header_layout = QHBoxLayout()
        
        # Title
        title = self.create_title_label("Quản lý ngân sách")
        header_layout.addWidget(title)
        
        # Add budget button
        add_btn = self.create_primary_button("Thêm ngân sách")
        add_btn.clicked.connect(self.add_budget)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Period filter
        filter_layout = QHBoxLayout()
        
        filter_label = self.create_label("Lọc theo thời gian:", bold=True)
        filter_layout.addWidget(filter_label)
        
        self.period_filter = PeriodFilter()
        self.period_filter.filter_changed.connect(self.on_filter_changed)
        filter_layout.addWidget(self.period_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Budgets container
        self.budgets_layout = QVBoxLayout()
        self.budgets_layout.setSpacing(15)
        
        layout.addLayout(self.budgets_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def refresh_data(self):
        """Refresh budgets data"""
        if not self.parent or not self.parent.current_user_id:
            return
            
        try:
            # Clear existing budget cards
            for i in reversed(range(self.budgets_layout.count())):
                widget = self.budgets_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
                    
            # Get budgets for current period (using start and end dates)
            budgets = self.parent.budget_manager.get_user_budgets_by_date_range(
                user_id=self.parent.current_user_id,
                start_date_str=getattr(self, 'current_start_date_str', None),
                end_date_str=getattr(self, 'current_end_date_str', None)
            )
            
            # Add budget cards
            for budget in budgets:
                card = BudgetCard(budget, self)
                self.budgets_layout.addWidget(card)
                
        except Exception as e:
            self.parent.show_error(
                "Lỗi",
                f"Không thể tải danh sách ngân sách: {str(e)}"
            )
            
    def add_budget(self):
        """Show dialog to add new budget"""
        dialog = BudgetDialog(self, user_id=self.parent.current_user_id if self.parent else None)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_data()
            
    def edit_budget(self, budget_data):
        """Show dialog to edit budget
        
        Args:
            budget_data (dict): Budget data dictionary
        """
        dialog = BudgetDialog(self, budget_data, user_id=self.parent.current_user_id if self.parent else None)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_data()
            
    def delete_budget(self, budget_data):
        """Delete budget
        
        Args:
            budget_data (dict): Budget data dictionary
        """
        budget_id = budget_data.get('budget_id')
        if not budget_id:
            return
            
        if self.parent.show_question(
            "Xóa ngân sách",
            "Bạn có chắc chắn muốn xóa ngân sách này? Hành động này không thể hoàn tác."
        ):
            try:
                success = self.parent.budget_manager.delete_budget(budget_id)
                
                if success:
                    self.parent.show_info(
                        "Thành công",
                        "Đã xóa ngân sách thành công"
                    )
                    self.refresh_data()
                else:
                    self.parent.show_error(
                        "Lỗi",
                        "Không thể xóa ngân sách"
                    )
                    
            except Exception as e:
                self.parent.show_error(
                    "Lỗi",
                    f"Không thể xóa ngân sách: {str(e)}"
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