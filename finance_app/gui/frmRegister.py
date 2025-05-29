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
        self.setMinimumSize(500, 650)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setup_ui()

    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        self.setLayout(main_layout)
        
        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)
        main_layout.addSpacing(20)

        # Form container
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.StyledPanel)
        form_frame.setMinimumWidth(400)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(25, 25, 25, 25)

        # Title
        title = QLabel("ĐĂNG KÝ TÀI KHOẢN")
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title)
        form_layout.addSpacing(10)

        # Input fields style
        input_style = """
            QLineEdit {
                padding: 10px 15px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
                min-height: 40px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """

        # Username
        username_layout = QVBoxLayout()
        username_layout.setSpacing(8)
        username_label = QLabel("Tên đăng nhập *")
        username_label.setStyleSheet("color: #7f8c8d; font-size: 14px; font-weight: bold;")
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Nhập tên đăng nhập")
        self.username_edit.setStyleSheet(input_style)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)
        form_layout.addLayout(username_layout)

        # Fullname
        fullname_layout = QVBoxLayout()
        fullname_layout.setSpacing(8)
        fullname_label = QLabel("Họ và tên *")
        fullname_label.setStyleSheet("color: #7f8c8d; font-size: 14px; font-weight: bold;")
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
        password_label.setStyleSheet("color: #7f8c8d; font-size: 14px; font-weight: bold;")
        
        password_input_layout = QHBoxLayout()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Nhập mật khẩu")
        self.password_edit.setStyleSheet(input_style)
        
        self.toggle_password_btn = QPushButton()
        self.toggle_password_btn.setFixedSize(40, 40)
        self.toggle_password_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                                          'assets', 'eye_closed.png')))
        self.toggle_password_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
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
        confirm_label.setStyleSheet("color: #7f8c8d; font-size: 14px; font-weight: bold;")
        
        confirm_input_layout = QHBoxLayout()
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.Password)
        self.confirm_edit.setPlaceholderText("Nhập lại mật khẩu")
        self.confirm_edit.setStyleSheet(input_style)
        
        self.toggle_confirm_btn = QPushButton()
        self.toggle_confirm_btn.setFixedSize(40, 40)
        self.toggle_confirm_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                                         'assets', 'eye_closed.png')))
        self.toggle_confirm_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
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
                color: #95a5a6;
                font-size: 12px;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
        """)
        form_layout.addWidget(req_label)
        form_layout.addSpacing(10)

        # Buttons
        register_btn = QPushButton("Đăng ký")
        register_btn.setMinimumHeight(45)
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2472a4;
            }
        """)
        register_btn.clicked.connect(self.register)
        form_layout.addWidget(register_btn)

        back_btn = QPushButton("Quay lại đăng nhập")
        back_btn.setStyleSheet("""
            QPushButton {
                color: #3498db;
                border: none;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton:hover {
                color: #2980b9;
                text-decoration: underline;
            }
        """)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(self.reject)
        form_layout.addWidget(back_btn)

        form_frame.setLayout(form_layout)
        main_layout.addWidget(form_frame)

    def toggle_password_visibility(self):
        """Chuyển đổi hiển thị/ẩn mật khẩu"""
        if self.password_edit.echoMode() == QLineEdit.Password:
            self.password_edit.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                                             'assets', 'eye_open.png')))
        else:
            self.password_edit.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                                             'assets', 'eye_closed.png')))

    def toggle_confirm_visibility(self):
        """Chuyển đổi hiển thị/ẩn xác nhận mật khẩu"""
        if self.confirm_edit.echoMode() == QLineEdit.Password:
            self.confirm_edit.setEchoMode(QLineEdit.Normal)
            self.toggle_confirm_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                                            'assets', 'eye_open.png')))
        else:
            self.confirm_edit.setEchoMode(QLineEdit.Password)
            self.toggle_confirm_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                                            'assets', 'eye_closed.png')))

    def register(self):
        """Xử lý đăng ký người dùng mới"""
        try:
            username = self.username_edit.text().strip()
            password = self.password_edit.text()
            confirm = self.confirm_edit.text()
            fullname = self.fullname_edit.text().strip()

            # Validate empty fields
            if not all([username, password, confirm, fullname]):
                QMessageBox.warning(self, "Thiếu thông tin", 
                                  "Vui lòng điền đầy đủ thông tin các trường bắt buộc")
                return

            # Validate username
            if len(username) < 4:
                QMessageBox.warning(self, "Tên đăng nhập không hợp lệ",
                                  "Tên đăng nhập phải có ít nhất 4 ký tự")
                return

            # Validate fullname
            if len(fullname) < 2:
                QMessageBox.warning(self, "Họ tên không hợp lệ",
                                  "Họ tên phải có ít nhất 2 ký tự")
                return

            # Validate password match
            if password != confirm:
                QMessageBox.warning(self, "Mật khẩu không khớp",
                                  "Mật khẩu và xác nhận mật khẩu phải giống nhau")
                return

            # Validate password strength
            if not UserManager.is_strong_password(password):
                QMessageBox.warning(self, "Mật khẩu yếu", 
                    "Mật khẩu cần có:\n• Ít nhất 8 ký tự\n• Chữ hoa\n• Chữ thường\n• Số\n• Ký tự đặc biệt")
                return

            try:
                user_manager = UserManager()
                result = user_manager.add_user(username=username, password=password, full_name=fullname)
                
                if result:
                    QMessageBox.information(self, "Đăng ký thành công", 
                        "Tài khoản đã được tạo thành công!\nBạn có thể đăng nhập với tài khoản vừa tạo.")
                    self.register_success.emit()
                    self.accept()
                else:
                    QMessageBox.critical(self, "Lỗi", "Không thể tạo tài khoản. Vui lòng thử lại sau.")
                    
            except ValueError as ve:
                QMessageBox.warning(self, "Lỗi", str(ve))
            except Exception as e:
                print(f"Lỗi chi tiết khi đăng ký: {str(e)}")
                QMessageBox.critical(self, "Lỗi hệ thống", 
                                   "Có lỗi xảy ra khi tạo tài khoản. Vui lòng thử lại sau.")
        except Exception as e:
            print(f"Lỗi trong quá trình xử lý đăng ký: {str(e)}")
            QMessageBox.critical(self, "Lỗi hệ thống", "Có lỗi xảy ra. Vui lòng thử lại sau.")

    def keyPressEvent(self, event):
        """Xử lý sự kiện phím tắt"""
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            self.register()  # Ctrl + Enter để đăng ký
        elif event.key() == Qt.Key_Escape:
            self.reject()  # Esc để quay lại


