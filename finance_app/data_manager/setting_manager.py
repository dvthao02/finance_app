# setting_manager.py

from utils.file_helper import load_json, save_json, generate_id, get_current_datetime
from data_manager.user_manager import UserManager

class SettingManager:
    def __init__(self, file_path='settings.json'):
        import os
        # Get the directory where the package is installed
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(package_dir, 'data')
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(data_dir, file_path)
        self.settings = []
        self.user_manager = UserManager()
        self.current_user_id = None
        self.load_settings()

    def set_current_user(self, user_id):
        """Thiết lập người dùng hiện tại
        Args:
            user_id (str): ID của người dùng
        """
        self.current_user_id = user_id

    def load_settings(self):
        """Tải danh sách settings từ file, đảm bảo mỗi user có settings mặc định."""
        try:
            self.settings = load_json(self.file_path)
        except FileNotFoundError:
            self.settings = []
            save_json(self.file_path, self.settings)
            
        # Ensure all active users have a settings entry
        active_users = self.user_manager.get_all_users(active_only=True)
        for user in active_users:
            user_id = user['user_id']
            if not any(s['user_id'] == user_id for s in self.settings):
                self.settings.append(self._get_default_settings(user_id))
        
        save_json(self.file_path, self.settings)

    def save_settings(self):
        """Lưu danh sách settings vào file."""
        return save_json(self.file_path, self.settings)

    def _get_default_settings(self, user_id):
        """Trả về cài đặt mặc định cho người dùng mới."""
        return {
            'setting_id': generate_id('setting', self.settings),
            'user_id': user_id,
            'currency': 'VND',
            'notification_enabled': True,
            'theme': 'light',
            'report_frequency': 'monthly',
            'created_at': get_current_datetime(),
            'updated_at': get_current_datetime()
        }

    def get_user_settings(self, user_id=None):
        """Lấy cài đặt của một người dùng cụ thể."""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            return self._get_default_settings('default')
            
        for setting in self.settings:
            if setting['user_id'] == user_id:
                return setting
                
        # If settings not found, create and return default
        default_settings = self._get_default_settings(user_id)
        self.settings.append(default_settings)
        self.save_settings()
        return default_settings

    def update_user_settings(self, user_id=None, new_settings=None):
        """Cập nhật cài đặt cho một người dùng."""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or new_settings is None:
            return False
            
        for i, setting in enumerate(self.settings):
            if setting['user_id'] == user_id:
                # Preserve setting_id and user_id
                new_settings['setting_id'] = setting['setting_id']
                new_settings['user_id'] = user_id
                new_settings['updated_at'] = get_current_datetime()
                self.settings[i] = new_settings
                self.save_settings()
                return True
        return False

    def reset_user_settings(self, user_id=None):
        """Reset cài đặt của người dùng về mặc định."""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            return False
            
        default_settings = self._get_default_settings(user_id)
        for i, setting in enumerate(self.settings):
            if setting['user_id'] == user_id:
                self.settings[i] = default_settings
                self.save_settings()
                return True
        return False

    def get_setting_by_id(self, setting_id=None):
        """Lấy cài đặt theo setting_id."""
        if setting_id is None:
            return None
            
        for setting in self.settings:
            if setting['setting_id'] == setting_id:
                return setting
        return None
