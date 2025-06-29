# setting_manager.py

from finance_app.utils.file_helper import load_json, save_json, generate_id, get_current_datetime
from finance_app.data_manager.user_manager import UserManager

class SettingManager:
    def __init__(self, file_path='settings.json'):
        import os
        # Get the directory where the package is installed
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(package_dir, 'data')
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(data_dir, file_path)
        self.settings = None # Defer loading
        self.user_manager = UserManager()
        self.current_user_id = None
        # self.load_settings() # Removed eager loading

    def _load_data_if_needed(self):
        if self.settings is None:
            self.settings = self.load_settings_internal()

    def set_current_user(self, user_id):
        """Thiết lập người dùng hiện tại
        Args:
            user_id (str): ID của người dùng
        """
        self.current_user_id = user_id

    def load_settings_internal(self):
        """Tải danh sách settings từ file, đảm bảo mỗi user có settings mặc định."""
        try:
            settings_data = load_json(self.file_path)
        except FileNotFoundError:
            settings_data = []
            save_json(self.file_path, settings_data) # Save empty list if file not found
            
        # Ensure all active users have a settings entry
        active_users = self.user_manager.get_all_users(active_only=True)
        # Create a dictionary for faster lookup of existing settings
        user_settings_map = {s['user_id']: s for s in settings_data}
        
        updated = False
        for user in active_users:
            user_id = user['user_id']
            if user_id not in user_settings_map:
                default_setting = self._get_default_settings(user_id)
                settings_data.append(default_setting)
                user_settings_map[user_id] = default_setting # Add to map as well
                updated = True
        
        if updated:
            save_json(self.file_path, settings_data)
        return settings_data

    def save_settings(self):
        """Lưu danh sách settings vào file."""
        self._load_data_if_needed() # Ensure settings are loaded
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
        self._load_data_if_needed() # Load data if not already loaded
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            # For a generic 'default' user or unauthenticated state,
            # return a default structure without saving it.
            return {
                'setting_id': 'default_setting',
                'user_id': 'default',
                'currency': 'VND',
                'notification_enabled': True,
                'theme': 'light',
                'report_frequency': 'monthly',
                'created_at': get_current_datetime(),
                'updated_at': get_current_datetime()
            }
            
        for setting in self.settings:
            if setting['user_id'] == user_id:
                return setting
                
        # If settings not found for a specific user_id, create, save, and return default
        default_settings = self._get_default_settings(user_id)
        self.settings.append(default_settings)
        self.save_settings() # Save if new default is added
        return default_settings

    def get_setting(self, key, user_id=None, default=None):
        """Lấy một giá trị cài đặt cụ thể cho người dùng."""
        user_settings = self.get_user_settings(user_id) # This already handles loading and defaults
        if user_settings:
            return user_settings.get(key, default)
        return default # Should not happen if get_user_settings works correctly

    def update_user_setting(self, key, value, user_id=None):
        """Cập nhật một giá trị cài đặt cho người dùng."""
        self._load_data_if_needed() # Load data if not already loaded
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            return False
            
        for i, setting in enumerate(self.settings):
            if setting['user_id'] == user_id:
                setting[key] = value
                setting['updated_at'] = get_current_datetime()
                self.settings[i] = setting
                self.save_settings()
                return True
        return False

    def reset_user_settings(self, user_id=None):
        """Reset cài đặt của người dùng về mặc định."""
        self._load_data_if_needed() # Load data if not already loaded
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
        self._load_data_if_needed() # Load data if not already loaded
        if setting_id is None:
            return None
            
        for setting in self.settings:
            if setting['setting_id'] == setting_id:
                return setting
        return None
