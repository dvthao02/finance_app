from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit,
                             QPushButton, QHBoxLayout, QMessageBox, QComboBox, QDateEdit)
from PyQt5.QtCore import QDate

class UserDialog(QDialog):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self.user_manager = parent.user_manager if parent else None
        self.init_ui()
        
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Thêm người dùng mới" if not self.user else "Sửa thông tin người dùng")
        self.setMinimumWidth(450)
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Username
        self.username_input = QLineEdit()
        if self.user:
            self.username_input.setText(self.user['username'])
            self.username_input.setEnabled(False)
        else:
            self.username_input.setPlaceholderText("Nhập tên đăng nhập")
        layout.addRow("Tên đăng nhập:", self.username_input)
        
        # Password (only for new users)
        if not self.user:
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_input.setPlaceholderText("Nhập mật khẩu")
            layout.addRow("Mật khẩu:", self.password_input)
        
        # Full name
        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("Nhập họ và tên")
        if self.user:
            self.fullname_input.setText(self.user['full_name'])
        layout.addRow("Họ và tên:", self.fullname_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Nhập địa chỉ email")
        if self.user:
            self.email_input.setText(self.user['email'])
        layout.addRow("Email:", self.email_input)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Nhập số điện thoại")
        if self.user:
            self.phone_input.setText(self.user['phone'])
        layout.addRow("Số điện thoại:", self.phone_input)
        
        # Role
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Người dùng", "Quản trị viên"])
        if self.user and self.user.get('is_admin', False):
            self.role_combo.setCurrentText("Quản trị viên")
        layout.addRow("Vai trò:", self.role_combo)
        
        # Date of birth
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        if self.user and self.user.get('date_of_birth'):
            self.dob_input.setDate(QDate.fromString(self.user['date_of_birth'], "yyyy-MM-dd"))
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
        button_box = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.save_user)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        button_box.addWidget(save_btn)
        button_box.addWidget(cancel_btn)
        layout.addRow(button_box)
        
    def save_user(self):
        """Save user data"""
        try:
            username = self.username_input.text().strip()
            if not username:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tên đăng nhập")
                return

            user_data = {
                'full_name': self.fullname_input.text().strip(),
                'email': self.email_input.text().strip(),
                'phone': self.phone_input.text().strip(),
                'date_of_birth': self.dob_input.date().toString("yyyy-MM-dd"),
                'address': self.address_input.text().strip(),
                'is_admin': self.role_combo.currentText() == "Quản trị viên"
            }

            if not user_data['full_name']:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập họ và tên")
                return

            if self.user:  # Update existing user
                update_payload = {
                    'full_name': user_data['full_name'],
                    'email': user_data['email'],
                    'phone': user_data['phone'],
                    'date_of_birth': user_data['date_of_birth'],
                    'address': user_data['address']
                }
                success = self.user_manager.update_user(self.user['user_id'], **update_payload)
                if not success:
                    QMessageBox.critical(self, "Lỗi", "Không thể cập nhật thông tin người dùng.")
                    return
            else:  # Add new user
                password = self.password_input.text().strip()
                if not password:
                    QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập mật khẩu")
                    return

                # Pass all relevant fields to add_user, including is_admin
                result = self.user_manager.add_user(
                    username=username,
                    password=password,
                    full_name=user_data['full_name'],
                    email=user_data['email'],
                    phone=user_data['phone'],
                    date_of_birth=user_data['date_of_birth'],
                    address=user_data['address'],
                    is_admin=user_data['is_admin']
                )
                if isinstance(result, dict) and result.get('status') == 'error':
                    QMessageBox.critical(self, "Lỗi", result.get('message', 'Không thể thêm người dùng.'))
                    self.error_message = result.get('message', 'Không thể thêm người dùng.')
                    return
                self.error_message = None
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
            self.error_message = str(e)
            
            
class ResetPasswordDialog(QDialog):
    def __init__(self, parent=None, user_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.user_manager = parent.user_manager if parent and hasattr(parent, 'user_manager') else None
        if not self.user_manager:
            # This should not happen if called from AdminUsersPage correctly
            QMessageBox.critical(self, "Lỗi", "Không thể truy cập User Manager.")
            # Consider closing the dialog or disabling save if user_manager is not available
            # self.close()
            pass 
        self.init_ui()
        
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Đặt lại mật khẩu")
        layout = QFormLayout()
        self.setLayout(layout)
        
        # New password
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Nhập mật khẩu mới")
        layout.addRow("Mật khẩu mới:", self.password_input)
        
        # Confirm password
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setPlaceholderText("Nhập lại mật khẩu mới")
        layout.addRow("Xác nhận:", self.confirm_input)
        
        # Buttons
        button_box = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.save_password)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        button_box.addWidget(save_btn)
        button_box.addWidget(cancel_btn)
        layout.addRow(button_box)
        
    def save_password(self):
        """Save new password"""
        if not self.user_manager or not self.user_id:
            QMessageBox.critical(self, "Lỗi", "Không thể thực hiện thao tác. Thiếu User Manager hoặc User ID.")
            return

        try:
            password = self.password_input.text().strip()
            confirm = self.confirm_input.text().strip()
            
            if not password or not confirm:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đầy đủ thông tin")
                return
                
            if password != confirm:
                QMessageBox.warning(self, "Cảnh báo", "Mật khẩu xác nhận không khớp")
                return
            
            # Call the new admin_reset_password method
            result = self.user_manager.admin_reset_password(self.user_id, password)
            
            if result.get("status") == "success":
                QMessageBox.information(self, "Thành công", result.get("message", "Đã đặt lại mật khẩu thành công."))
                self.accept()
            else:
                QMessageBox.critical(self, "Lỗi", result.get("message", "Không thể đặt lại mật khẩu."))
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi: {str(e)}")
