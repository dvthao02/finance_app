from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QFormLayout)

class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user = parent.user
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Đổi mật khẩu")
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Current password
        self.current_pass = QLineEdit()
        self.current_pass.setEchoMode(QLineEdit.Password)
        layout.addRow("Mật khẩu hiện tại:", self.current_pass)
        
        # New password
        self.new_pass = QLineEdit()
        self.new_pass.setEchoMode(QLineEdit.Password)
        layout.addRow("Mật khẩu mới:", self.new_pass)
        
        # Confirm new password
        self.confirm_pass = QLineEdit()
        self.confirm_pass.setEchoMode(QLineEdit.Password)
        layout.addRow("Xác nhận mật khẩu mới:", self.confirm_pass)
        
        # Password requirements
        requirements = QLabel(
            "Mật khẩu phải có ít nhất:\n"
            "- 8 ký tự\n"
            "- 1 chữ hoa\n"
            "- 1 chữ thường\n"
            "- 1 số\n"
            "- 1 ký tự đặc biệt"
        )
        requirements.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addRow(requirements)
        
        # Change button
        change_btn = QPushButton("Đổi mật khẩu")
        change_btn.clicked.connect(self.change_password)
        layout.addRow(change_btn)
        
    def change_password(self):
        """Handle password change"""
        current = self.current_pass.text()
        new = self.new_pass.text()
        confirm = self.confirm_pass.text()
        
        if not all([current, new, confirm]):
            QMessageBox.warning(self, "Lỗi", "Vui lòng điền đầy đủ thông tin")
            return
            
        if new != confirm:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu mới không khớp")
            return
            
        try:
            self.parent().parent().user_manager.change_password(
                self.user['username'],
                current,
                new
            )
            QMessageBox.information(self, "Thành công", "Đã đổi mật khẩu thành công")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
