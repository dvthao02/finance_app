# category_manager.py

from utils.file_helper import load_json, save_json, generate_id, get_current_datetime
from data_manager.user_manager import UserManager

class CategoryManager:
    def __init__(self, file_path='categories.json'):
        import os
        # Get the directory where the package is installed
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(package_dir, 'data')
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(data_dir, file_path)
        self.categories = self.load_categories()
        self.user_manager = UserManager()
        self.current_user_id = None

    def set_current_user(self, user_id):
        """Thiết lập người dùng hiện tại
        Args:
            user_id (str): ID của người dùng
        """
        self.current_user_id = user_id

    def load_categories(self):
        """Tải danh sách categories từ file"""
        return load_json(self.file_path)

    def save_categories(self):
        """Lưu danh sách categories vào file"""
        return save_json(self.file_path, self.categories)

    def get_all_categories(self, user_id=None, category_type=None, active_only=True):
        """
        Lấy tất cả categories
        Args:
            user_id: ID người dùng thực hiện yêu cầu (nếu None, sử dụng current_user_id)
            category_type: 'income', 'expense' hoặc None (lấy tất cả)
            active_only: True để chỉ lấy categories đang hoạt động
        """
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            return []
            
        result = self.categories.copy()

        # Nếu không phải admin, chỉ lấy categories của người dùng hoặc categories chung (user_id=None)
        if not self.user_manager.is_admin(user_id):
            result = [cat for cat in result if cat.get('user_id') == user_id or cat.get('user_id') is None]

        if active_only:
            result = [cat for cat in result if cat.get('is_active', True)]

        if category_type:
            result = [cat for cat in result if cat.get('type') == category_type]

        return result

    def get_category_by_id(self, user_id, category_id, is_admin=False):
        """Lấy category theo ID"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or category_id is None:
            return None
            
        for category in self.categories:
            if category.get('category_id') == category_id:
                if is_admin or category.get('user_id') in [user_id, None]:
                    return category
        return None

    def get_category_by_id(self, category_id):
        """
        Lấy category theo ID
        Args:
            category_id: ID của category cần lấy
        Returns:
            dict: Thông tin category hoặc None nếu không tìm thấy
        """
        if not category_id:
            return None
            
        for category in self.categories:
            if category.get('category_id') == category_id:
                return category
        return None

    def get_categories_by_type(self, user_id=None, category_type=None):
        """Lấy categories theo loại (income/expense)"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or category_type is None:
            return []
            
        return [cat for cat in self.get_all_categories(user_id, active_only=True) 
                if cat.get('type') == category_type]

    def create_category(self, user_id=None, name=None, category_type=None, icon="📝", color="#808080", description=""):
        """
        Tạo category mới
        """
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or name is None or category_type is None:
            return False, "Thiếu thông tin bắt buộc"
            
        # Kiểm tra quyền quản trị: Chỉ admin mới có thể tạo category mới
        if not self.user_manager.is_admin(user_id):
            return False, "Chỉ quản trị viên mới có thể tạo danh mục mới"
            
        # Kiểm tra tên đã tồn tại trong phạm vi người dùng hoặc toàn cục
        existing = self.get_category_by_name(user_id, name)
        if existing:
            return False, "Tên category đã tồn tại"

        # Kiểm tra loại hợp lệ
        if category_type not in ['income', 'expense']:
            return False, "Loại category phải là 'income' hoặc 'expense'"

        new_category = {
            'category_id': generate_id('cat', self.categories),
            'name': name,
            'type': category_type,
            'icon': icon,
            'color': color,
            'description': description,
            'is_active': True,
            'created_at': get_current_datetime(),
            'user_id': None  # Admin tạo category chung
        }

        self.categories.append(new_category)

        if self.save_categories():
            return True, new_category
        return False, "Lỗi khi lưu file"

    def update_category(self, user_id=None, category_id=None, **kwargs):
        """
        Cập nhật category
        """
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or category_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        category = self.get_category_by_id(user_id, category_id)
        if not category:
            return False, "Không tìm thấy category hoặc không có quyền"

        # Kiểm tra quyền: Người dùng thường chỉ cập nhật category của họ, admin cập nhật bất kỳ category nào
        if not self.user_manager.is_admin(user_id) and category.get('user_id') != user_id:
            return False, "Không có quyền cập nhật category này"

        # Kiểm tra tên trùng lặp (nếu update name)
        if 'name' in kwargs:
            existing = self.get_category_by_name(user_id, kwargs['name'])
            if existing and existing['category_id'] != category_id:
                return False, "Tên category đã tồn tại"

        # Kiểm tra type hợp lệ
        if 'type' in kwargs and kwargs['type'] not in ['income', 'expense']:
            return False, "Loại category phải là 'income' hoặc 'expense'"

        # Update các trường
        allowed_fields = ['name', 'type', 'icon', 'color', 'description', 'is_active']
        for field in allowed_fields:
            if field in kwargs:
                category[field] = kwargs[field]

        if self.save_categories():
            return True, category
        return False, "Lỗi khi lưu file"

    def delete_category(self, user_id=None, category_id=None):
        """Xóa category (soft delete - set is_active = False)"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or category_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        category = self.get_category_by_id(user_id, category_id)
        if not category:
            return False, "Không tìm thấy category hoặc không có quyền"

        # Kiểm tra quyền
        if not self.user_manager.is_admin(user_id) and category.get('user_id') != user_id:
            return False, "Không có quyền xóa category này"

        category['is_active'] = False

        if self.save_categories():
            return True, "Đã xóa category thành công"
        return False, "Lỗi khi lưu file"

    def restore_category(self, user_id=None, category_id=None):
        """Khôi phục category đã xóa"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or category_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        category = self.get_category_by_id(user_id, category_id)
        if not category:
            return False, "Không tìm thấy category hoặc không có quyền"

        # Kiểm tra quyền
        if not self.user_manager.is_admin(user_id) and category.get('user_id') != user_id:
            return False, "Không có quyền khôi phục category này"

        category['is_active'] = True

        if self.save_categories():
            return True, "Đã khôi phục category thành công"
        return False, "Lỗi khi lưu file"

    def get_category_by_name(self, user_id=None, name=None):
        """Tìm category theo tên trong phạm vi người dùng hoặc toàn cục"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or name is None:
            return None
            
        name = name.lower()
        for category in self.categories:
            if category['name'].lower() == name:
                # Nếu là admin, kiểm tra tất cả; nếu không, chỉ kiểm tra category của user_id hoặc chung
                if self.user_manager.is_admin(user_id) or category.get('user_id') in [user_id, None]:
                    return category
        return None

    def search_categories(self, user_id=None, keyword=None):
        """Tìm kiếm categories theo từ khóa"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or keyword is None:
            return []
            
        keyword = keyword.lower()
        result = []

        for category in self.get_all_categories(user_id):
            if (keyword in category['name'].lower() or 
                keyword in category.get('description', '').lower()):
                result.append(category)

        return result

    def get_category_stats(self, user_id=None):
        """Thống kê categories"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            return {
                'total': 0,
                'active': 0,
                'inactive': 0,
                'income_categories': 0,
                'expense_categories': 0
            }
            
        categories = self.get_all_categories(user_id)
        total = len(categories)
        active = len([cat for cat in categories if cat.get('is_active', True)])
        income_cats = len([cat for cat in categories if cat.get('type') == 'income'])
        expense_cats = len([cat for cat in categories if cat.get('type') == 'expense'])

        return {
            'total': total,
            'active': active,
            'inactive': total - active,
            'income_categories': income_cats,
            'expense_categories': expense_cats
        }

    def get_category_name(self, category_id=None):
        """Trả về tên category theo ID (hoặc 'Unknown' nếu không tìm thấy)"""
        if category_id is None:
            return "Unknown"
            
        for category in self.categories:
            if category.get('category_id') == category_id:
                return category.get('name', 'Unknown')
        return "Unknown"

    def get_user_categories(self, user_id, is_admin=False):
        """Get all categories for a user or all if admin"""
        if is_admin:
            return self.categories
        return [c for c in self.categories if c['user_id'] == user_id or c['user_id'] is None]