# notification_manager.py

from utils.file_helper import load_json, save_json, generate_id, get_current_datetime
from datetime import datetime
from data_manager.user_manager import UserManager

class NotificationManager:
    def __init__(self, file_path='notifications.json'):
        import os
        # Get the directory where the package is installed
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(package_dir, 'data')
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(data_dir, file_path)
        self.notifications = self.load_notifications()
        self.user_manager = UserManager()  # Thêm UserManager
        self.current_user_id = None

    def set_current_user(self, user_id):
        """Thiết lập người dùng hiện tại
        Args:
            user_id (str): ID của người dùng
        """
        self.current_user_id = user_id
    
    def load_notifications(self):
        """Tải danh sách notifications từ file"""
        return load_json(self.file_path)
    
    def save_notifications(self):
        """Lưu danh sách notifications vào file"""
        return save_json(self.file_path, self.notifications)
    
    def get_user_notifications(self, user_id, is_admin=False):
        """Get all notifications for a user or all if admin"""
        if is_admin:
            return self.notifications
        return [n for n in self.notifications if n['user_id'] == user_id]
    
    def get_all_notifications(self, user_id=None, target_user_id=None, unread_only=False):
        """
        Lấy tất cả notifications
        Args:
            user_id: ID người dùng thực hiện yêu cầu (None để sử dụng current_user_id)
            target_user_id: ID người dùng cần lấy dữ liệu (None để lấy của chính user_id)
            unread_only: True để chỉ lấy thông báo chưa đọc
        """
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            return []
            
        if target_user_id and target_user_id != user_id and not self.user_manager.is_admin(user_id):
            raise ValueError("Không có quyền truy cập thông báo của người dùng khác")
        
        result = self.notifications.copy()
        
        if target_user_id:
            result = [notif for notif in result if notif['user_id'] == target_user_id]
        else:
            result = [notif for notif in result if notif['user_id'] == user_id]
        
        if unread_only:
            result = [notif for notif in result if not notif.get('is_read', False)]
        
        # Sắp xếp theo thời gian tạo mới nhất
        result.sort(key=lambda x: x['created_at'], reverse=True)
        
        return result
    
    def get_notification_by_id(self, user_id=None, notification_id=None):
        """Lấy notification theo ID"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or notification_id is None:
            return None
            
        for notif in self.notifications:
            if notif['notification_id'] == notification_id:
                if notif['user_id'] != user_id and not self.user_manager.is_admin(user_id):
                    raise ValueError("Không có quyền truy cập thông báo này")
                return notif
        return None
    
    def create_notification(self, user_id=None, notification_type=None, title=None, message=None, 
                          priority='medium', data=None):
        """
        Tạo notification mới
        """
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or notification_type is None or title is None or message is None:
            return False, "Thiếu thông tin bắt buộc"
            
        # Kiểm tra user_id
        if not self.user_manager.get_user_by_id(user_id):
            return False, f"Không tìm thấy người dùng với ID: {user_id}"
        
        valid_types = ['budget_alert', 'transaction_alert', 'recurring_reminder', 
                      'income_received', 'goal_achievement', 'system']
        
        if notification_type not in valid_types:
            return False, "Loại thông báo không hợp lệ"
        
        valid_priorities = ['low', 'medium', 'high']
        if priority not in valid_priorities:
            return False, "Độ ưu tiên không hợp lệ"
        
        new_notification = {
            'notification_id': generate_id('notif', self.notifications),
            'user_id': user_id,
            'type': notification_type,
            'title': title,
            'message': message,
            'is_read': False,
            'priority': priority,
            'created_at': get_current_datetime(),
            'read_at': None,
            'data': data or {}
        }
        
        self.notifications.append(new_notification)
        
        if self.save_notifications():
            return True, new_notification
        return False, "Lỗi khi lưu file"
    
    def mark_as_read(self, user_id=None, notification_id=None):
        """Đánh dấu notification đã đọc"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or notification_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        notification = self.get_notification_by_id(user_id, notification_id)
        if not notification:
            return False, "Không tìm thấy thông báo hoặc không có quyền"
        
        notification['is_read'] = True
        notification['read_at'] = get_current_datetime()
        
        if self.save_notifications():
            return True, "Đã đánh dấu thông báo đã đọc"
        return False, "Lỗi khi lưu file"
    
    def mark_as_unread(self, user_id=None, notification_id=None):
        """Đánh dấu notification chưa đọc"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or notification_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        notification = self.get_notification_by_id(user_id, notification_id)
        if not notification:
            return False, "Không tìm thấy thông báo hoặc không có quyền"
        
        notification['is_read'] = False
        notification['read_at'] = None
        
        if self.save_notifications():
            return True, "Đã đánh dấu thông báo chưa đọc"
        return False, "Lỗi khi lưu file"
    
    def mark_all_as_read(self, user_id=None, target_user_id=None):
        """Đánh dấu tất cả notifications của user đã đọc"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        notifications = self.get_all_notifications(user_id, target_user_id, unread_only=True)
        current_time = get_current_datetime()
        
        for notification in notifications:
            notification['is_read'] = True
            notification['read_at'] = current_time
        
        if self.save_notifications():
            return True, f"Đã đánh dấu {len(notifications)} thông báo đã đọc"
        return False, "Lỗi khi lưu file"
    
    def delete_notification(self, user_id=None, notification_id=None):
        """Xóa notification"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or notification_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        notification = self.get_notification_by_id(user_id, notification_id)
        if not notification:
            return False, "Không tìm thấy thông báo hoặc không có quyền"
        
        for i, notif in enumerate(self.notifications):
            if notif['notification_id'] == notification_id:
                del self.notifications[i]
                if self.save_notifications():
                    return True, "Đã xóa thông báo"
                return False, "Lỗi khi lưu file"
            
        return False, "Không tìm thấy thông báo"
    
    def delete_user_notifications(self, user_id):
        """Delete all notifications for a user
        
        Args:
            user_id (str): ID of the user whose notifications should be deleted
        """
        if not user_id:
            return
        
        notifications = self.load_notifications()
        notifications = [n for n in notifications if n['user_id'] != user_id]
        self.save_notifications(notifications)
        print(f"Đã xóa tất cả thông báo của người dùng: {user_id}")
        return True

# No major bug found, ensure all id keys are correct and consistent.