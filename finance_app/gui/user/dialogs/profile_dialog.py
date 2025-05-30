from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout
from finance_app.gui.base.base_widget import BaseWidget

class ProfileDialog(QDialog, BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI"""
        # Set window properties
        self.setWindowTitle("Chỉnh sửa thông tin")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Full name
        name_label = self.create_label("Họ và tên", bold=True)
        self.name_input = self.create_input_field("Nhập họ và tên")
        if self.parent.parent.current_user:
            self.name_input.setText(self.parent.parent.current_user.get('full_name', ''))
            
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        
        # Email
        email_label = self.create_label("Email", bold=True)
        self.email_input = self.create_input_field("Nhập email")
        if self.parent.parent.current_user:
            self.email_input.setText(self.parent.parent.current_user.get('email', ''))
            
        layout.addWidget(email_label)
        layout.addWidget(self.email_input)
        
        # Phone
        phone_label = self.create_label("Số điện thoại", bold=True)
        self.phone_input = self.create_input_field("Nhập số điện thoại")
        if self.parent.parent.current_user:
            self.phone_input.setText(self.parent.parent.current_user.get('phone', ''))
            
        layout.addWidget(phone_label)
        layout.addWidget(self.phone_input)
        
        # Address
        address_label = self.create_label("Địa chỉ", bold=True)
        self.address_input = self.create_input_field("Nhập địa chỉ")
        if self.parent.parent.current_user:
            self.address_input.setText(self.parent.parent.current_user.get('address', ''))
            
        layout.addWidget(address_label)
        layout.addWidget(self.address_input)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        cancel_btn = self.create_secondary_button("Hủy")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = self.create_primary_button("Lưu")
        save_btn.clicked.connect(self.save_profile)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
    def save_profile(self):
        """Save profile data"""
        # Get form data
        full_name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        address = self.address_input.text().strip()
        
        # Validate data
        if not full_name:
            self.parent.parent.show_warning(
                "Thiếu thông tin",
                "Vui lòng nhập họ và tên"
            )
            return
            
        if not email:
            self.parent.parent.show_warning(
                "Thiếu thông tin",
                "Vui lòng nhập email"
            )
            return
            
        try:
            success = self.parent.parent.user_manager.update_user(
                user_id=self.parent.parent.current_user_id,
                full_name=full_name,
                email=email,
                phone=phone,
                address=address
            )
            
            if success:
                self.parent.parent.show_info(
                    "Thành công",
                    "Đã cập nhật thông tin thành công"
                )
                self.accept()
            else:
                self.parent.parent.show_error(
                    "Lỗi",
                    "Không thể cập nhật thông tin"
                )
                
        except Exception as e:
            self.parent.parent.show_error(
                "Lỗi",
                f"Không thể cập nhật thông tin: {str(e)}"
            )
