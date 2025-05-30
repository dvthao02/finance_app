from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QCheckBox, QSpinBox, QComboBox,
                             QMessageBox)
from PyQt5.QtCore import Qt
from finance_app.gui.base.base_widget import BaseWidget

class AdminSettingsPage(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        """Initialize the settings page UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Page title
        title = self.create_title_label("Cài đặt hệ thống")
        layout.addWidget(title)
        
        # Settings sections
        self.create_general_settings(layout)
        self.create_notification_settings(layout)
        self.create_backup_settings(layout)
        
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
        
        section.setLayout(layout)
        parent_layout.addWidget(section)
        
    def create_notification_settings(self, parent_layout):
        """Create notification settings section"""
        section = self.create_settings_section("Cài đặt thông báo")
        layout = QVBoxLayout()
        
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
        
        # Push notifications
        push_layout = QHBoxLayout()
        push_label = self.create_label("Thông báo đẩy:", bold=True)
        push_value = self.create_label("Bật")
        push_btn = self.create_secondary_button("Thay đổi")
        
        push_layout.addWidget(push_label)
        push_layout.addWidget(push_value)
        push_layout.addStretch()
        push_layout.addWidget(push_btn)
        
        layout.addLayout(push_layout)
        
        section.setLayout(layout)
        parent_layout.addWidget(section)
        
    def create_backup_settings(self, parent_layout):
        """Create backup settings section"""
        section = self.create_settings_section("Sao lưu và phục hồi")
        layout = QVBoxLayout()
        
        # Auto backup
        backup_layout = QHBoxLayout()
        backup_label = self.create_label("Tự động sao lưu:", bold=True)
        backup_value = self.create_label("Hàng tuần")
        backup_btn = self.create_secondary_button("Thay đổi")
        
        backup_layout.addWidget(backup_label)
        backup_layout.addWidget(backup_value)
        backup_layout.addStretch()
        backup_layout.addWidget(backup_btn)
        
        layout.addLayout(backup_layout)
        
        # Manual backup
        manual_layout = QHBoxLayout()
        manual_btn = self.create_primary_button("Sao lưu ngay")
        manual_btn.setFixedWidth(200)
        
        manual_layout.addWidget(manual_btn)
        manual_layout.addStretch()
        
        layout.addLayout(manual_layout)
        
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

    def create_section(self, title, settings):
        """Create a settings section
        
        Args:
            title (str): Section title
            settings (list): List of setting configurations
        
        Returns:
            QFrame: The section frame
        """
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #202124;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Settings
        for setting in settings:
            setting_layout = QHBoxLayout()
            
            # Label
            label = QLabel(setting['label'])
            label.setStyleSheet("""
                QLabel {
                    color: #5f6368;
                    font-size: 14px;
                }
            """)
            setting_layout.addWidget(label)
            
            # Control
            if setting['type'] == 'checkbox':
                control = QCheckBox()
                control.setChecked(setting['default'])
            elif setting['type'] == 'spinbox':
                control = QSpinBox()
                control.setMinimum(setting['min'])
                control.setMaximum(setting['max'])
                control.setValue(setting['default'])
                control.setStyleSheet("""
                    QSpinBox {
                        border: 1px solid #e0e0e0;
                        border-radius: 4px;
                        padding: 5px;
                        min-width: 80px;
                    }
                """)
            elif setting['type'] == 'combobox':
                control = QComboBox()
                control.addItems(setting['options'])
                control.setCurrentText(setting['default'])
                control.setStyleSheet("""
                    QComboBox {
                        border: 1px solid #e0e0e0;
                        border-radius: 4px;
                        padding: 5px;
                        min-width: 120px;
                    }
                """)
            
            control.setProperty('setting_key', setting['key'])
            setting_layout.addWidget(control)
            setting_layout.addStretch()
            
            layout.addLayout(setting_layout)
        
        section.setLayout(layout)
        return section
    
    def load_settings(self):
        """Load current settings"""
        try:
            settings = self.parent.setting_manager.get_system_settings()
            
            # Update controls with saved values
            for section in [self.findChild(QFrame) for _ in range(3)]:
                if section:
                    for control in section.findChildren((QCheckBox, QSpinBox, QComboBox)):
                        key = control.property('setting_key')
                        if key in settings:
                            if isinstance(control, QCheckBox):
                                control.setChecked(settings[key])
                            elif isinstance(control, QSpinBox):
                                control.setValue(settings[key])
                            elif isinstance(control, QComboBox):
                                control.setCurrentText(settings[key])
        except Exception as e:
            print(f"Error loading settings: {str(e)}")
    
    def save_settings(self):
        """Save settings"""
        try:
            settings = {}
            
            # Collect values from all controls
            for section in [self.findChild(QFrame) for _ in range(3)]:
                if section:
                    for control in section.findChildren((QCheckBox, QSpinBox, QComboBox)):
                        key = control.property('setting_key')
                        if isinstance(control, QCheckBox):
                            settings[key] = control.isChecked()
                        elif isinstance(control, QSpinBox):
                            settings[key] = control.value()
                        elif isinstance(control, QComboBox):
                            settings[key] = control.currentText()
            
            # Save settings
            result = self.parent.setting_manager.save_system_settings(settings)
            
            if result:
                QMessageBox.information(
                    self,
                    "Success",
                    "Settings saved successfully!",
                    QMessageBox.Ok
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to save settings. Please try again.",
                    QMessageBox.Ok
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred: {str(e)}",
                QMessageBox.Ok
            ) 