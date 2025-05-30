from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt
from finance_app.gui.base.base_widget import BaseWidget

class UserSettingsPage(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        """Initialize the settings page UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Page title
        title = self.create_title_label("Cài đặt")
        layout.addWidget(title)
        
        # Settings sections
        self.create_general_settings(layout)
        self.create_notification_settings(layout)
        self.create_privacy_settings(layout)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        self.setLayout(layout)
        
    def create_general_settings(self, parent_layout):
        """Create general settings section"""
        section = self.create_settings_section("Cài đặt chung")
        layout = QVBoxLayout()
        
        # Language settings
        lang_layout = QHBoxLayout()
        lang_label = self.create_label("Ngôn ngữ:", bold=True)
        lang_value = self.create_label("Tiếng Việt")
        lang_btn = self.create_secondary_button("Thay đổi")
        
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(lang_value)
        lang_layout.addStretch()
        lang_layout.addWidget(lang_btn)
        
        layout.addLayout(lang_layout)
        
        # Theme settings
        theme_layout = QHBoxLayout()
        theme_label = self.create_label("Giao diện:", bold=True)
        theme_value = self.create_label("Sáng")
        theme_btn = self.create_secondary_button("Thay đổi")
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(theme_value)
        theme_layout.addStretch()
        theme_layout.addWidget(theme_btn)
        
        layout.addLayout(theme_layout)
        
        # Currency settings
        currency_layout = QHBoxLayout()
        currency_label = self.create_label("Đơn vị tiền tệ:", bold=True)
        currency_value = self.create_label("VND")
        currency_btn = self.create_secondary_button("Thay đổi")
        
        currency_layout.addWidget(currency_label)
        currency_layout.addWidget(currency_value)
        currency_layout.addStretch()
        currency_layout.addWidget(currency_btn)
        
        layout.addLayout(currency_layout)
        
        section.setLayout(layout)
        parent_layout.addWidget(section)
        
    def create_notification_settings(self, parent_layout):
        """Create notification settings section"""
        section = self.create_settings_section("Cài đặt thông báo")
        layout = QVBoxLayout()
        
        # Budget notifications
        budget_layout = QHBoxLayout()
        budget_label = self.create_label("Thông báo ngân sách:", bold=True)
        budget_value = self.create_label("Bật")
        budget_btn = self.create_secondary_button("Thay đổi")
        
        budget_layout.addWidget(budget_label)
        budget_layout.addWidget(budget_value)
        budget_layout.addStretch()
        budget_layout.addWidget(budget_btn)
        
        layout.addLayout(budget_layout)
        
        # Transaction notifications
        trans_layout = QHBoxLayout()
        trans_label = self.create_label("Thông báo giao dịch:", bold=True)
        trans_value = self.create_label("Bật")
        trans_btn = self.create_secondary_button("Thay đổi")
        
        trans_layout.addWidget(trans_label)
        trans_layout.addWidget(trans_value)
        trans_layout.addStretch()
        trans_layout.addWidget(trans_btn)
        
        layout.addLayout(trans_layout)
        
        # Email notifications
        email_layout = QHBoxLayout()
        email_label = self.create_label("Thông báo qua email:", bold=True)
        email_value = self.create_label("Bật")
        email_btn = self.create_secondary_button("Thay đổi")
        
        email_layout.addWidget(email_label)
        email_layout.addWidget(email_value)
        email_layout.addStretch()
        email_layout.addWidget(email_btn)
        
        layout.addLayout(email_layout)
        
        section.setLayout(layout)
        parent_layout.addWidget(section)
        
    def create_privacy_settings(self, parent_layout):
        """Create privacy settings section"""
        section = self.create_settings_section("Cài đặt bảo mật")
        layout = QVBoxLayout()
        
        # Two-factor authentication
        twofa_layout = QHBoxLayout()
        twofa_label = self.create_label("Xác thực hai lớp:", bold=True)
        twofa_value = self.create_label("Tắt")
        twofa_btn = self.create_secondary_button("Bật")
        
        twofa_layout.addWidget(twofa_label)
        twofa_layout.addWidget(twofa_value)
        twofa_layout.addStretch()
        twofa_layout.addWidget(twofa_btn)
        
        layout.addLayout(twofa_layout)
        
        # Session timeout
        session_layout = QHBoxLayout()
        session_label = self.create_label("Thời gian chờ:", bold=True)
        session_value = self.create_label("30 phút")
        session_btn = self.create_secondary_button("Thay đổi")
        
        session_layout.addWidget(session_label)
        session_layout.addWidget(session_value)
        session_layout.addStretch()
        session_layout.addWidget(session_btn)
        
        layout.addLayout(session_layout)
        
        # Data privacy
        privacy_layout = QHBoxLayout()
        privacy_label = self.create_label("Quyền riêng tư dữ liệu:", bold=True)
        privacy_value = self.create_label("Chỉ mình tôi")
        privacy_btn = self.create_secondary_button("Thay đổi")
        
        privacy_layout.addWidget(privacy_label)
        privacy_layout.addWidget(privacy_value)
        privacy_layout.addStretch()
        privacy_layout.addWidget(privacy_btn)
        
        layout.addLayout(privacy_layout)
        
        section.setLayout(layout)
        parent_layout.addWidget(section)
        
    def create_settings_section(self, title):
        """Create a settings section
        
        Args:
            title (str): Section title
        """
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Section title
        title_label = self.create_label(title, size=18, bold=True)
        layout.addWidget(title_label)
        
        section.setLayout(layout)
        return section
        
    def refresh_data(self):
        """Refresh settings data"""
        pass # Will be implemented later 