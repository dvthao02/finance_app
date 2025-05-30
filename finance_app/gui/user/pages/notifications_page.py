import os
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QScrollArea, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from finance_app.gui.base.base_widget import BaseWidget

class NotificationCard(QFrame):
    def __init__(self, notification, parent=None):
        super().__init__(parent)
        self.notification = notification
        self.init_ui()
        
    def init_ui(self):
        """Initialize the notification card UI"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {'#f8f9fa' if self.notification.get('is_read', False) else 'white'};
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Title and time
        header_layout = QHBoxLayout()
        
        title = QLabel(self.notification.get('title', ''))
        title.setStyleSheet("""
            QLabel {
                color: #202124;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        time = QLabel(self.notification.get('created_at', ''))
        time.setStyleSheet("color: #5f6368; font-size: 12px;")
        time.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(time)
        
        # Message
        message = QLabel(self.notification.get('message', ''))
        message.setWordWrap(True)
        message.setStyleSheet("color: #5f6368; font-size: 14px;")
        
        # Add widgets to layout
        layout.addLayout(header_layout)
        layout.addWidget(message)
        
        self.setLayout(layout)

class NotificationsPage(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.total_notifications_label = None
        self.unread_notifications_label = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the notifications page UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Page header
        header_layout = QHBoxLayout()
        
        # Title
        title = self.create_title_label("Thông báo")
        header_layout.addWidget(title)
        
        # Mark all as read button
        mark_all_btn = self.create_secondary_button("Đánh dấu tất cả đã đọc")
        mark_all_btn.clicked.connect(self.mark_all_as_read)
        header_layout.addWidget(mark_all_btn)
        
        layout.addLayout(header_layout)
        
        # Statistics cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Total notifications
        total_notifications_card, self.total_notifications_label = self.create_stat_card_with_label_ref(
            "Tổng thông báo",
            "0",
            "notifications_icon.png",
            "#1a73e8"
        )
        stats_layout.addWidget(total_notifications_card)
        
        # Unread notifications
        unread_notifications_card, self.unread_notifications_label = self.create_stat_card_with_label_ref(
            "Chưa đọc",
            "0",
            "unread_icon.png",
            "#ea4335"
        )
        stats_layout.addWidget(unread_notifications_card)
        
        layout.addLayout(stats_layout)
        
        # Notifications list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.notifications_container = QWidget()
        self.notifications_layout = QVBoxLayout()
        self.notifications_layout.setSpacing(10)
        self.notifications_container.setLayout(self.notifications_layout)
        
        scroll_area.setWidget(self.notifications_container)
        layout.addWidget(scroll_area)
        
        self.setLayout(layout)
        
        # Load notifications - This will be called by refresh_data after user context is set
        # self.load_notifications()
        
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
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
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
        
    def load_notifications(self):
        """Load notifications"""
        try:
            notifications = self.parent.notification_manager.get_user_notifications(
                self.parent.current_user_id
            )
            
            # Update statistics
            total_notifications = len(notifications)
            unread_notifications = len([n for n in notifications if not n.get('is_read', False)])
            
            # Update stat cards
            if self.total_notifications_label:
                self.total_notifications_label.setText(str(total_notifications))
            if self.unread_notifications_label:
                self.unread_notifications_label.setText(str(unread_notifications))
            
            # Clear notifications container
            for i in reversed(range(self.notifications_layout.count())):
                widget = self.notifications_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            
            # Add notifications
            for notification in notifications:
                card = NotificationCard(notification, self)
                self.notifications_layout.addWidget(card)
            
            # Add stretch to push notifications to the top
            self.notifications_layout.addStretch()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể tải thông báo: {str(e)}",
                QMessageBox.Ok
            )
            
    def mark_all_as_read(self):
        """Mark all notifications as read"""
        try:
            self.parent.notification_manager.mark_all_as_read(
                self.parent.current_user_id
            )
            self.load_notifications()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể đánh dấu thông báo đã đọc: {str(e)}",
                QMessageBox.Ok
            )
            
    def refresh_data(self):
        """Refresh notification data, called when dashboard user context is set or updated."""
        if not self.parent or not self.parent.notification_manager:
            print("NotificationsPage: Cannot refresh data, parent or notification_manager not available.")
            return
        self.load_notifications() 