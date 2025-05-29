from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QApplication, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from finance_app.data_manager.user_manager import UserManager

class RegisterForm(QDialog):
    """Form đăng ký người dùng mới"""
    register_success = pyqtSignal()  # Signal phát khi đăng ký thành công
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Đăng Ký Tài Khoản")
        self.setFixedWidth(400)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setup_ui()

    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 30, 40, 30)

        # Tiêu đề
        title = QLabel("Đăng Ký Tài Khoản")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Username
        layout.addWidget(QLabel("Tên đăng nhập *"))
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Nhập tên đăng nhập")
        layout.addWidget(self.username_edit)

        # Fullname
        layout.addWidget(QLabel("Họ và tên *"))
        self.fullname_edit = QLineEdit()
        self.fullname_edit.setPlaceholderText("Nhập họ và tên")
        layout.addWidget(self.fullname_edit)

        # Password
        layout.addWidget(QLabel("Mật khẩu *"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Nhập mật khẩu")
        layout.addWidget(self.password_edit)

        # Confirm Password
        layout.addWidget(QLabel("Xác nhận mật khẩu *"))
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.Password)
        self.confirm_edit.setPlaceholderText("Nhập lại mật khẩu")
        layout.addWidget(self.confirm_edit)

        # Password requirements
        req_text = "Mật khẩu phải có:\n- Ít nhất 8 ký tự\n- Chữ hoa và chữ thường\n- Số\n- Ký tự đặc biệt"
        req_label = QLabel(req_text)
        req_label.setStyleSheet("color: #95a5a6; font-size: 9pt;")
        layout.addWidget(req_label)

        # Buttons
        register_btn = QPushButton("Đăng ký")
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2574a9;
            }
        """)
        register_btn.clicked.connect(self.register)
        layout.addWidget(register_btn)

        back_btn = QPushButton("Quay lại đăng nhập")
        back_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)
        back_btn.clicked.connect(self.reject)
        layout.addWidget(back_btn)

    def register(self):
        """Xử lý đăng ký người dùng mới"""
        try:
            u = self.username_edit.text().strip()
            p = self.password_edit.text()
            c = self.confirm_edit.text()
            f = self.fullname_edit.text().strip()

            if not all([u, p, c, f]):
                QMessageBox.critical(self, "Thiếu thông tin", "Vui lòng điền đầy đủ thông tin")
                return

            if p != c:
                QMessageBox.critical(self, "Lỗi", "Mật khẩu không khớp")
                return

            if not UserManager.is_strong_password(p):
                QMessageBox.warning(self, "Mật khẩu yếu", 
                    "Mật khẩu cần có:\n- Ít nhất 8 ký tự\n- Chữ hoa\n- Chữ thường\n- Số\n- Ký tự đặc biệt")
                return

            try:
                user_manager = UserManager()
                result = user_manager.add_user(username=u, password=p, full_name=f)
                
                if result:
                    QMessageBox.information(self, "Thành công", 
                        "Đăng ký thành công!\nBạn có thể đăng nhập với tài khoản vừa tạo.")
                    self.register_success.emit()
                    self.accept()
                else:
                    QMessageBox.critical(self, "Lỗi", "Không thể tạo tài khoản. Vui lòng thử lại.")
                    
            except ValueError as ve:
                QMessageBox.critical(self, "Lỗi", str(ve))
            except Exception as e:
                print(f"Lỗi chi tiết khi đăng ký: {str(e)}")
                QMessageBox.critical(self, "Lỗi", "Có lỗi xảy ra khi tạo tài khoản. Vui lòng thử lại.")
        except Exception as e:
            print(f"Lỗi trong quá trình xử lý đăng ký: {str(e)}")
            QMessageBox.critical(self, "Lỗi", "Có lỗi xảy ra. Vui lòng thử lại.")

    def keyPressEvent(self, event):
        """Xử lý sự kiện phím tắt"""
        if event.key() == Qt.Key_Return:  # Enter để đăng ký
            self.register()
        elif event.key() == Qt.Key_Escape:  # Esc để quay lại
            self.reject()


