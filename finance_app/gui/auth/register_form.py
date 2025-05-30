from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
import os
from finance_app.data_manager.user_manager import UserManager

class RegisterForm(QDialog):
    """Form đăng ký người dùng mới"""
    register_success = pyqtSignal()  # Signal phát khi đăng ký thành công
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Đăng Ký Tài Khoản")
        self.setFixedSize(500, 700)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                font-family: Arial;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)
        
        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'logo.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)

        # Form container
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.StyledPanel)
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
            }
        """)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("ĐĂNG KÝ TÀI KHOẢN")
        title.setStyleSheet("""
            QLabel {
                color: #1a73e8;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title)

        # Input fields style
        input_style = """
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                min-height: 45px;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
            }
        """

        # Username
        username_layout = QVBoxLayout()
        username_layout.setSpacing(8)
        username_label = QLabel("Tên đăng nhập *")
        username_label.setStyleSheet("color: #5f6368; font-size: 14px; font-weight: bold;")
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Nhập tên đăng nhập (ít nhất 4 ký tự)")
        self.username_edit.setStyleSheet(input_style)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)
        form_layout.addLayout(username_layout)

        # Fullname
        fullname_layout = QVBoxLayout()
        fullname_layout.setSpacing(8)
        fullname_label = QLabel("Họ và tên *")
        fullname_label.setStyleSheet("color: #5f6368; font-size: 14px; font-weight: bold;")
        self.fullname_edit = QLineEdit()
        self.fullname_edit.setPlaceholderText("Nhập họ và tên")
        self.fullname_edit.setStyleSheet(input_style)
        fullname_layout.addWidget(fullname_label)
        fullname_layout.addWidget(self.fullname_edit)
        form_layout.addLayout(fullname_layout)

        # Password
        password_layout = QVBoxLayout()
        password_layout.setSpacing(8)
        password_label = QLabel("Mật khẩu *")
        password_label.setStyleSheet("color: #5f6368; font-size: 14px; font-weight: bold;")
        
        password_input_layout = QHBoxLayout()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Nhập mật khẩu")
        self.password_edit.setStyleSheet(input_style)
        
        self.toggle_password_btn = QPushButton()
        self.toggle_password_btn.setFixedSize(45, 45)
        self.toggle_password_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                                          'assets', 'eye_closed.png')))
        self.toggle_password_btn.setStyleSheet("""
            QPushButton {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 5px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                border: 2px solid #1a73e8;
            }
        """)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        
        password_input_layout.addWidget(self.password_edit)
        password_input_layout.addWidget(self.toggle_password_btn)
        
        password_layout.addWidget(password_label)
        password_layout.addLayout(password_input_layout)
        form_layout.addLayout(password_layout)

        # Confirm Password
        confirm_layout = QVBoxLayout()
        confirm_layout.setSpacing(8)
        confirm_label = QLabel("Xác nhận mật khẩu *")
        confirm_label.setStyleSheet("color: #5f6368; font-size: 14px; font-weight: bold;")
        
        confirm_input_layout = QHBoxLayout()
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.Password)
        self.confirm_edit.setPlaceholderText("Nhập lại mật khẩu")
        self.confirm_edit.setStyleSheet(input_style)
        
        self.toggle_confirm_btn = QPushButton()
        self.toggle_confirm_btn.setFixedSize(45, 45)
        self.toggle_confirm_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                                         'assets', 'eye_closed.png')))
        self.toggle_confirm_btn.setStyleSheet("""
            QPushButton {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 5px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                border: 2px solid #1a73e8;
            }
        """)
        self.toggle_confirm_btn.clicked.connect(self.toggle_confirm_visibility)
        
        confirm_input_layout.addWidget(self.confirm_edit)
        confirm_input_layout.addWidget(self.toggle_confirm_btn)
        
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addLayout(confirm_input_layout)
        form_layout.addLayout(confirm_layout)

        # Password requirements
        req_text = """
        Mật khẩu phải có:
        • Ít nhất 8 ký tự
        • Chữ hoa và chữ thường
        • Số
        • Ký tự đặc biệt (!@#$%^&*...)
        """
        req_label = QLabel(req_text)
        req_label.setStyleSheet("""
            QLabel {
                color: #5f6368;
                font-size: 12px;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 8px;
            }
        """)
        form_layout.addWidget(req_label)

        # Register button
        register_btn = QPushButton("Đăng ký")
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
            QPushButton:pressed {
                background-color: #104d9e;
            }
        """)
        register_btn.clicked.connect(self.register)
        form_layout.addWidget(register_btn)

        # Login link
        login_btn = QPushButton("Đã có tài khoản? Đăng nhập ngay")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setStyleSheet("""
            QPushButton {
                color: #1a73e8;
                border: none;
                font-size: 14px;
                padding: 10px;
                background: transparent;
            }
            QPushButton:hover {
                color: #1557b0;
                text-decoration: underline;
            }
        """)
        login_btn.clicked.connect(self.close)
        form_layout.addWidget(login_btn)

        form_frame.setLayout(form_layout)
        main_layout.addWidget(form_frame)

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_edit.echoMode() == QLineEdit.Password:
            self.password_edit.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                                              'assets', 'eye_open.png')))
        else:
            self.password_edit.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                                              'assets', 'eye_closed.png')))

    def toggle_confirm_visibility(self):
        """Toggle confirm password visibility"""
        if self.confirm_edit.echoMode() == QLineEdit.Password:
            self.confirm_edit.setEchoMode(QLineEdit.Normal)
            self.toggle_confirm_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                                             'assets', 'eye_open.png')))
        else:
            self.confirm_edit.setEchoMode(QLineEdit.Password)
            self.toggle_confirm_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                                             'assets', 'eye_closed.png')))

    def register(self):
        """Handle registration"""
        # Get input values
        username = self.username_edit.text().strip()
        fullname = self.fullname_edit.text().strip()
        password = self.password_edit.text()
        confirm = self.confirm_edit.text()

        # Validate input
        if not username or not fullname or not password or not confirm:
            QMessageBox.warning(
                self,
                "Thiếu thông tin",
                "Vui lòng điền đầy đủ thông tin bắt buộc",
                QMessageBox.Ok
            )
            return

        if len(username) < 4:
            QMessageBox.warning(
                self,
                "Tên đăng nhập không hợp lệ",
                "Tên đăng nhập phải có ít nhất 4 ký tự",
                QMessageBox.Ok
            )
            return

        if password != confirm:
            QMessageBox.warning(
                self,
                "Mật khẩu không khớp",
                "Mật khẩu xác nhận không khớp với mật khẩu đã nhập",
                QMessageBox.Ok
            )
            return

        # Create user
        try:
            user_manager = UserManager()
            result = user_manager.add_user(
                username=username,
                password=password,
                full_name=fullname
            )

            if result.get("success"):
                QMessageBox.information(
                    self,
                    "Đăng ký thành công",
                    "Tài khoản đã được tạo thành công",
                    QMessageBox.Ok
                )
                self.register_success.emit()
                self.close()
            else:
                QMessageBox.critical(
                    self,
                    "Đăng ký thất bại",
                    result.get("message", "Không thể tạo tài khoản"),
                    QMessageBox.Ok
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Đã xảy ra lỗi: {str(e)}",
                QMessageBox.Ok
            )

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.register() 