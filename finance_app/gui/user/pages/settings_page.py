from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt
from finance_app.gui.base.base_widget import BaseWidget
import logging # Add this import

logger = logging.getLogger(__name__) # Add logger instance

class UserSettingsPage(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        # Assuming you have a setting_manager instance, e.g., passed from parent or globally accessible
        # For now, let's assume it's accessible via self.parent.setting_manager
        # You might need to adjust this based on your actual application structure
        self.setting_manager = getattr(self.parent, 'setting_manager', None) 
        if not self.setting_manager:
            logger.error("SettingManager not found in UserSettingsPage parent.")
            # Handle this error appropriately, maybe show a message to the user
        self.init_ui()
        self.refresh_data() # Load initial data
        logger.info("UserSettingsPage initialized")
        
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
        self.lang_value = self.create_label("Tiếng Việt") # Assign to self
        self.lang_btn = self.create_secondary_button("Thay đổi") # Assign to self
        
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_value)
        lang_layout.addStretch()
        lang_layout.addWidget(self.lang_btn)
        
        layout.addLayout(lang_layout)
        
        # Theme settings
        theme_layout = QHBoxLayout()
        theme_label = self.create_label("Giao diện:", bold=True)
        self.theme_value = self.create_label("Sáng") # Assign to self
        self.theme_btn = self.create_secondary_button("Thay đổi") # Assign to self
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_value)
        theme_layout.addStretch()
        theme_layout.addWidget(self.theme_btn)
        
        layout.addLayout(theme_layout)
        
        # Currency settings
        currency_layout = QHBoxLayout()
        currency_label = self.create_label("Đơn vị tiền tệ:", bold=True)
        self.currency_value = self.create_label("VND") # Assign to self
        self.currency_btn = self.create_secondary_button("Thay đổi") # Assign to self
        
        currency_layout.addWidget(currency_label)
        currency_layout.addWidget(self.currency_value)
        currency_layout.addStretch()
        currency_layout.addWidget(self.currency_btn)
        
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
        self.budget_value = self.create_label("Bật") # Assign to self
        self.budget_btn = self.create_secondary_button("Thay đổi") # Assign to self
        
        budget_layout.addWidget(budget_label)
        budget_layout.addWidget(self.budget_value)
        budget_layout.addStretch()
        budget_layout.addWidget(self.budget_btn)
        
        layout.addLayout(budget_layout)
        
        # Transaction notifications
        trans_layout = QHBoxLayout()
        trans_label = self.create_label("Thông báo giao dịch:", bold=True)
        self.trans_value = self.create_label("Bật") # Assign to self
        self.trans_btn = self.create_secondary_button("Thay đổi") # Assign to self
        
        trans_layout.addWidget(trans_label)
        trans_layout.addWidget(self.trans_value)
        trans_layout.addStretch()
        trans_layout.addWidget(self.trans_btn)
        
        layout.addLayout(trans_layout)
        
        # Email notifications
        email_layout = QHBoxLayout()
        email_label = self.create_label("Thông báo qua email:", bold=True)
        self.email_value = self.create_label("Bật") # Assign to self
        self.email_btn = self.create_secondary_button("Thay đổi") # Assign to self
        
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_value)
        email_layout.addStretch()
        email_layout.addWidget(self.email_btn)
        
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
        self.twofa_value = self.create_label("Tắt") # Assign to self
        self.twofa_btn = self.create_secondary_button("Bật") # Assign to self
        
        twofa_layout.addWidget(twofa_label)
        twofa_layout.addWidget(self.twofa_value)
        twofa_layout.addStretch()
        twofa_layout.addWidget(self.twofa_btn)
        
        layout.addLayout(twofa_layout)
        
        # Session timeout
        session_layout = QHBoxLayout()
        session_label = self.create_label("Thời gian chờ:", bold=True)
        self.session_value = self.create_label("30 phút") # Assign to self
        self.session_btn = self.create_secondary_button("Thay đổi") # Assign to self
        
        session_layout.addWidget(session_label)
        session_layout.addWidget(self.session_value)
        session_layout.addStretch()
        session_layout.addWidget(self.session_btn)
        
        layout.addLayout(session_layout)
        
        # Data privacy
        privacy_layout = QHBoxLayout()
        privacy_label = self.create_label("Quyền riêng tư dữ liệu:", bold=True)
        self.privacy_value = self.create_label("Chỉ mình tôi") # Assign to self
        self.privacy_btn = self.create_secondary_button("Thay đổi") # Assign to self
        
        privacy_layout.addWidget(privacy_label)
        privacy_layout.addWidget(self.privacy_value)
        privacy_layout.addStretch()
        privacy_layout.addWidget(self.privacy_btn)
        
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
        logger.debug("Refreshing user settings data")
        if not self.setting_manager:
            logger.warning("Cannot refresh settings: SettingManager is not available.")
            return

        try:
            # Example: Load settings. This depends on how your SettingManager is structured
            # and what settings are relevant to this page.
            user_id = getattr(self.parent, 'user_id', None)
            if not user_id:
                logger.warning("User ID not found in parent, cannot load user-specific settings.")
                # Fallback to general settings or defaults if applicable
            
            # Language
            lang_setting = self.setting_manager.get_setting('language', user_id=user_id, default='Tiếng Việt')
            self.lang_value.setText(lang_setting)

            # Theme
            theme_setting = self.setting_manager.get_setting('theme', user_id=user_id, default='Sáng')
            self.theme_value.setText(theme_setting)

            # Currency
            currency_setting = self.setting_manager.get_setting('currency', user_id=user_id, default='VND')
            self.currency_value.setText(currency_setting)

            # Notification settings
            budget_notifications = self.setting_manager.get_setting('budget_notifications', user_id=user_id, default=True)
            self.budget_value.setText("Bật" if budget_notifications else "Tắt")

            transaction_notifications = self.setting_manager.get_setting('transaction_notifications', user_id=user_id, default=True)
            self.trans_value.setText("Bật" if transaction_notifications else "Tắt")

            email_notifications = self.setting_manager.get_setting('email_notifications', user_id=user_id, default=True)
            self.email_value.setText("Bật" if email_notifications else "Tắt")
            
            # Privacy settings
            two_fa_enabled = self.setting_manager.get_setting('two_factor_authentication', user_id=user_id, default=False)
            self.twofa_value.setText("Bật" if two_fa_enabled else "Tắt")
            self.twofa_btn.setText("Tắt" if two_fa_enabled else "Bật") # Button text might change based on state

            session_timeout = self.setting_manager.get_setting('session_timeout', user_id=user_id, default='30 phút')
            self.session_value.setText(session_timeout)

            data_privacy = self.setting_manager.get_setting('data_privacy', user_id=user_id, default='Chỉ mình tôi')
            self.privacy_value.setText(data_privacy)
            
            logger.info("User settings data refreshed successfully.")

        except Exception as e:
            logger.error(f"Error refreshing settings data: {e}", exc_info=True)
        # pass # Remove pass as we have content now