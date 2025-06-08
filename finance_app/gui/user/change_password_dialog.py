from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QFormLayout)
from finance_app.data_manager.user_manager import UserManager  # Import UserManager

class ChangePasswordDialog(QDialog):
    def __init__(self, user_id, parent=None): # Modified constructor
        super().__init__(parent)
        self.user_id = user_id # Store user_id
        self.user_manager = UserManager() # Instantiate UserManager
        # self.user = parent.user  # This line is problematic and removed
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Đổi mật khẩu")
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Current password
        self.current_pass = QLineEdit()
        self.current_pass.setEchoMode(QLineEdit.Password)
        self.current_pass.setObjectName("current_pass")
        self.current_pass.setFixedHeight(40)
        layout.addRow("Mật khẩu hiện tại:", self._add_password_with_eye(self.current_pass))
        
        # New password
        self.new_pass = QLineEdit()
        self.new_pass.setEchoMode(QLineEdit.Password)
        self.new_pass.setObjectName("new_pass")
        self.new_pass.setFixedHeight(40)
        layout.addRow("Mật khẩu mới:", self._add_password_with_eye(self.new_pass))
        
        # Confirm new password
        self.confirm_pass = QLineEdit()
        self.confirm_pass.setEchoMode(QLineEdit.Password)
        self.confirm_pass.setObjectName("confirm_pass")
        self.confirm_pass.setFixedHeight(40)
        layout.addRow("Xác nhận mật khẩu mới:", self._add_password_with_eye(self.confirm_pass))
        
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

    def _add_password_with_eye(self, line_edit):
        """Add an eye icon button to toggle password visibility for a QLineEdit, styled for clear visibility."""
        from PyQt5.QtWidgets import QAction
        from PyQt5.QtGui import QIcon
        import os
        # Set style for QLineEdit to ensure padding for the icon
        line_edit.setStyleSheet("""
            QLineEdit {
                padding-right: 32px;
                font-size: 14px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            QLineEdit:focus {
                border: 1px solid #1a73e8;
                background-color: white;
            }
        """)
        line_edit.setFixedHeight(40)
        line_edit.setMinimumWidth(220)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )
        eye_open = os.path.join(project_root, 'assets', 'eye_open.png')
        eye_closed = os.path.join(project_root, 'assets', 'eye_closed.png')
        action = QAction(line_edit)
        action.setText('👁')
        if os.path.exists(eye_closed):
            icon = QIcon(eye_closed)
            action.setIcon(icon)
            action.setIconVisibleInMenu(False)
        action.setToolTip("Hiện/Ẩn mật khẩu")
        line_edit.addAction(action, line_edit.TrailingPosition)
        def toggle():
            if line_edit.echoMode() == line_edit.Password:
                line_edit.setEchoMode(line_edit.Normal)
                if os.path.exists(eye_open):
                    action.setIcon(QIcon(eye_open))
            else:
                line_edit.setEchoMode(line_edit.Password)
                if os.path.exists(eye_closed):
                    action.setIcon(QIcon(eye_closed))
        action.triggered.connect(toggle)
        return line_edit

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
            # Use self.user_manager and self.user_id
            success, message = self.user_manager.change_password(
                self.user_id,
                current,
                new
            )
            if success:
                QMessageBox.information(self, "Thành công", "Đã đổi mật khẩu thành công")
                self.accept()
            else:
                QMessageBox.critical(self, "Lỗi", message) # Display message from user_manager
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
