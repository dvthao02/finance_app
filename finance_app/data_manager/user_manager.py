# user_manager.py

import bcrypt
# import re # No longer needed directly here
import os
import json
import logging
from datetime import datetime
from finance_app.utils.file_helper import (
    load_json, save_json, generate_id,
    is_valid_email, is_valid_phone, is_strong_password # Import new validation functions
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self, user_file='users.json'):
        # Get the directory where the package is installed
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(package_dir, 'data')
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        self.user_file = os.path.join(data_dir, user_file)
        
        # Initialize users file if it doesn't exist
        if not os.path.exists(self.user_file):
            logger.info(f"Creating new users file at {self.user_file}")
            self.save_users([])
            
        # Create default admin if no users exist
        users = self.load_users()
        if not users:
            logger.info("Creating default admin user")
            self.add_user(
                username="admin",
                password="Admin@123",
                full_name="Administrator",
                is_admin=True
            )

    def set_current_user(self, user_id):
        """Thiết lập người dùng hiện tại cho manager.
        Args:
            user_id (str): ID của người dùng
        """
        # This manager typically loads all users, but setting current_user_id 
        # can be useful for context-specific operations or logging.
        self.current_user_id = user_id
        logger.debug(f"UserManager current user set to: {user_id}")

    def load_users(self):
        try:
            users = load_json(self.user_file)
            logger.debug(f"Loaded {len(users)} users from {self.user_file}")
            return users
        except Exception as e:
            logger.error(f"Error loading users: {str(e)}")
            return []

    def save_users(self, users):
        try:
            save_json(self.user_file, users)
            logger.debug(f"Saved {len(users)} users to {self.user_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving users: {str(e)}")
            return False

    def hash_password(self, password):
        try:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {str(e)}")
            raise ValueError("Error processing password")

    def check_password(self, password, hashed):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error checking password: {str(e)}")
            return False

    def is_email_unique(self, email, user_id_to_exclude=None):
        if not email: # Empty email is considered unique in terms of not clashing
            return True
        users = self.load_users()
        for user in users:
            if user.get('user_id') == user_id_to_exclude:
                continue
            if user.get('email') == email:
                return False
        return True

    def is_phone_unique(self, phone, user_id_to_exclude=None):
        if not phone: # Empty phone is considered unique
            return True
        users = self.load_users()
        for user in users:
            if user.get('user_id') == user_id_to_exclude:
                continue
            if user.get('phone') == phone:
                return False
        return True

    def is_admin(self, user_id):
        """Kiểm tra xem user_id có phải là admin không"""
        try:
            user = self.get_user_by_id(user_id)
            return user and user.get('is_admin', False)
        except Exception as e:
            logger.error(f"Error checking admin status: {str(e)}")
            return False

    def find_user_by_username(self, username):
        if not username:
            return None
            
        try:
            users = self.load_users()
            logger.debug(f"Searching for user '{username}' in {len(users)} users")
            
            for user in users:
                if user['username'].lower() == username.lower():
                    logger.debug(f"Found user: {user['username']}")
                    return user
                    
            logger.debug(f"User '{username}' not found")
            return None
            
        except Exception as e:
            logger.error(f"Error finding user: {str(e)}")
            return None

    def authenticate_user(self, username, password):
        try:
            if not username or not password:
                logger.warning("Empty username or password")
                return {"status": "error", "message": "Vui lòng nhập tên đăng nhập và mật khẩu."}
                
            user = self.find_user_by_username(username)
            
            if not user:
                logger.warning(f"Failed login attempt for non-existent user: {username}")
                return {"status": "error", "message": "Sai tên đăng nhập hoặc mật khẩu."}
                
            if not user.get('is_active', True):
                logger.warning(f"Login attempt for locked user: {username}")
                return {"status": "error", "message": "Tài khoản đã bị khóa."}
                
            if not self.check_password(password, user['password']):
                logger.warning(f"Failed login attempt for user: {username}")
                return {"status": "error", "message": "Sai tên đăng nhập hoặc mật khẩu."}
                
            # Update last login time
            users = self.load_users()
            for u in users:
                if u['username'] == username:
                    u['last_login'] = datetime.now().isoformat()
                    break
            self.save_users(users)
            
            logger.info(f"Successful login for user: {username}")
            return {"status": "success", "user": user}
            
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return {"status": "error", "message": "Lỗi xác thực. Vui lòng thử lại sau."}

    def add_user(self, username, password, full_name="", email="", phone="", date_of_birth="", address="", is_admin=False):
        try:
            if not username or not password:
                raise ValueError("Tên đăng nhập và mật khẩu không được để trống.")

            users = self.load_users()

            if self.find_user_by_username(username):
                raise ValueError("Tên người dùng đã tồn tại.")

            if not is_strong_password(password): # Use imported function
                raise ValueError("Mật khẩu yếu. Phải gồm chữ hoa, thường, số và ký tự đặc biệt, ít nhất 8 ký tự.")

            # Email and Phone validation
            if email and not is_valid_email(email): # Use imported function
                raise ValueError("Định dạng email không hợp lệ.")
            if email and not self.is_email_unique(email):
                raise ValueError("Địa chỉ email đã được sử dụng.")

            if phone and not is_valid_phone(phone): # Use imported function
                raise ValueError("Định dạng số điện thoại không hợp lệ. (VD: 10-11 số)")
            if phone and not self.is_phone_unique(phone):
                raise ValueError("Số điện thoại đã được sử dụng.")

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
                "last_login": None,
                "avatar": None,
                "date_of_birth": date_of_birth,
                "address": address
            }
            
            users.append(user)
            if self.save_users(users):
                logger.info(f"Added new user: {username}")
                return user
            else:
                raise Exception("Failed to save user data")
                
        except Exception as e:
            logger.error(f"Error adding user: {str(e)}")
            raise

    def update_user(self, user_id, **kwargs):
        try:
            if not user_id:
                raise ValueError("User ID is required")
                
            users = self.load_users()
            user_to_update = None
            for u in users:
                if u['user_id'] == user_id:
                    user_to_update = u
                    break
            
            if not user_to_update:
                # This case should ideally not happen if user_id is always valid when called
                logger.error(f"User with ID {user_id} not found for update.")
                raise ValueError(f"User with ID {user_id} not found.")

            user_data_changed = False

            # Validate and prepare email if provided
            if 'email' in kwargs:
                email_to_check = kwargs['email']
                if email_to_check != user_to_update.get('email'):
                    if email_to_check and not is_valid_email(email_to_check): # Use imported function
                        raise ValueError("Định dạng email không hợp lệ.")
                    if email_to_check and not self.is_email_unique(email_to_check, user_id_to_exclude=user_id):
                        raise ValueError("Địa chỉ email đã được sử dụng.")
                    user_to_update['email'] = email_to_check
                    user_data_changed = True

            # Validate and prepare phone if provided
            if 'phone' in kwargs:
                phone_to_check = kwargs['phone']
                if phone_to_check != user_to_update.get('phone'):
                    if phone_to_check and not is_valid_phone(phone_to_check): # Use imported function
                        raise ValueError("Định dạng số điện thoại không hợp lệ. (VD: 10-11 số)")
                    if phone_to_check and not self.is_phone_unique(phone_to_check, user_id_to_exclude=user_id):
                        raise ValueError("Số điện thoại đã được sử dụng.")
                    user_to_update['phone'] = phone_to_check
                    user_data_changed = True
            
            # Update other allowed fields
            allowed_fields = ['full_name', 'date_of_birth', 'address', 'is_active'] # email and phone handled above
            for field in allowed_fields:
                if field in kwargs:
                    if user_to_update.get(field) != kwargs[field]:
                        user_to_update[field] = kwargs[field]
                        user_data_changed = True
                            
            if user_data_changed:
                user_to_update['updated_at'] = datetime.now().isoformat()
                if self.save_users(users):
                    logger.info(f"Updated user: {user_id}")
                    return True # Successfully updated
                else:
                    # This case implies save_users failed, which logs its own error
                    raise Exception("Lưu dữ liệu người dùng thất bại sau khi cập nhật.") 
            
            return False # No actual changes were made or needed saving
            
        except ValueError as ve: # Catch ValueErrors from validations and re-raise
            logger.warning(f"Validation error updating user {user_id}: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            # Wrap other exceptions in a generic one or re-raise if specific handling is not needed here
            raise Exception(f"Lỗi không xác định khi cập nhật người dùng: {str(e)}")

    def delete_user(self, user_id):
        try:
            if not user_id:
                raise ValueError("User ID is required")
                
            users = self.load_users()
            
            for i, user in enumerate(users):
                if user['user_id'] == user_id:
                    del users[i]
                    if self.save_users(users):
                        logger.info(f"Deleted user: {user_id}")
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False

    def toggle_user_lock(self, user_id, lock=True):
        try:
            users = self.load_users()
            user_updated = False
            for user in users:
                if user['user_id'] == user_id:
                    user['is_active'] = not lock
                    user['updated_at'] = datetime.now().isoformat()
                    user_updated = True
                    break
            
            if user_updated and self.save_users(users):
                logger.info(f"User {user_id} lock status set to {lock}")
                return True
            logger.warning(f"User {user_id} not found or failed to update lock status.")
            return False
        except Exception as e:
            logger.error(f"Error toggling user lock for {user_id}: {str(e)}")
            return False

    def admin_reset_password(self, user_id, new_password):
        try:
            if not user_id:
                return {"status": "error", "message": "User ID is required."}
            if not new_password:
                return {"status": "error", "message": "New password cannot be empty."}

            if not is_strong_password(new_password): # Use imported function
                return {"status": "error", "message": "Mật khẩu yếu. Phải gồm chữ hoa, thường, số và ký tự đặc biệt, ít nhất 8 ký tự."}

            users = self.load_users()
            user_found = False
            for user in users:
                if user['user_id'] == user_id:
                    user['password'] = self.hash_password(new_password)
                    user['updated_at'] = datetime.now().isoformat()
                    user_found = True
                    break
            
            if not user_found:
                return {"status": "error", "message": "User not found."}

            if self.save_users(users):
                logger.info(f"Admin reset password for user: {user_id}")
                return {"status": "success", "message": "Password reset successfully."}
            else:
                return {"status": "error", "message": "Failed to save updated user data."}
        except Exception as e:
            logger.error(f"Error resetting password for user {user_id}: {str(e)}")
            return {"status": "error", "message": f"An error occurred: {str(e)}"}

    def change_password(self, username, old_password, new_password):
        users = self.load_users()
        for user in users:
            if user['username'] == username and self.check_password(old_password, user['password']):
                if not is_strong_password(new_password): # Use imported function
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
        if not is_strong_password(new_password): # Use imported function
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