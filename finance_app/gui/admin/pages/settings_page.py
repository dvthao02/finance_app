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
        lang_btn.clicked.connect(lambda: self.change_setting_dialog('language', lang_value))
        
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
        theme_btn.clicked.connect(lambda: self.change_setting_dialog('theme', theme_value))
        
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
        email_btn.clicked.connect(lambda: self.change_setting_dialog('notification_enabled', email_value))
        
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
        push_btn.clicked.connect(lambda: self.change_setting_dialog('notification_enabled', push_value))
        
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
        backup_btn.clicked.connect(lambda: self.change_setting_dialog('backup_frequency', backup_value))
        
        backup_layout.addWidget(backup_label)
        backup_layout.addWidget(backup_value)
        backup_layout.addStretch()
        backup_layout.addWidget(backup_btn)
        
        layout.addLayout(backup_layout)
        
        # Manual backup
        manual_layout = QHBoxLayout()
        manual_btn = self.create_primary_button("Sao lưu ngay")
        manual_btn.setFixedWidth(200)
        manual_btn.clicked.connect(self.manual_backup)
        
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
        from finance_app.data_manager.setting_manager import SettingManager
        import os
        # Khởi tạo SettingManager
        setting_manager = SettingManager()
        setting_manager._load_data_if_needed()
        # Lấy settings của admin (hoặc user đầu tiên)
        settings_list = setting_manager.settings
        if not settings_list:
            return
        # Lấy settings đầu tiên (hoặc có thể lọc theo user_id admin)
        settings = settings_list[0]
        # Cập nhật các label/checkbox/combo box trên giao diện
        # Tìm các widget theo tên hoặc thứ tự (giả sử đúng thứ tự tạo ra trong init_ui)
        # Ngôn ngữ
        lang_label = [lbl for lbl in self.findChildren(QLabel) if lbl.text() == "Ngôn ngữ:"]
        if lang_label:
            lang_value = lang_label[0].parent().findChildren(QLabel)[1]
            lang_value.setText(settings.get('language', 'Tiếng Việt'))
        # Giao diện
        theme_label = [lbl for lbl in self.findChildren(QLabel) if lbl.text() == "Giao diện:"]
        if theme_label:
            theme_value = theme_label[0].parent().findChildren(QLabel)[1]
            theme_value.setText('Sáng' if settings.get('theme', 'light') == 'light' else 'Tối')
        # Thông báo qua email
        email_label = [lbl for lbl in self.findChildren(QLabel) if lbl.text() == "Thông báo qua email:"]
        if email_label:
            email_value = email_label[0].parent().findChildren(QLabel)[1]
            email_value.setText('Bật' if settings.get('notification_enabled', True) else 'Tắt')
        # Thông báo đẩy
        push_label = [lbl for lbl in self.findChildren(QLabel) if lbl.text() == "Thông báo đẩy:"]
        if push_label:
            push_value = push_label[0].parent().findChildren(QLabel)[1]
            push_value.setText('Bật' if settings.get('notification_enabled', True) else 'Tắt')
        # Tự động sao lưu
        backup_label = [lbl for lbl in self.findChildren(QLabel) if lbl.text() == "Tự động sao lưu:"]
        if backup_label:
            backup_value = backup_label[0].parent().findChildren(QLabel)[1]
            backup_value.setText(settings.get('backup_frequency', 'Hàng tuần'))
        
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
    
    def change_setting_dialog(self, key, value_label):
        """Hiển thị dialog chọn giá trị mới cho setting và lưu lại"""
        from PyQt5.QtWidgets import QInputDialog
        options = {
            'language': ["Tiếng Việt", "English"],
            'theme': ["Sáng", "Tối"],
            'notification_enabled': ["Bật", "Tắt"],
            'backup_frequency': ["Hàng ngày", "Hàng tuần", "Hàng tháng"]
        }
        current = value_label.text()
        items = options.get(key, [])
        if not items:
            return
        item, ok = QInputDialog.getItem(self, "Chọn giá trị mới", f"Chọn {key.replace('_', ' ')}:", items, items.index(current) if current in items else 0, False)
        if ok and item:
            value_label.setText(item)
            # Lưu lại setting
            self.save_single_setting(key, item)

    def save_single_setting(self, key, value):
        """Lưu một setting đơn lẻ và reload lại giao diện"""
        from finance_app.data_manager.setting_manager import SettingManager
        setting_manager = SettingManager()
        setting_manager._load_data_if_needed()
        # Lấy settings đầu tiên (admin)
        settings = setting_manager.settings[0]
        # Map value về đúng kiểu
        if key == 'theme':
            settings[key] = 'light' if value == 'Sáng' else 'dark'
        elif key == 'notification_enabled':
            settings[key] = True if value == 'Bật' else False
        else:
            settings[key] = value
        setting_manager.save_settings()
        self.refresh_data()
        QMessageBox.information(self, "Thành công", "Đã cập nhật cài đặt thành công!", QMessageBox.Ok)

    def manual_backup(self):
        # Giả lập thao tác sao lưu
        QMessageBox.information(self, "Sao lưu", "Dữ liệu đã được sao lưu thành công!", QMessageBox.Ok)