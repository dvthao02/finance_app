from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea,
                           QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from datetime import datetime

class NotificationPanel(QScrollArea):
    notification_clicked = pyqtSignal(dict)  # Signal emitted when a notification is clicked
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the notification panel UI"""
        # Make the scroll area look good
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("""
            QScrollArea {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 4px;
            }
        """)
        
        # Create main widget and layout
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add title
        title = QLabel("Thông báo")
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 16px;
                font-weight: bold;
                padding: 5px 0;
            }
        """)
        self.main_layout.addWidget(title)
        
        # Container for notifications
        self.notifications_container = QWidget()
        self.notifications_layout = QVBoxLayout(self.notifications_container)
        self.notifications_layout.setSpacing(8)
        self.notifications_layout.setAlignment(Qt.AlignTop)
        
        # Add empty state label
        self.empty_label = QLabel("Không có thông báo mới")
        self.empty_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
                padding: 20px;
            }
        """)
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.notifications_layout.addWidget(self.empty_label)
        
        self.main_layout.addWidget(self.notifications_container)
        self.setWidget(self.main_widget)
        
    def create_notification_widget(self, notification):
        """Create a widget for a single notification"""
        widget = QWidget()
        widget.setObjectName("notification")
        
        # Set different styles based on notification type
        if notification.get('type') == 'warning':
            color = "#e74c3c"  # Red for warnings
        elif notification.get('type') == 'info':
            color = "#3498db"  # Blue for info
        else:
            color = "#2ecc71"  # Green for success
            
        widget.setStyleSheet(f"""
            QWidget#notification {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 4px;
                padding: 10px;
            }}
            QWidget#notification:hover {{
                background-color: #f8f9fa;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # Title and close button row
        header_layout = QHBoxLayout()
        
        title = QLabel(notification.get('title', ''))
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        header_layout.addWidget(title)
        
        # Add close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #7f8c8d;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #e74c3c;
            }
        """)
        close_btn.clicked.connect(lambda: self.remove_notification(widget))
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # Message
        message = QLabel(notification.get('message', ''))
        message.setWordWrap(True)
        message.setStyleSheet("""
            QLabel {
                color: #34495e;
                font-size: 13px;
            }
        """)
        layout.addWidget(message)
        
        # Timestamp
        timestamp = QLabel(self.format_timestamp(notification.get('created_at', '')))
        timestamp.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 12px;
            }
        """)
        layout.addWidget(timestamp)
        
        widget.setLayout(layout)
        
        # Store notification data
        widget.notification_data = notification
        
        # Make widget clickable
        widget.mousePressEvent = lambda e: self.notification_clicked.emit(notification)
        
        return widget
        
    def update_notifications(self, notifications):
        """Update the panel with new notifications"""
        # Clear existing notifications
        while self.notifications_layout.count() > 0:
            item = self.notifications_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not notifications:
            self.notifications_layout.addWidget(self.empty_label)
            return
            
        self.empty_label.setParent(None)  # Remove empty state label
        
        # Add new notifications
        for notification in sorted(notifications, 
                                key=lambda x: datetime.strptime(x['created_at'], '%Y-%m-%d %H:%M:%S'),
                                reverse=True):
            widget = self.create_notification_widget(notification)
            self.notifications_layout.addWidget(widget)
            
    def remove_notification(self, widget):
        """Remove a notification widget"""
        widget.setParent(None)
        widget.deleteLater()
        
        # Show empty state if no notifications left
        if self.notifications_layout.count() == 0:
            self.notifications_layout.addWidget(self.empty_label)
            
    def add_notification(self, notification):
        """Add a single notification to the panel"""
        # Remove empty state label if it exists
        if self.empty_label.parent():
            self.empty_label.setParent(None)
            
        # Create and add notification widget
        widget = self.create_notification_widget(notification)
        self.notifications_layout.insertWidget(0, widget)  # Add at the top
        
    @staticmethod
    def format_timestamp(timestamp_str):
        """Format timestamp for display"""
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            delta = now - timestamp
            
            if delta.days == 0:
                if delta.seconds < 60:
                    return "Vừa xong"
                elif delta.seconds < 3600:
                    minutes = delta.seconds // 60
                    return f"{minutes} phút trước"
                else:
                    hours = delta.seconds // 3600
                    return f"{hours} giờ trước"
            elif delta.days == 1:
                return "Hôm qua"
            elif delta.days < 7:
                return f"{delta.days} ngày trước"
            else:
                return timestamp.strftime('%d/%m/%Y')
        except:
            return timestamp_str  # Return original if parsing fails
