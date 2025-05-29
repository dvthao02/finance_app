# user_manager.py

import bcrypt
import re
from datetime import datetime
from utils.file_helper import load_json, save_json, generate_id

import os

class UserManager:
    def __init__(self, user_file='users.json'):
        # Get the directory where the package is installed
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(package_dir, 'data')
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        self.user_file = os.path.join(data_dir, user_file)

    def load_users(self):
        return load_json(self.user_file)

    def save_users(self, users):
        save_json(self.user_file, users)

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    @staticmethod
    def is_strong_password(password):
        return (
            len(password) >= 8 and
            re.search(r'[a-z]', password) and
            re.search(r'[A-Z]', password) and
            re.search(r'\d', password) and
            re.search(r'[^\w\s]', password)
        )

    def is_admin(self, user_id):
        """Kiểm tra xem user_id có phải là admin không"""
        user = self.get_user_by_id(user_id)
        return user and user.get('is_admin', False)    
    def find_user_by_username(self, username):
        users = self.load_users()
        print(f"Searching for user '{username}' in {len(users)} users")
        for user in users:
            if user['username'] == username:
                print(f"Found user: {user}")
                return user
        print(f"User '{username}' not found")
        return None

    def add_user(self, username, password, full_name="", email="", phone="", date_of_birth="", address="", is_admin=False):
        users = self.load_users()

        if self.find_user_by_username(username):
            raise ValueError("Tên người dùng đã tồn tại.")

        if not self.is_strong_password(password):
            raise ValueError("Mật khẩu yếu. Phải gồm chữ hoa, thường, số và ký tự đặc biệt, ít nhất 8 ký tự.")

        now = datetime.now().isoformat()
        user = {
            "user_id": generate_id("user", users),
            "username": username,
            "password": self.hash_password(password),
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "is_admin": is_admin,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "avatar": None,
            "date_of_birth": date_of_birth,
            "address": address
        }
        users.append(user)
        self.save_users(users)
        print(f"Đã thêm người dùng mới với ID: {user['user_id']}")
        return user    
    def authenticate_user(self, username, password):
        user = self.find_user_by_username(username)
        
        if not user:
            return {"status": "error", "message": "Sai tên đăng nhập hoặc mật khẩu."}
            
        if not user.get('is_active', True):
            return {"status": "locked", "message": "Tài khoản đã bị khóa."}
            
        if not self.check_password(password, user['password']):
            return {"status": "error", "message": "Sai tên đăng nhập hoặc mật khẩu."}
            
        return {"status": "success", "user": user}

    def change_password(self, username, old_password, new_password):
        users = self.load_users()
        for user in users:
            if user['username'] == username and self.check_password(old_password, user['password']):
                if not self.is_strong_password(new_password):
                    raise ValueError("Mật khẩu mới không đủ mạnh.")
                user['password'] = self.hash_password(new_password)
                user['updated_at'] = datetime.now().isoformat()
                self.save_users(users)
                print("Đổi mật khẩu thành công.")
                return True
        raise ValueError("Sai mật khẩu cũ hoặc người dùng không tồn tại.")

    def deactivate_user(self, username):
        users = self.load_users()
        for user in users:
            if user['username'] == username:
                user['is_active'] = False
                user['updated_at'] = datetime.now().isoformat()
                self.save_users(users)
                print("Tài khoản đã được tắt.")
                return True
        raise ValueError("Không tìm thấy người dùng để tắt.")

    def activate_user(self, username):
        users = self.load_users()
        for user in users:
            if user['username'] == username:
                user['is_active'] = True
                user['updated_at'] = datetime.now().isoformat()
                self.save_users(users)
                print("Tài khoản đã được kích hoạt.")
                return True
        raise ValueError("Không tìm thấy người dùng để kích hoạt.")

    def update_user_info(self, username, full_name=None, email=None, phone=None, date_of_birth=None, address=None):
        users = self.load_users()
        for user in users:
            if user['username'] == username:
                if full_name is not None:
                    user['full_name'] = full_name
                if email is not None:
                    user['email'] = email
                if phone is not None:
                    user['phone'] = phone
                if date_of_birth is not None:
                    user['date_of_birth'] = date_of_birth
                if address is not None:
                    user['address'] = address
                user['updated_at'] = datetime.now().isoformat()
                self.save_users(users)
                print("Thông tin người dùng đã được cập nhật.")
                return True
        raise ValueError("Không tìm thấy người dùng để cập nhật thông tin.")

    def get_all_users(self, active_only=True):
        users = self.load_users()
        return [user for user in users if user['is_active']] if active_only else users

    def get_user_by_id(self, user_id):
        users = self.load_users()
        for user in users:
            if user['user_id'] == user_id:
                return user
        return None  # Thay đổi để trả về None thay vì raise ValueError

    def delete_user(self, username):
        users = self.load_users()
        for i, user in enumerate(users):
            if user['username'] == username:
                del users[i]
                self.save_users(users)
                print("Người dùng đã được xóa.")
                return True
        raise ValueError("Không tìm thấy người dùng để xóa.")

    def get_user_avatar(self, username):
        user = self.find_user_by_username(username)
        if user:
            return user.get('avatar', None)
        raise ValueError("Không tìm thấy người dùng để lấy ảnh đại diện.")

    def set_user_avatar(self, username, avatar_path):
        users = self.load_users()
        for user in users:
            if user['username'] == username:
                user['avatar'] = avatar_path
                user['updated_at'] = datetime.now().isoformat()
                self.save_users(users)
                print("Ảnh đại diện đã được cập nhật.")
                return True
        raise ValueError("Không tìm thấy người dùng để cập nhật ảnh đại diện.")

    def reset_all_passwords(self, new_password="123456aA@"):
        """Reset mật khẩu của tất cả users thành mật khẩu mặc định"""
        if not self.is_strong_password(new_password):
            raise ValueError("Mật khẩu mới không đủ mạnh")
            
        users = self.load_users()
        updated_count = 0
        
        for user in users:
            user['password'] = self.hash_password(new_password)
            user['updated_at'] = datetime.now().isoformat()
            updated_count += 1
            
        self.save_users(users)
        print(f"Đã reset mật khẩu cho {updated_count} tài khoản")
        return updated_count        
# Reset tất cả về 123456aA@  