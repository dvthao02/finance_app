from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal

class NotificationPanel(QWidget):
    notification_clicked = pyqtSignal(str)  # Signal emitted when notification is clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
    def add_notification(self, notification):
        """Add a new notification to the panel
        Args:
            notification: Dictionary containing notification data
        """
        notif_widget = QLabel(notification['message'])
        notif_widget.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border-radius: 5px;
                padding: 10px;
                margin: 5px;
            }
            QLabel:hover {
                background-color: #e0e0e0;
            }
        """)
        notif_widget.mousePressEvent = lambda e: self.notification_clicked.emit(notification['id'])
        
        self.layout.addWidget(notif_widget)
        
    def clear_notifications(self):
        """Clear all notifications from the panel"""
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)
