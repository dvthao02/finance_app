from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QDateEdit, QPushButton)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from datetime import datetime, timedelta
import calendar
import os

class PeriodFilter(QWidget):
    """Widget for filtering data by time period"""
    
    # Signal emitted when filter changes
    filter_changed = pyqtSignal(QDate, QDate)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._block_recursion = False
        # Attempt to get a base path for assets, assuming this file is in a subdirectory of 'gui'
        try:
            # finance_app/gui/components/period_filter.py -> finance_app/gui
            gui_base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # finance_app/gui -> finance_app
            app_base_path = os.path.dirname(gui_base_path)
            # finance_app -> project_root (if assets is here)
            self.assets_path_prefix = os.path.join(os.path.dirname(app_base_path), 'assets').replace('\\', '/') + '/'
            if not os.path.exists(os.path.join(os.path.dirname(app_base_path), 'assets')):
                 # Fallback if assets is not at project_root/assets, but maybe finance_app/assets
                 self.assets_path_prefix = os.path.join(app_base_path, 'assets').replace('\\', '/') + '/'
                 if not os.path.exists(os.path.join(app_base_path, 'assets')):
                     # Final fallback: assume assets is in the same dir as gui (project_root/gui/assets)
                     # This might be incorrect depending on project structure.
                     self.assets_path_prefix = os.path.join(gui_base_path, 'assets').replace('\\', '/') + '/'
                     if not os.path.exists(os.path.join(gui_base_path, 'assets')):
                        print(f"Warning: Could not reliably determine assets path for PeriodFilter. Assuming relative 'assets/'. Path found: {self.assets_path_prefix}")
                        self.assets_path_prefix = "assets/" # Default if path not found

        except Exception as e:
            print(f"Error determining assets path: {e}")
            self.assets_path_prefix = "assets/" # Fallback

        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Period selector
        period_label = QLabel("Thời gian:")
        period_label.setStyleSheet("color: #5f6368; font-weight: bold;")
        
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Hôm nay",      # 0
            "Tuần này",     # 1
            "Tháng này",    # 2
            "Quý này",      # 3
            "Năm nay",      # 4
            "Tùy chọn"      # 5
        ])
        self.period_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 5px 10px;
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                min-width: 120px;
            }}
            QComboBox:focus {{
                border: 2px solid #1a73e8;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: url({self.assets_path_prefix}down_arrow.png);
                width: 12px;
                height: 12px;
            }}
        """)
        self.period_combo.currentIndexChanged.connect(self._handle_period_selection_change)
        
        # Date range
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setStyleSheet("""
            QDateEdit {
                padding: 5px 10px;
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }
            QDateEdit:focus {
                border: 2px solid #1a73e8;
            }
        """)
        self.start_date_edit.dateChanged.connect(self._handle_custom_date_change)
        
        date_separator = QLabel("đến")
        date_separator.setStyleSheet("color: #5f6368;")
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setStyleSheet(self.start_date_edit.styleSheet())
        self.end_date_edit.dateChanged.connect(self._handle_custom_date_change)
        
        # Add widgets to layout
        layout.addWidget(period_label)
        layout.addWidget(self.period_combo)
        layout.addWidget(self.start_date_edit)
        layout.addWidget(date_separator)
        layout.addWidget(self.end_date_edit)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Set initial period
        self.period_combo.setCurrentIndex(2)  # "Tháng này"
        
    def _handle_period_selection_change(self, index):
        """Handle period selection change from the QComboBox."""
        if self._block_recursion:
            return

        self._block_recursion = True
        try:
            today = datetime.now().date()
            start_dt, end_dt = None, None

            if index == 0:  # Hôm nay
                start_dt = today
                end_dt = today
            elif index == 1:  # Tuần này
                start_dt = today - timedelta(days=today.weekday())
                end_dt = start_dt + timedelta(days=6)
            elif index == 2:  # Tháng này
                start_dt = today.replace(day=1)
                _, last_day = timedelta(days=0), timedelta(days=calendar.monthrange(today.year, today.month)[1]-1)
                end_dt = start_dt + last_day
            elif index == 3:  # Quý này
                current_quarter = (today.month - 1) // 3
                start_dt = datetime(today.year, 3 * current_quarter + 1, 1).date()
                end_month = 3 * current_quarter + 3
                end_dt = datetime(today.year, end_month, calendar.monthrange(today.year, end_month)[1]).date()
            elif index == 4:  # Năm nay
                start_dt = today.replace(month=1, day=1)
                end_dt = today.replace(month=12, day=31)
            elif index == 5:  # Tùy chọn
                self.filter_changed.emit(self.start_date_edit.date(), self.end_date_edit.date())
                return
            else: # Should not happen
                return

            if start_dt and end_dt:
                self.start_date_edit.blockSignals(True)
                self.end_date_edit.blockSignals(True)
                
                self.start_date_edit.setDate(QDate(start_dt.year, start_dt.month, start_dt.day))
                self.end_date_edit.setDate(QDate(end_dt.year, end_dt.month, end_dt.day))
                
                self.start_date_edit.blockSignals(False)
                self.end_date_edit.blockSignals(False)
                
                self.filter_changed.emit(self.start_date_edit.date(), self.end_date_edit.date())
        finally:
            self._block_recursion = False
            
    def _handle_custom_date_change(self):
        """Handle date range change from QDateEdit widgets."""
        if self._block_recursion:
            return

        self._block_recursion = True
        try:
            if self.period_combo.currentIndex() != 5:
                self.period_combo.blockSignals(True)
                self.period_combo.setCurrentIndex(5)
                self.period_combo.blockSignals(False)
            
            self.filter_changed.emit(self.start_date_edit.date(), self.end_date_edit.date())
        finally:
            self._block_recursion = False
        
    def get_date_range(self):
        """Get selected date range
        
        Returns:
            tuple: (start_date, end_date) as QDate objects
        """
        return (self.start_date_edit.date(), self.end_date_edit.date()) 