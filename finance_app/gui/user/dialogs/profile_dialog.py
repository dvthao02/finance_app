from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QDateEdit,
                             QPushButton, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import QDate
from finance_app.data_manager.user_manager import UserManager

class ProfileDialog(QDialog):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self.user_manager = UserManager()
        self.init_ui()
        
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Cập nhật thông tin cá nhân")
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Full name
        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("Nhập họ tên")
        if self.user:
            self.fullname_input.setText(self.user.get('full_name', ''))
        layout.addRow("Họ tên:", self.fullname_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Nhập email")
        if self.user:
            self.email_input.setText(self.user.get('email', ''))
        layout.addRow("Email:", self.email_input)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Nhập số điện thoại")
        if self.user:
            self.phone_input.setText(self.user.get('phone', ''))
        layout.addRow("Số điện thoại:", self.phone_input)
        
        # Date of birth
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        if self.user and self.user.get('date_of_birth'):
            try:
                self.dob_input.setDate(QDate.fromString(self.user['date_of_birth'], "yyyy-MM-dd"))
            except:
                self.dob_input.setDate(QDate.currentDate())
        else:
            self.dob_input.setDate(QDate.currentDate())
        layout.addRow("Ngày sinh:", self.dob_input)
        
        # Address
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Nhập địa chỉ")
        if self.user:
            self.address_input.setText(self.user.get('address', ''))
        layout.addRow("Địa chỉ:", self.address_input)
        
        # Buttons
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.save_profile)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
        
    def save_profile(self):
        """Save profile data"""
        try:
            # Validate full name
            full_name = self.fullname_input.text().strip()
            if not full_name:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập họ tên")
                return
            
            # Validate email
            email = self.email_input.text().strip()
            if not email:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập email")
                return
            
            # Prepare profile data
            profile_data = {
                'full_name': full_name,
                'email': email,
                'phone': self.phone_input.text().strip(),
                'date_of_birth': self.dob_input.date().toString("yyyy-MM-dd"),
                'address': self.address_input.text().strip()
            }
            
            # Update user profile
            result = self.user_manager.update_profile(
                self.user['username'],
                **profile_data
            )
            
            if isinstance(result, tuple):
                success, message = result
                if not success:
                    QMessageBox.warning(self, "Lỗi", message)
                    return
                    
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
