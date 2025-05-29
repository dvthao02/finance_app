from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from finance_app.data_manager.user_manager import UserManager
import os

class LoginForm(QWidget):
    login_success = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_manager = UserManager()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Set window fixed size
        self.setFixedSize(400, 500)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)  # Add margins around the entire form
        self.setLayout(main_layout)
        
        # Remove logo section
        
        # Login form container
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.StyledPanel)
        form_frame.setMinimumWidth(350)
        form_frame.setMaximumWidth(450)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)  # Increase spacing between elements
        form_layout.setContentsMargins(20, 25, 20, 25)  # Add internal padding
        
        # Title
        title_label = QLabel("ĐĂNG NHẬP")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 26px;
                font-weight: bold;
                margin-bottom: 25px;
            }
        """)
        form_layout.addWidget(title_label)
        form_layout.addSpacing(10)  # Add space after title
        
        # Username input
        username_layout = QVBoxLayout()
        username_layout.setSpacing(8)  # Space between label and input
        username_label = QLabel("Tên đăng nhập:")
        username_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.username_input = QLineEdit()
        self.username_input.setMinimumHeight(40)  # Increase input height
        self.username_input.setPlaceholderText("Nhập tên đăng nhập")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        
        # Password input
        password_layout = QVBoxLayout()
        password_layout.setSpacing(8)  # Space between label and input
        password_label = QLabel("Mật khẩu:")
        password_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        password_input_layout = QHBoxLayout()
        password_input_layout.setSpacing(10)  # Space between password input and eye button
        self.password_input = QLineEdit()
        self.password_input.setMinimumHeight(40)  # Increase input height
        self.password_input.setPlaceholderText("Nhập mật khẩu")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        
        # Show/Hide password button
        self.toggle_password_btn = QPushButton()
        self.toggle_password_btn.setFixedSize(40, 40)  # Make the button square
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
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        
        password_input_layout.addWidget(self.password_input)
        password_input_layout.addWidget(self.toggle_password_btn)
        
        password_layout.addWidget(password_label)
        password_layout.addLayout(password_input_layout)
        
        # Login button
        self.login_button = QPushButton("Đăng nhập")
        self.login_button.setMinimumHeight(45)  # Increase button height
        self.login_button.setStyleSheet("""
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
        self.login_button.clicked.connect(self.handle_login)
        
        # Register link
        self.register_button = QPushButton("Đăng ký tài khoản mới")
        self.register_button.setStyleSheet("""
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
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.register_button.clicked.connect(self.show_register_form)
        
        # Add spacing between elements
        form_layout.addLayout(username_layout)
        form_layout.addSpacing(10)
        form_layout.addLayout(password_layout)
        form_layout.addSpacing(20)
        form_layout.addWidget(self.login_button)
        form_layout.addSpacing(10)
        form_layout.addWidget(self.register_button)
        
        form_frame.setLayout(form_layout)
        
        # Center the form
        main_layout.addStretch()
        main_layout.addWidget(form_frame, alignment=Qt.AlignCenter)
        main_layout.addStretch()

    # Rest of the methods remain the same
    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                                              'assets', 'eye_open.png')))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                                              'assets', 'eye_closed.png')))
            
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đầy đủ thông tin đăng nhập")
            return
            
        result = self.user_manager.authenticate_user(username, password)
        
        if result["status"] == "success":
            main_window = self.window()
            main_window.on_login_success(result["user"]["user_id"])
        elif result["status"] == "locked":
            QMessageBox.warning(self, "Cảnh báo", result["message"])
        else:
            QMessageBox.critical(self, "Lỗi", result["message"])
            
    def show_register_form(self):
        from finance_app.gui.frmRegister import RegisterForm
        frmRegister = RegisterForm(self)
        if frmRegister.exec_() == RegisterForm.Accepted:
            self.username_input.clear()
            self.password_input.clear()
            self.username_input.setFocus()

    #xử lý key press cho form đăng nhập
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.handle_login()
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
    

