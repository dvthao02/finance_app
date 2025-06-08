from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os
import shutil

class AdminProfilePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_user = None
        self.setObjectName("admin_profile_page")
        self.init_ui()
        
    def init_ui(self):
        """Initialize the profile page UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Page title
        title = QLabel("Profile")
        title.setStyleSheet("""
            QLabel {
                color: #202124;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        layout.addWidget(title)
        
        # Profile card
        profile_card = QFrame()
        profile_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        card_layout = QVBoxLayout()
        
        # User info section
        info_layout = QHBoxLayout()
        
        # Avatar section
        avatar_layout = QVBoxLayout()
        avatar_layout.setAlignment(Qt.AlignCenter)
        
        avatar_label = QLabel()
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        avatar_path = os.path.join(project_root, 'assets', 'admin_avatar.png')
        if os.path.exists(avatar_path):
            avatar_label.setPixmap(QIcon(avatar_path).pixmap(120, 120))
        avatar_label.setStyleSheet("margin-bottom: 10px;")
        
        change_avatar_btn = QPushButton("Change Avatar")
        change_avatar_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #1a73e8;
                border-radius: 4px;
                color: #1a73e8;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #e8f0fe;
            }
        """)
        # Connect the change_avatar_btn to the change_avatar method
        change_avatar_btn.clicked.connect(self.change_avatar)
        
        avatar_layout.addWidget(avatar_label)
        avatar_layout.addWidget(change_avatar_btn)
        info_layout.addLayout(avatar_layout)
        
        # User details section
        details_layout = QVBoxLayout()
        details_layout.setSpacing(15)
        
        # Username
        username_layout = QVBoxLayout()
        username_label = QLabel("Username")
        username_label.setStyleSheet("color: #5f6368; font-size: 12px;")
        self.username_value = QLabel("")
        self.username_value.setStyleSheet("font-size: 16px; font-weight: bold;")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_value)
        
        # Full Name
        name_layout = QVBoxLayout()
        name_label = QLabel("Full Name")
        name_label.setStyleSheet("color: #5f6368; font-size: 12px;")
        self.name_edit = QLineEdit()
        self.name_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
            }
        """)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        
        # Email
        email_layout = QVBoxLayout()
        email_label = QLabel("Email")
        email_label.setStyleSheet("color: #5f6368; font-size: 12px;")
        self.email_edit = QLineEdit()
        self.email_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
            }
        """)
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_edit)
        
        # Add details to layout
        details_layout.addLayout(username_layout)
        details_layout.addLayout(name_layout)
        details_layout.addLayout(email_layout)
        
        # Save button
        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                border: none;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        save_btn.clicked.connect(self.save_changes)
        details_layout.addWidget(save_btn)
        
        info_layout.addLayout(details_layout)
        info_layout.addStretch()
        
        card_layout.addLayout(info_layout)
        profile_card.setLayout(card_layout)
        layout.addWidget(profile_card)
        
        # Security section
        security_card = QFrame()
        security_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        security_layout = QVBoxLayout()
        
        security_title = QLabel("Security")
        security_title.setStyleSheet("""
            QLabel {
                color: #202124;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        
        # Change password button
        change_pass_btn = QPushButton("Change Password")
        change_pass_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #1a73e8;
                border-radius: 4px;
                color: #1a73e8;
                font-weight: bold;
                padding: 10px 20px;
                max-width: 200px;
            }
            QPushButton:hover {
                background-color: #e8f0fe;
            }
        """)
        change_pass_btn.clicked.connect(self.show_change_password_dialog)
        
        security_layout.addWidget(security_title)
        security_layout.addWidget(change_pass_btn)
        security_card.setLayout(security_layout)
        
        layout.addWidget(security_card)
        layout.addStretch()
        self.setLayout(layout)
        
    def refresh_data(self):
        """Called by the dashboard when the current user is set or changed."""
        if self.parent and self.parent.current_user:
            self.update_user_info(self.parent.current_user)
        else:
            # Clear fields or show placeholder if no user data
            self.update_user_info(None)

    def update_user_info(self, user_data):
        """Update the profile page with user data
        
        Args:
            user_data (dict): Dictionary containing user information
        """
        self.current_user = user_data
        if user_data:
            self.username_value.setText(user_data.get('username', ''))
            self.name_edit.setText(user_data.get('full_name', ''))
            self.email_edit.setText(user_data.get('email', ''))
        else:
            # Clear fields if user_data is None
            self.username_value.setText("N/A")
            self.name_edit.setText("")
            self.email_edit.setText("")
            
    def save_changes(self):
        """Save profile changes"""
        if not self.current_user:
            return
        try:
            from finance_app.data_manager.user_manager import UserManager
            user_manager = UserManager()
            # Update user data
            success = user_manager.update_user(
                user_id=self.current_user['user_id'],
                full_name=self.name_edit.text(),
                email=self.email_edit.text()
            )
            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    "Profile updated successfully"
                )
                self.refresh_data()  # Ensure UI reloads data
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to update profile"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error updating profile: {str(e)}"
            )

    def show_change_password_dialog(self):
        """Show change password dialog"""
        if not self.current_user:
            return
        try:
            from finance_app.gui.user.change_password_dialog import ChangePasswordDialog  # Fixed import path
            # Pass username instead of user_id for compatibility
            dialog = ChangePasswordDialog(self.current_user['username'], self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error showing change password dialog: {str(e)}"
            )

    def change_avatar(self):
        """Allow admin to change avatar image"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh đại diện", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            try:
                # Save avatar path to user data (or copy to assets and update user profile)
                from finance_app.data_manager.user_manager import UserManager
                user_manager = UserManager()
                # Optionally, copy file to assets/avatar_{user_id}.png
                ext = os.path.splitext(file_path)[1]
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
                avatar_dir = os.path.join(project_root, 'assets')
                avatar_filename = f"admin_avatar_{self.current_user['user_id']}{ext}"
                avatar_dest = os.path.join(avatar_dir, avatar_filename)
                shutil.copyfile(file_path, avatar_dest)
                # Update user profile with new avatar path
                success = user_manager.update_user(
                    user_id=self.current_user['user_id'],
                    avatar=avatar_filename
                )
                if success:
                    QMessageBox.information(self, "Thành công", "Đã cập nhật ảnh đại diện.")
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Lỗi", "Không thể cập nhật ảnh đại diện.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi khi cập nhật avatar: {str(e)}")