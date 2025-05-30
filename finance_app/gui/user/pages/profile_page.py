from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget, QLabel,
                             QPushButton, QFrame, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt
from finance_app.gui.base.base_widget import BaseWidget
from finance_app.gui.components.statistics_panel import StatisticsPanel

class UserProfilePage(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        """Initialize the profile page UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Page header
        title = self.create_title_label("Hồ sơ người dùng")
        layout.addWidget(title)
        
        # Profile card
        profile_card = QFrame()
        profile_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        profile_layout = QVBoxLayout()
        
        # User info section
        info_layout = QHBoxLayout()
        
        # Avatar and basic info
        basic_info = QVBoxLayout()
        basic_info.setSpacing(10)
        
        # Username
        self.username_label = QLabel()
        self.username_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        basic_info.addWidget(self.username_label)
        
        # Full name
        self.name_label = QLabel()
        self.name_label.setStyleSheet("font-size: 16px;")
        basic_info.addWidget(self.name_label)
        
        # Email
        self.email_label = QLabel()
        self.email_label.setStyleSheet("color: #5f6368;")
        basic_info.addWidget(self.email_label)
        
        info_layout.addLayout(basic_info)
        info_layout.addStretch()
        
        # Edit profile button
        edit_btn = self.create_secondary_button("Chỉnh sửa thông tin")
        edit_btn.clicked.connect(self.edit_profile)
        info_layout.addWidget(edit_btn)
        
        profile_layout.addLayout(info_layout)
        
        # Statistics panel
        self.stats_panel = StatisticsPanel()
        profile_layout.addWidget(self.stats_panel)
        
        profile_card.setLayout(profile_layout)
        layout.addWidget(profile_card)
        
        # Change password card
        password_card = QFrame()
        password_card.setStyleSheet(profile_card.styleSheet())
        
        password_layout = QVBoxLayout()
        
        # Card title
        password_title = self.create_label("Đổi mật khẩu", bold=True, size=18)
        password_layout.addWidget(password_title)
        
        # Current password
        current_label = self.create_label("Mật khẩu hiện tại:", bold=True)
        self.current_password = self.create_input_field("Nhập mật khẩu hiện tại", password=True)
        password_layout.addWidget(current_label)
        password_layout.addWidget(self.current_password)
        
        # New password
        new_label = self.create_label("Mật khẩu mới:", bold=True)
        self.new_password = self.create_input_field("Nhập mật khẩu mới", password=True)
        password_layout.addWidget(new_label)
        password_layout.addWidget(self.new_password)
        
        # Confirm password
        confirm_label = self.create_label("Xác nhận mật khẩu mới:", bold=True)
        self.confirm_password = self.create_input_field("Nhập lại mật khẩu mới", password=True)
        password_layout.addWidget(confirm_label)
        password_layout.addWidget(self.confirm_password)
        
        # Change password button
        change_btn = self.create_primary_button("Đổi mật khẩu")
        change_btn.clicked.connect(self.change_password)
        password_layout.addWidget(change_btn)
        
        password_card.setLayout(password_layout)
        layout.addWidget(password_card)
        
        self.setLayout(layout)
        
    def refresh_data(self):
        """Called by the dashboard when the current user is set or changed."""
        if self.parent and self.parent.current_user:
            self.update_user_info(self.parent.current_user)
        else:
            self.update_user_info(None) # Clear fields

    def update_user_info(self, user_data):
        """Update user information
        
        Args:
            user_data (dict): User data dictionary
        """
        if not user_data:
            # Clear fields if user_data is None
            self.username_label.setText("N/A")
            self.name_label.setText("")
            self.email_label.setText("")
            # self.stats_panel.update_data(None) # Or clear it appropriately
            return
            
        # Update labels
        self.username_label.setText(user_data.get('username', ''))
        self.name_label.setText(user_data.get('full_name', ''))
        self.email_label.setText(user_data.get('email', ''))
        
        # Update statistics panel
        if hasattr(self.stats_panel, 'update_statistics') and callable(self.stats_panel.update_statistics):
            self.stats_panel.update_statistics({})
        
    def edit_profile(self):
        """Show dialog to edit profile"""
        from finance_app.gui.user.dialogs.profile_dialog import ProfileDialog
        
        dialog = ProfileDialog(self)
        if dialog.exec_() == QMessageBox.Accepted:
            # Refresh user data
            self.parent.refresh_data()
            
    def change_password(self):
        """Change user password"""
        current_password = self.current_password.text()
        new_password = self.new_password.text()
        confirm_password = self.confirm_password.text()
        
        # Validate input
        if not current_password:
            self.parent.show_warning(
                "Thiếu thông tin",
                "Vui lòng nhập mật khẩu hiện tại"
            )
            return
            
        if not new_password:
            self.parent.show_warning(
                "Thiếu thông tin",
                "Vui lòng nhập mật khẩu mới"
            )
            return
            
        if not confirm_password:
            self.parent.show_warning(
                "Thiếu thông tin",
                "Vui lòng xác nhận mật khẩu mới"
            )
            return
            
        if new_password != confirm_password:
            self.parent.show_warning(
                "Lỗi",
                "Mật khẩu mới không khớp"
            )
            return
            
        try:
            success = self.parent.user_manager.change_password(
                self.parent.current_user_id,
                current_password,
                new_password
            )
            
            if success:
                self.parent.show_info(
                    "Thành công",
                    "Đã đổi mật khẩu thành công"
                )
                
                # Clear input fields
                self.current_password.clear()
                self.new_password.clear()
                self.confirm_password.clear()
            else:
                self.parent.show_error(
                    "Lỗi",
                    "Mật khẩu hiện tại không đúng"
                )
                
        except Exception as e:
            self.parent.show_error(
                "Lỗi",
                f"Không thể đổi mật khẩu: {str(e)}"
            ) 