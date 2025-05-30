from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
                             QDateEdit, QSpinBox, QListWidget, QListWidgetItem,
                             QCheckBox)
from PyQt5.QtCore import Qt, QDate
from finance_app.gui.base.base_widget import BaseWidget
from datetime import datetime, date

class BudgetDialog(QDialog, BaseWidget):
    def __init__(self, parent=None, budget_data=None):
        super().__init__(parent)
        self.parent = parent
        self.budget_data = budget_data
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI"""
        # Set window properties
        self.setWindowTitle("Thêm ngân sách" if not self.budget_data else "Chỉnh sửa ngân sách")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Budget name
        name_label = self.create_label("Tên ngân sách", bold=True)
        self.name_input = self.create_input_field("Nhập tên ngân sách")
        if self.budget_data:
            self.name_input.setText(self.budget_data.get('name', ''))
            
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        
        # Budget type
        type_label = self.create_label("Loại ngân sách", bold=True)
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
        
        if self.budget_data:
            index = 1 if self.budget_data.get('type') == 'expense' else 0
            self.type_combo.setCurrentIndex(index)
            
        self.type_combo.currentIndexChanged.connect(self.load_categories)
        
        layout.addWidget(type_label)
        layout.addWidget(self.type_combo)
        
        # Categories
        categories_label = self.create_label("Danh mục", bold=True)
        self.categories_list = QListWidget()
        self.categories_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
                min-height: 150px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #f1f3f4;
            }
            QListWidget::item:selected {
                background-color: #e8f0fe;
                color: #1a73e8;
            }
        """)
        
        # Load categories
        self.load_categories()
        
        layout.addWidget(categories_label)
        layout.addWidget(self.categories_list)
        
        # Limit amount
        limit_label = self.create_label("Giới hạn", bold=True)
        self.limit_input = QSpinBox()
        self.limit_input.setRange(0, 1000000000)
        self.limit_input.setSingleStep(1000)
        self.limit_input.setSuffix(" đ")
        self.limit_input.setGroupSeparatorShown(True)
        self.limit_input.setStyleSheet("""
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
        
        if self.budget_data:
            self.limit_input.setValue(self.budget_data.get('limit', 0))
            
        layout.addWidget(limit_label)
        layout.addWidget(self.limit_input)
        
        # Period
        period_label = self.create_label("Thời gian", bold=True)
        period_layout = QHBoxLayout()
        
        # Start date
        start_label = self.create_label("Từ ngày:")
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setStyleSheet("""
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
        
        # End date
        end_label = self.create_label("Đến ngày:")
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addMonths(1))
        self.end_date.setStyleSheet(self.start_date.styleSheet())
        
        if self.budget_data:
            start_date = datetime.fromisoformat(self.budget_data.get('start_date'))
            end_date = datetime.fromisoformat(self.budget_data.get('end_date'))
            self.start_date.setDate(QDate(start_date.year, start_date.month, start_date.day))
            self.end_date.setDate(QDate(end_date.year, end_date.month, end_date.day))
            
        period_layout.addWidget(start_label)
        period_layout.addWidget(self.start_date)
        period_layout.addWidget(end_label)
        period_layout.addWidget(self.end_date)
        
        layout.addWidget(period_label)
        layout.addLayout(period_layout)
        
        # Description
        desc_label = self.create_label("Mô tả", bold=True)
        self.desc_input = self.create_input_field("Nhập mô tả (không bắt buộc)")
        if self.budget_data:
            self.desc_input.setText(self.budget_data.get('description', ''))
            
        layout.addWidget(desc_label)
        layout.addWidget(self.desc_input)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        cancel_btn = self.create_secondary_button("Hủy")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = self.create_primary_button("Lưu")
        save_btn.clicked.connect(self.save_budget)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
    def load_categories(self):
        """Load categories based on selected type"""
        try:
            # Clear current items
            self.categories_list.clear()
            
            # Get categories
            category_type = 'expense' if self.type_combo.currentText() == "Chi tiêu" else 'income'
            categories = self.parent.parent.category_manager.get_user_categories(
                self.parent.parent.current_user_id,
                category_type=category_type
            )
            
            # Add categories to list
            for category in categories:
                item = QListWidgetItem(category.get('name', ''))
                item.setData(Qt.UserRole, category.get('category_id'))
                
                # Create checkbox
                checkbox = QCheckBox()
                checkbox.setStyleSheet("""
                    QCheckBox {
                        margin: 5px;
                    }
                    QCheckBox::indicator {
                        width: 18px;
                        height: 18px;
                    }
                    QCheckBox::indicator:unchecked {
                        border: 2px solid #5f6368;
                        border-radius: 3px;
                        background-color: white;
                    }
                    QCheckBox::indicator:checked {
                        border: 2px solid #1a73e8;
                        border-radius: 3px;
                        background-color: #1a73e8;
                        image: url(assets/check.png);
                    }
                """)
                
                # Check if category is selected
                if self.budget_data:
                    category_ids = self.budget_data.get('category_ids', [])
                    if category.get('category_id') in category_ids:
                        checkbox.setChecked(True)
                        
                item.setData(Qt.UserRole + 1, checkbox)
                
                self.categories_list.addItem(item)
                self.categories_list.setItemWidget(item, checkbox)
                
        except Exception as e:
            self.parent.show_error(
                "Lỗi",
                f"Không thể tải danh sách danh mục: {str(e)}"
            )
            
    def save_budget(self):
        """Save budget data"""
        # Get form data
        name = self.name_input.text().strip()
        budget_type = 'expense' if self.type_combo.currentText() == "Chi tiêu" else 'income'
        limit = self.limit_input.value()
        start_date = self.start_date.date().toPyDate().isoformat()
        end_date = self.end_date.date().toPyDate().isoformat()
        description = self.desc_input.text().strip()
        
        # Get selected categories
        category_ids = []
        for i in range(self.categories_list.count()):
            item = self.categories_list.item(i)
            checkbox = self.categories_list.itemWidget(item)
            if checkbox.isChecked():
                category_ids.append(item.data(Qt.UserRole))
                
        # Validate data
        if not name:
            self.parent.show_warning(
                "Thiếu thông tin",
                "Vui lòng nhập tên ngân sách"
            )
            return
            
        if not category_ids:
            self.parent.show_warning(
                "Thiếu thông tin",
                "Vui lòng chọn ít nhất một danh mục"
            )
            return
            
        if limit <= 0:
            self.parent.show_warning(
                "Thiếu thông tin",
                "Vui lòng nhập giới hạn lớn hơn 0"
            )
            return
            
        if self.start_date.date() > self.end_date.date():
            self.parent.show_warning(
                "Lỗi",
                "Ngày bắt đầu phải nhỏ hơn ngày kết thúc"
            )
            return
            
        try:
            if self.budget_data:
                # Update existing budget
                success = self.parent.parent.budget_manager.update_budget(
                    budget_id=self.budget_data['budget_id'],
                    name=name,
                    type=budget_type,
                    category_ids=category_ids,
                    limit=limit,
                    start_date=start_date,
                    end_date=end_date,
                    description=description
                )
                
                if success:
                    self.parent.show_info(
                        "Thành công",
                        "Đã cập nhật ngân sách thành công"
                    )
                    self.accept()
                else:
                    self.parent.show_error(
                        "Lỗi",
                        "Không thể cập nhật ngân sách"
                    )
            else:
                # Create new budget
                success = self.parent.parent.budget_manager.create_budget(
                    user_id=self.parent.parent.current_user_id,
                    name=name,
                    type=budget_type,
                    category_ids=category_ids,
                    limit=limit,
                    start_date=start_date,
                    end_date=end_date,
                    description=description
                )
                
                if success:
                    self.parent.show_info(
                        "Thành công",
                        "Đã thêm ngân sách mới thành công"
                    )
                    self.accept()
                else:
                    self.parent.show_error(
                        "Lỗi",
                        "Không thể thêm ngân sách mới"
                    )
                    
        except Exception as e:
            self.parent.show_error(
                "Lỗi",
                f"Không thể lưu ngân sách: {str(e)}"
            )
