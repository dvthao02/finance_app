from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from finance_app.gui.base.base_form import BaseForm
from finance_app.gui.base.base_widget import BaseWidget
from finance_app.data_manager.user_manager import UserManager
import os

class LoginForm(BaseForm, BaseWidget):
    # Signal emitted on successful login with user ID
    login_success = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_manager = UserManager()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Setup window properties with a distinct title and size for testing
        self.setup_window("Login Screen", fixed_size=(380, 580))
        
        # Create content layout with margins (no top spacing, stretchers will handle)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create login card
        login_card = self.create_card(padding=30)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(20)
        
        # Add title (internal to the card)
        title = self.create_title_label("Đăng nhập tài khoản")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #333333; margin-bottom: 30px;")
        card_layout.addWidget(title)
        
        # Username input
        username_layout = QVBoxLayout()
        username_layout.setSpacing(8)
        username_label = self.create_label("Tên đăng nhập", bold=True)
        self.username_input = self.create_input_field("Nhập tên đăng nhập")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        
        # Password input
        password_layout = QVBoxLayout()
        password_layout.setSpacing(8)
        password_label = self.create_label("Mật khẩu", bold=True)
        
        password_input_layout = QHBoxLayout()
        password_input_layout.setSpacing(10)
        self.password_input = self.create_input_field("Nhập mật khẩu", password=True)
        
        # Show/Hide password button
        self.toggle_password_btn = self.create_icon_button(self.get_asset_path('eye_closed.png'))
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        
        password_input_layout.addWidget(self.password_input)
        password_input_layout.addWidget(self.toggle_password_btn)
        
        password_layout.addWidget(password_label)
        password_layout.addLayout(password_input_layout)
        
        # Add input layouts
        card_layout.addLayout(username_layout)
        card_layout.addLayout(password_layout)
        card_layout.addSpacing(25) # Adjusted spacing before login button
        
        # Login button
        self.login_button = self.create_primary_button("Đăng nhập")
        self.login_button.clicked.connect(self.handle_login)
        
        # Register link
        self.register_button = self.create_link_button("Chưa có tài khoản? Đăng ký ngay")
        self.register_button.clicked.connect(self.show_register_form)
        
        card_layout.addWidget(self.login_button)
        card_layout.addWidget(self.register_button)
        
        login_card.setLayout(card_layout)
        
        # Add stretchers to center the login card vertically
        content_layout.addStretch(1)
        content_layout.addWidget(login_card)
        content_layout.addStretch(1)
        
        # Add content layout to main layout
        self.main_layout.addLayout(content_layout)
        
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_input.echoMode() == self.password_input.Password:
            self.password_input.setEchoMode(self.password_input.Normal)
            self.toggle_password_btn.setIcon(QIcon(self.get_asset_path('eye_open.png')))
        else:
            self.password_input.setEchoMode(self.password_input.Password)
            self.toggle_password_btn.setIcon(QIcon(self.get_asset_path('eye_closed.png')))
            
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.show_warning(
                "Thiếu thông tin",
                "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu"
            )
            return
            
        # Attempt login
        result = self.user_manager.authenticate_user(username, password)
        
        if result.get("status") == "success":
            self.login_success.emit(result["user"]["user_id"])
            self.close()
        else:
            self.show_error(
                "Đăng nhập thất bại",
                result.get("message", "Tên đăng nhập hoặc mật khẩu không đúng")
            )
            
    def show_register_form(self):
        """Show registration form"""
        from finance_app.gui.auth.register_form import RegisterForm
        register_form = RegisterForm(self.parent)
        register_form.register_success.connect(self.on_register_success)
        self.hide()
        register_form.show()
        
    def on_register_success(self, user_id):
        """Handle successful registration"""
        self.login_success.emit(user_id)
        
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.handle_login() 