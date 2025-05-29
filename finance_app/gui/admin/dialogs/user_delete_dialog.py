from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QMessageBox,
                           QPushButton, QCheckBox, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt

class UserDeleteDialog(QDialog):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self.init_ui()
        
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Xác nhận xóa người dùng")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Warning icon and text
        warning_label = QLabel(
            f"Bạn sắp xóa người dùng {self.user.get('username', '')}"
        )
        warning_label.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        layout.addWidget(warning_label)
        
        # Details
        details_label = QLabel(
            "Các dữ liệu sau sẽ bị xóa:\n"
            "- Thông tin cá nhân\n"
            "- Tất cả giao dịch\n"
            "- Tất cả ngân sách\n"
            "- Tất cả giao dịch định kỳ\n"
            "- Tất cả thông báo\n\n"
            "Hành động này không thể hoàn tác!"
        )
        details_label.setWordWrap(True)
        layout.addWidget(details_label)
        
        # Confirmation checkbox
        self.confirm_check = QCheckBox("Tôi hiểu và muốn xóa người dùng này")
        layout.addWidget(self.confirm_check)
        
        # Spacer
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Buttons
        buttons_layout = QVBoxLayout()
        
        self.delete_button = QPushButton("Xóa người dùng")
        self.delete_button.setEnabled(False)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.delete_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("Hủy")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Connect checkbox to enable/disable delete button
        self.confirm_check.stateChanged.connect(self._handle_confirm_check)
        
    def _handle_confirm_check(self, state):
        """Enable delete button only when checkbox is checked"""
        self.delete_button.setEnabled(state == Qt.Checked)
