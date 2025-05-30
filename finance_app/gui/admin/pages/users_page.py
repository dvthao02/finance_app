from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView, QMenu, QDialog, QLineEdit,
                             QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from finance_app.gui.admin.user_dialogs import UserDialog, ResetPasswordDialog
from finance_app.gui.admin.dialogs.user_details_dialog import UserDetailsDialog
import os
from finance_app.gui.base.base_widget import BaseWidget

class AdminUsersPage(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.user_manager = parent.user_manager if parent else None
        self.total_users_label = None
        self.active_users_label = None
        self.locked_users_label = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the users page UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Page header
        header_layout = QHBoxLayout()
        
        # Title
        title = self.create_title_label("Quản lý người dùng")
        header_layout.addWidget(title)
        
        # Add User button
        add_btn = self.create_primary_button("Thêm người dùng")
        add_btn.clicked.connect(self.add_user)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Statistics cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Total Users
        total_users_card, self.total_users_label = self.create_stat_card_with_label_ref(
            "Total Users",
            "0",
            "users_icon.png",
            "#1a73e8"
        )
        stats_layout.addWidget(total_users_card)
        
        # Active Users
        active_users_card, self.active_users_label = self.create_stat_card_with_label_ref(
            "Active Users",
            "0",
            "active_users_icon.png",
            "#34a853"
        )
        stats_layout.addWidget(active_users_card)
        
        # Locked Users
        locked_users_card, self.locked_users_label = self.create_stat_card_with_label_ref(
            "Locked Users",
            "0",
            "locked_users_icon.png",
            "#ea4335"
        )
        stats_layout.addWidget(locked_users_card)
        
        layout.addLayout(stats_layout)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels([
            "Tên đăng nhập", "Họ tên", "Email",
            "Loại tài khoản", "Trạng thái", "Thao tác"
        ])
        
        # Set column widths
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.setColumnWidth(0, 150)  # Username
        self.users_table.setColumnWidth(1, 200)  # Full name
        self.users_table.setColumnWidth(2, 200)  # Email
        self.users_table.setColumnWidth(3, 100)  # Role
        self.users_table.setColumnWidth(4, 100)  # Status
        
        self.users_table.horizontalHeader().setVisible(True)

        # Style the table
        self.users_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                font-weight: bold;
                color: #333;
            }
        """)
        
        layout.addWidget(self.users_table)
        self.setLayout(layout)
        
        # Load users - This will be called by refresh_data after user context is set
        # self.load_users() 
    
    def create_stat_card_with_label_ref(self, title, value, icon_name, color):
        """Create a statistics card and return the card and its value QLabel.
        
        Args:
            title (str): Card title
            value (str): Statistic value
            icon_name (str): Icon file name
            color (str): Accent color
        
        Returns:
            tuple: (QFrame, QLabel) The card frame and the value label
        """
        card = QFrame()
        card.setObjectName(f"stat_card_{title.replace(' ', '_').lower()}")
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        # Icon
        icon_label = QLabel()
        # Construct path relative to this file's location to assets directory
        # finance_app/gui/admin/pages/users_page.py -> project_root/assets
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        icon_path = os.path.join(project_root, 'assets', icon_name)

        if os.path.exists(icon_path):
            icon_label.setPixmap(QIcon(icon_path).pixmap(32, 32))
        else:
            print(f"Warning: Icon not found at {icon_path}")
            icon_label.setText("?")

        layout.addWidget(icon_label)
        
        # Text
        text_layout = QVBoxLayout()
        
        value_label = QLabel(value)
        value_label.setObjectName(f"value_label_{title.replace(' ', '_').lower()}")
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        
        title_label = QLabel(title)
        title_label.setObjectName(f"title_label_{title.replace(' ', '_').lower()}")
        title_label.setStyleSheet("""
            QLabel {
                color: #5f6368;
                font-size: 14px;
            }
        """)
        
        text_layout.addWidget(value_label)
        text_layout.addWidget(title_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        card.setLayout(layout)
        return card, value_label

    def create_stat_card(self, title, value, icon_name, color):
        card, _ = self.create_stat_card_with_label_ref(title, value, icon_name, color)
        return card
    
    def load_users(self):
        """Load users into the table"""
        try:
            # Fetch all users, including inactive/locked ones for admin view
            users = self.parent.user_manager.get_all_users(active_only=False)
            # Nếu cần lọc theo user_id, có thể truyền user_id=self.parent.current_user_id
            
            # Update statistics
            total_users = len(users)
            active_users = len([u for u in users if u.get('is_active', True)])
            locked_users = total_users - active_users
            
            # Update stat cards
            if self.total_users_label:
                self.total_users_label.setText(str(total_users))
            if self.active_users_label:
                self.active_users_label.setText(str(active_users))
            if self.locked_users_label:
                self.locked_users_label.setText(str(locked_users))
            
            # Clear table
            self.users_table.setRowCount(0)
            
            # Add users to table
            for user in users:
                row = self.users_table.rowCount()
                self.users_table.insertRow(row)
                
                # Column indices shift due to ID removal
                self.users_table.setItem(row, 0, QTableWidgetItem(user.get('username', '')))
                self.users_table.setItem(row, 1, QTableWidgetItem(user.get('full_name', '')))
                self.users_table.setItem(row, 2, QTableWidgetItem(user.get('email', '')))
                
                # Role
                role = "Admin" if user.get('is_admin') else "User"
                role_item = QTableWidgetItem(role)
                role_item.setTextAlignment(Qt.AlignCenter)
                self.users_table.setItem(row, 3, role_item)
                
                # Status
                status = "Hoạt động" if user.get('is_active', True) else "Đã khóa"
                status_item = QTableWidgetItem(status)
                status_item.setTextAlignment(Qt.AlignCenter)
                if user.get('is_active', True):
                    status_item.setForeground(Qt.darkGreen)
                else:
                    status_item.setForeground(Qt.red)
                self.users_table.setItem(row, 4, status_item)
                
                # Actions button
                actions_btn = QPushButton("...")
                actions_btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        padding: 5px 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #f1f3f4;
                        border-radius: 4px;
                    }
                """)
                
                # Create actions menu
                menu = QMenu()
                
                # View details action
                view_action = menu.addAction("Xem chi tiết")
                view_action.triggered.connect(lambda checked, u=user: self.view_user_details(u))
                
                # Edit action
                edit_action = menu.addAction("Chỉnh sửa")
                edit_action.triggered.connect(lambda checked, u=user: self.edit_user(u))
                
                # Reset password action
                reset_action = menu.addAction("Đặt lại mật khẩu")
                reset_action.triggered.connect(lambda checked, u=user: self.reset_password(u))
                
                # Lock/Unlock action
                if user.get('is_active', True):
                    lock_action = menu.addAction("Khóa")
                    lock_action.triggered.connect(lambda checked, u=user: self.toggle_lock(u, True))
                else:
                    unlock_action = menu.addAction("Mở khóa")
                    unlock_action.triggered.connect(lambda checked, u=user: self.toggle_lock(u, False))
                
                # Delete action
                menu.addSeparator()
                delete_action = menu.addAction("Xóa")
                delete_action.triggered.connect(lambda checked, u=user: self.delete_user(u))
                
                # Set menu for button
                actions_btn.setMenu(menu)
                
                # Add button to table
                self.users_table.setCellWidget(row, 5, actions_btn)
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể tải danh sách người dùng: {str(e)}",
                QMessageBox.Ok
            )
    
    def add_user(self):
        """Show dialog to add new user"""
        dialog = UserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()
    
    def edit_user(self, user_data):
        """Show dialog to edit user
        
        Args:
            user_data (dict): User data dictionary
        """
        dialog = UserDialog(self, user_data)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()
    
    def view_user_details(self, user_data):
        """Show user details dialog
        
        Args:
            user_data (dict): User data dictionary
        """
        dialog = UserDetailsDialog(self, user_data)
        dialog.exec_()
    
    def toggle_user_status(self, user_data):
        """Toggle user active status
        
        Args:
            user_data (dict): User data dictionary
        """
        user_id = user_data.get('user_id')
        is_active = user_data.get('is_active', True)
        
        if not user_id:
            return
            
        action = "khóa" if is_active else "mở khóa"
        if self.parent.show_question(
            f"{action.capitalize()} tài khoản",
            f"Bạn có chắc chắn muốn {action} tài khoản này?"
        ):
            try:
                success = self.parent.user_manager.update_user(
                    user_id=user_id,
                    is_active=not is_active
                )
                
                if success:
                    self.parent.show_info(
                        "Thành công",
                        f"Đã {action} tài khoản thành công"
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An error occurred: {str(e)}",
                    QMessageBox.Ok
                )
    
    def reset_password(self, user):
        """Show dialog to reset user password
        
        Args:
            user (dict): User data
        """
        dialog = ResetPasswordDialog(parent=self, user_id=user['user_id'])
        if dialog.exec_() == QDialog.Accepted:
            pass # self.load_users() # Could be called if dialog doesn't do it
    
    def toggle_lock(self, user, lock):
        """Toggle user lock status
        
        Args:
            user (dict): User data
            lock (bool): Whether to lock or unlock
        """
        try:
            result = self.parent.user_manager.toggle_user_lock(
                user['user_id'],
                lock
            )
            
            if result:
                action = "locked" if lock else "unlocked"
                QMessageBox.information(
                    self,
                    "Success",
                    f"User {user['username']} has been {action}.",
                    QMessageBox.Ok
                )
                self.load_users()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to {'lock' if lock else 'unlock'} user. Please try again.",
                    QMessageBox.Ok
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred: {str(e)}",
                QMessageBox.Ok
            )
    
    def delete_user(self, user):
        """Delete user after confirmation
        
        Args:
            user (dict): User data
        """
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete user {user['username']}?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = self.parent.user_manager.delete_user(user['user_id'])
                
                if result:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"User {user['username']} has been deleted.",
                        QMessageBox.Ok
                    )
                    self.load_users()
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to delete user. Please try again.",
                        QMessageBox.Ok
                    )
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An error occurred: {str(e)}",
                    QMessageBox.Ok
                )
    
    def refresh_data(self):
        """Refresh user data, called when dashboard user context is set or updated."""
        if not self.parent or not self.parent.user_manager:
            # Or log an error, or show a message in the UI
            print("AdminUsersPage: Cannot refresh data, parent or user_manager not available.")
            return
        self.load_users()

    # Utility methods to delegate to parent (Dashboard) for showing messages
    def show_error(self, title, message):
        if self.parent and hasattr(self.parent, 'show_error'):
            self.parent.show_error(title, message)
        else:
            QMessageBox.critical(self, title, message)

    def show_info(self, title, message):
        if self.parent and hasattr(self.parent, 'show_info'):
            self.parent.show_info(title, message)
        else:
            QMessageBox.information(self, title, message)

    def show_warning(self, title, message):
        if self.parent and hasattr(self.parent, 'show_warning'):
            self.parent.show_warning(title, message)
        else:
            QMessageBox.warning(self, title, message)

    def show_question(self, title, message):
        if self.parent and hasattr(self.parent, 'show_question'):
            return self.parent.show_question(title, message)
        return QMessageBox.question(self, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No) 