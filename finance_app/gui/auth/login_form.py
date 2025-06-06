from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QWidget, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
import os
from finance_app.data_manager.user_manager import UserManager

class LoginForm(QDialog):
    login_success = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_manager = UserManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Đăng nhập tài khoản")
        self.setWindowIcon(QIcon(self.get_asset_path("app_icon.png")))
        self.setFixedSize(400, 450)

        self.setStyleSheet("QDialog { background-color: #f0f0f0; }")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setAlignment(Qt.AlignCenter)

        login_card = QWidget()
        login_card.setFixedWidth(380)
        login_card.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
            }
        """)
        card_layout = QVBoxLayout(login_card)
        card_layout.setContentsMargins(25, 20, 25, 20)
        card_layout.setSpacing(18)

        title = QLabel("Đăng nhập tài khoản")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #333333; 
            margin-top: 5px;
            margin-bottom: 20px;
        """)
        card_layout.addWidget(title)

        # Username
        username_label = QLabel("Tên đăng nhập")
        username_label.setStyleSheet("font-size: 14px; font-weight: bold; border: none; margin-bottom: 2px;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập tên đăng nhập")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
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
        self.username_input.setFixedHeight(40)
        card_layout.addWidget(username_label)
        card_layout.addWidget(self.username_input)

        # Password
        password_label = QLabel("Mật khẩu")
        password_label.setStyleSheet("font-size: 14px; font-weight: bold; border: none; margin-bottom: 2px; margin-top: 5px;")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Nhập mật khẩu")
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
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
        self.password_input.setFixedHeight(40)

        self.toggle_password_action = QAction(self)
        self.toggle_password_action.setIcon(QIcon(self.get_asset_path('eye_closed.png')))
        self.toggle_password_action.setToolTip("Hiện/Ẩn mật khẩu")
        self.toggle_password_action.triggered.connect(self.toggle_password_visibility)
        self.password_input.addAction(self.toggle_password_action, QLineEdit.TrailingPosition)

        card_layout.addWidget(password_label)
        card_layout.addWidget(self.password_input)
        card_layout.addSpacing(15)

        # Login button
        self.login_button = QPushButton("Đăng nhập")
        self.login_button.setFixedHeight(40)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton:pressed {
                background-color: #1256A1;
            }
        """)
        self.login_button.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_button)

        # Register button
        self.register_button = QPushButton("Chưa có tài khoản? Đăng ký ngay")
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.register_button.setStyleSheet("""
            QPushButton {
                color: #1A73E8; 
                border: none; 
                background-color: transparent;
                font-size: 13px;
                padding-top: 8px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        self.register_button.clicked.connect(self.show_register_form)
        card_layout.addWidget(self.register_button)

        self.main_layout.addWidget(login_card)

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_action.setIcon(QIcon(self.get_asset_path('eye_open.png')))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_action.setIcon(QIcon(self.get_asset_path('eye_closed.png')))

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu")
            return

        result = self.user_manager.authenticate_user(username, password)
        if result.get("status") == "success":
            self.login_success.emit(result["user"]["user_id"])
            self.accept()
        else:
            QMessageBox.critical(self, "Đăng nhập thất bại", result.get("message", "Tên đăng nhập hoặc mật khẩu không đúng"))

    def show_register_form(self):
        from finance_app.gui.auth.register_form import RegisterForm
        register_form = RegisterForm(self)
        register_form.register_success.connect(self.on_register_success_from_dialog)
        
        dialog_result = register_form.exec_()
        
        self.activateWindow()

    def on_register_success_from_dialog(self, user_id):
        QMessageBox.information(
            self, 
            "Đăng ký thành công", 
            "Tài khoản của bạn đã được tạo thành công. Vui lòng đăng nhập."
        )

    def get_asset_path(self, filename):
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_path, "assets", filename)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.handle_login()
