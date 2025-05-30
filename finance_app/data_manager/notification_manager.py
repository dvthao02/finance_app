# notification_manager.py

from finance_app.utils.file_helper import load_json, save_json, generate_id, get_current_datetime
from datetime import datetime
from finance_app.data_manager.user_manager import UserManager

class NotificationManager:
    def __init__(self, file_path='notifications.json'):
        import os
        # Get the directory where the package is installed
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(package_dir, 'data')
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(data_dir, file_path)
        self.notifications = None # Defer loading
        self.user_manager = UserManager() 
        self.current_user_id = None

    def _load_data_if_needed(self):
        if self.notifications is None:
            self.notifications = load_json(self.file_path)

    def _save_data(self):
        return save_json(self.file_path, self.notifications)

    def set_current_user(self, user_id):
        """Thiết lập người dùng hiện tại
        Args:
            user_id (str): ID của người dùng
        """
        self.current_user_id = user_id
    
    def get_user_notifications(self, user_id, is_admin=False, unread_only=False):
        """Get all notifications for a user or all if admin"""
        self._load_data_if_needed()
        
        # Use self.current_user_id if user_id is not explicitly provided
        # This part was missing in the original get_user_notifications, 
        # but present in get_all_notifications. Aligning for consistency.
        if user_id is None: 
            user_id = self.current_user_id

        if user_id is None and not is_admin: # if still no user_id and not admin, return empty
            return []

        data_to_filter = []
        if is_admin:
            # Admin can see all notifications if no specific user_id is targeted by them
            # Or, if a user_id is provided, admin sees that user's notifications.
            if user_id: # If admin is targeting a specific user
                 data_to_filter = [n for n in self.notifications if n['user_id'] == user_id]
            else: # Admin sees all if no target_user_id
                 data_to_filter = self.notifications.copy()
        else: # Non-admin users only see their own notifications
            if user_id: # Should always have a user_id for non-admins
                data_to_filter = [n for n in self.notifications if n['user_id'] == user_id]
            else: # Should not happen if logic is correct, but as a fallback
                return []
        
        if unread_only:
            data_to_filter = [n for n in data_to_filter if not n.get('is_read', False)]
            
        data_to_filter.sort(key=lambda x: x['created_at'], reverse=True)
        return data_to_filter
    
    def get_all_notifications(self, user_id=None, target_user_id=None, unread_only=False):
        self._load_data_if_needed()
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            return []
            
        if target_user_id and target_user_id != user_id and not self.user_manager.is_admin(user_id):
            raise ValueError("Không có quyền truy cập thông báo của người dùng khác")
        
        # Determine whose notifications to fetch
        actual_target_user_id = target_user_id if target_user_id else user_id

        result = [notif for notif in self.notifications if notif['user_id'] == actual_target_user_id]
        
        if unread_only:
            result = [notif for notif in result if not notif.get('is_read', False)]
        
        # Sắp xếp theo thời gian tạo mới nhất
        result.sort(key=lambda x: x['created_at'], reverse=True)
        
        return result
    
    def get_notification_by_id(self, user_id=None, notification_id=None):
        """Lấy notification theo ID"""
        self._load_data_if_needed()
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
        self._load_data_if_needed()
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
        
        if self._save_data():
            return True, new_notification
        return False, "Lỗi khi lưu file"
    
    def mark_as_read(self, user_id=None, notification_id=None):
        """Đánh dấu notification đã đọc"""
        self._load_data_if_needed()
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or notification_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        notification = self.get_notification_by_id(user_id, notification_id)
        if not notification:
            return False, "Không tìm thấy thông báo hoặc không có quyền"
        
        notification['is_read'] = True
        notification['read_at'] = get_current_datetime()
        
        if self._save_data():
            return True, "Đã đánh dấu thông báo đã đọc"
        return False, "Lỗi khi lưu file"
    
    def mark_as_unread(self, user_id=None, notification_id=None):
        """Đánh dấu notification chưa đọc"""
        self._load_data_if_needed()
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or notification_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        notification = self.get_notification_by_id(user_id, notification_id)
        if not notification:
            return False, "Không tìm thấy thông báo hoặc không có quyền"
        
        notification['is_read'] = False
        notification['read_at'] = None
        
        if self._save_data():
            return True, "Đã đánh dấu thông báo chưa đọc"
        return False, "Lỗi khi lưu file"
    
    def mark_all_as_read(self, user_id=None, target_user_id=None):
        """Đánh dấu tất cả notifications của user đã đọc"""
        self._load_data_if_needed()
        if user_id is None:
            user_id = self.current_user_id # User performing the action
            
        if user_id is None:
            return False, "Thiếu thông tin người dùng thực hiện"

        # Determine whose notifications to mark. If target_user_id is not provided,
        # it means the current user is marking their own notifications as read.
        user_to_update_id = target_user_id if target_user_id else user_id

        # Permission check: Only admin can mark others' notifications
        if user_to_update_id != user_id and not self.user_manager.is_admin(user_id):
            return False, "Không có quyền đánh dấu thông báo của người dùng khác"

        current_time = get_current_datetime()
        marked_count = 0
        for notification in self.notifications:
            if notification['user_id'] == user_to_update_id and not notification.get('is_read', False):
                notification['is_read'] = True
                notification['read_at'] = current_time
                marked_count +=1
        
        if marked_count > 0:
            if self._save_data():
                return True, f"Đã đánh dấu {marked_count} thông báo đã đọc cho người dùng {user_to_update_id}"
            return False, "Lỗi khi lưu file"
        return True, f"Không có thông báo chưa đọc nào cho người dùng {user_to_update_id}"
    
    def delete_notification(self, user_id=None, notification_id=None):
        """Xóa notification"""
        self._load_data_if_needed()
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or notification_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        notification = self.get_notification_by_id(user_id, notification_id)
        if not notification:
            return False, "Không tìm thấy thông báo hoặc không có quyền"
        
        for i, notif in enumerate(self.notifications):
            if notif['notification_id'] == notification_id:
                # Permission check already done by get_notification_by_id implicitly
                del self.notifications[i]
                if self._save_data():
                    return True, "Đã xóa thông báo"
                return False, "Lỗi khi lưu file"
            
        return False, "Không tìm thấy thông báo"
    
    def delete_user_notifications(self, user_id):
        """Delete all notifications for a user
        
        Args:
            user_id (str): ID of the user whose notifications should be deleted
        """
        self._load_data_if_needed()
        if not user_id:
            return False, "User ID is required"
        
        initial_count = len(self.notifications)
        self.notifications = [n for n in self.notifications if n['user_id'] != user_id]
        
        if len(self.notifications) < initial_count:
            if self._save_data():
                return True, f"Successfully deleted {initial_count - len(self.notifications)} notifications for user {user_id}."
            else:
                return False, "Error saving data after deleting user notifications."
        return True, "No notifications found for this user to delete."

# No major bug found, ensure all id keys are correct and consistent.