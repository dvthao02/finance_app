# budget_manager.py

from utils.file_helper import load_json, save_json, generate_id, get_current_datetime, validate_date_format
from datetime import datetime, timedelta
import calendar
from data_manager.user_manager import UserManager
from data_manager.category_manager import CategoryManager

class BudgetManager:
    def __init__(self, budget_file='budgets.json', history_file='budget_change_history.json'):
        import os
        # Get the directory where the package is installed
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(package_dir, 'data')
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        self.budget_file = os.path.join(data_dir, budget_file)
        self.history_file = os.path.join(data_dir, history_file)
        self.budgets = self.load_budgets()
        self.history = self.load_history()
        self.user_manager = UserManager()
        self.category_manager = CategoryManager()
        self.current_user_id = None

    def set_current_user(self, user_id):
        """Thiết lập người dùng hiện tại
        Args:
            user_id (str): ID của người dùng
        """
        self.current_user_id = user_id
        self.category_manager.set_current_user(user_id)

    def load_budgets(self):
        """Tải danh sách budgets từ file, thêm auto_renew nếu thiếu"""
        budgets = load_json(self.budget_file)
        for budget in budgets:
            if 'auto_renew' not in budget:
                budget['auto_renew'] = True  # Mặc định gia hạn tự động
        return budgets
    
    def load_history(self):
        """Tải lịch sử thay đổi budgets từ file"""
        return load_json(self.history_file)
    
    def save_budgets(self):
        """Lưu danh sách budgets vào file"""
        return save_json(self.budget_file, self.budgets)
    
    def save_history(self):
        """Lưu lịch sử thay đổi vào file"""
        return save_json(self.history_file, self.history)
    
    def get_all_budgets(self, user_id=None, target_user_id=None, active_only=True):
        """
        Lấy tất cả budgets
        Args:
            user_id: ID người dùng thực hiện yêu cầu (None để sử dụng current_user_id)
            target_user_id: ID người dùng cần lấy dữ liệu (None để lấy tất cả nếu là admin)
            active_only: True để chỉ lấy budgets đang hoạt động
        """
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            return []
            
        if target_user_id and target_user_id != user_id and not self.user_manager.is_admin(user_id):
            raise ValueError("Không có quyền truy cập dữ liệu của người dùng khác")
        
        result = self.budgets.copy()
        
        if target_user_id:
            result = [budget for budget in result if budget['user_id'] == target_user_id]
        else:
            result = [budget for budget in result if budget['user_id'] == user_id]
        
        if active_only:
            result = [budget for budget in result if budget.get('is_active', True)]
        
        return result
    
    def get_user_budgets(self, user_id, is_admin=False):
        """Get all budgets for a user or all if admin"""
        if is_admin:
            return self.budgets
        return [b for b in self.budgets if b['user_id'] == user_id]
    
    def get_budget_by_id(self, user_id, budget_id, is_admin=False):
        """Get a budget by id, check permission"""
        for b in self.budgets:
            if b['budget_id'] == budget_id:
                if is_admin or b['user_id'] == user_id:
                    return b
        return None
    
    def create_budget(self, user_id=None, category_id=None, amount=None, period='monthly', 
                     alert_threshold=80, notes='', start_date=None, end_date=None, auto_renew=True):
        """
        Tạo budget mới
        """
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or category_id is None or amount is None:
            return False, "Thiếu thông tin bắt buộc"
            
        if not self.user_manager.get_user_by_id(user_id):
            return False, f"Không tìm thấy người dùng với ID: {user_id}"
        
        category = self.category_manager.get_category_by_id(user_id, category_id)
        if not category or not category.get('is_active', True):
            return False, f"Không tìm thấy danh mục với ID: {category_id} hoặc danh mục không hoạt động"
        
        if amount <= 0:
            return False, "Số tiền ngân sách phải > 0"
        
        if not (0 <= alert_threshold <= 100):
            return False, "Ngưỡng cảnh báo phải từ 0-100%"
        
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        
        if not end_date and period == 'monthly':
            date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            last_day = calendar.monthrange(date_obj.year, date_obj.month)[1]
            end_date = f"{date_obj.year}-{date_obj.month:02d}-{last_day:02d}"
        
        if not validate_date_format(start_date) or (end_date and not validate_date_format(end_date)):
            return False, "Format ngày không hợp lệ (YYYY-MM-DD)"
        
        new_budget = {
            'budget_id': generate_id('budget', self.budgets),
            'user_id': user_id,
            'category_id': category_id,
            'amount': amount,
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'spent_amount': 0,
            'remaining_amount': amount,
            'alert_threshold': alert_threshold,
            'is_active': True,
            'created_at': get_current_datetime(),
            'updated_at': get_current_datetime(),
            'notes': notes,
            'auto_renew': auto_renew
        }
        
        self.budgets.append(new_budget)
        
        self.add_history(
            budget_id=new_budget['budget_id'],
            user_id=user_id,
            change_type='create',
            old_amount=None,
            new_amount=amount,
            old_alert_threshold=None,
            new_alert_threshold=alert_threshold,
            reason='Tạo ngân sách mới',
            changed_by=user_id
        )
        
        if self.save_budgets() and self.save_history():
            return True, new_budget
        return False, "Lỗi khi lưu file"
    
    def update_budget(self, user_id=None, budget_id=None, **kwargs):
        """
        Cập nhật budget
        """
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or budget_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        budget = self.get_budget_by_id(user_id, budget_id)
        if not budget:
            return False, "Không tìm thấy budget"
        
        old_amount = budget.get('amount')
        old_alert_threshold = budget.get('alert_threshold')
        
        allowed_fields = ['amount', 'alert_threshold', 'notes', 'start_date', 'end_date', 'is_active', 'auto_renew']
        updated_fields = []
        
        for field in allowed_fields:
            if field in kwargs:
                if field == 'amount' and kwargs[field] <= 0:
                    return False, "Số tiền ngân sách phải > 0"
                
                if field == 'alert_threshold' and not (0 <= kwargs[field] <= 100):
                    return False, "Ngưỡng cảnh báo phải từ 0-100%"
                
                if field in ['start_date', 'end_date'] and kwargs[field] and not validate_date_format(kwargs[field]):
                    return False, "Format ngày không hợp lệ (YYYY-MM-DD)"
                
                budget[field] = kwargs[field]
                updated_fields.append(field)
        
        budget['updated_at'] = get_current_datetime()
        
        if 'amount' in kwargs:
            budget['remaining_amount'] = kwargs['amount'] - budget['spent_amount']
        
        if 'amount' in kwargs or 'alert_threshold' in kwargs:
            reason = kwargs.get('reason', f"Cập nhật budget - {', '.join(updated_fields)}")
            self.add_history(
                budget_id=budget_id,
                user_id=user_id,
                change_type='update',
                old_amount=old_amount,
                new_amount=budget.get('amount'),
                old_alert_threshold=old_alert_threshold,
                new_alert_threshold=budget.get('alert_threshold'),
                reason=reason,
                changed_by=user_id
            )
        
        if self.save_budgets() and self.save_history():
            return True, budget
        return False, "Lỗi khi lưu file"
    
    def update_spent_amount(self, user_id=None, budget_id=None, spent_amount=None):
        """Cập nhật số tiền đã chi tiêu"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or budget_id is None or spent_amount is None:
            return False, "Thiếu thông tin bắt buộc"
            
        budget = self.get_budget_by_id(user_id, budget_id)
        
        budget['spent_amount'] = spent_amount
        budget['remaining_amount'] = budget['amount'] - spent_amount
        budget['updated_at'] = get_current_datetime()
        
        if self.save_budgets():
            return True, budget
        return False, "Lỗi khi lưu file"
    
    def add_transaction_to_budget(self, user_id=None, budget_id=None, transaction_amount=None):
        """Thêm giao dịch vào budget"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or budget_id is None or transaction_amount is None:
            return False, "Thiếu thông tin bắt buộc"
            
        budget = self.get_budget_by_id(user_id, budget_id)
        
        new_spent = budget['spent_amount'] + transaction_amount
        return self.update_spent_amount(user_id, budget_id, new_spent)
    
    def delete_budget(self, user_id=None, budget_id=None):
        """Xóa budget (soft delete)"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or budget_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        budget = self.get_budget_by_id(user_id, budget_id)
        
        budget['is_active'] = False
        budget['updated_at'] = get_current_datetime()
        
        if self.save_budgets():
            return True, "Đã xóa budget thành công"
        return False, "Lỗi khi lưu file"
    
    def get_budget_alerts(self, user_id=None, target_user_id=None):
        """Lấy cảnh báo ngân sách"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            return []
            
        budgets = self.get_all_budgets(user_id, target_user_id)
        alerts = []
        
        for budget in budgets:
            if budget['amount'] > 0:
                spent_percent = (budget['spent_amount'] / budget['amount']) * 100
                if spent_percent >= budget['alert_threshold']:
                    alerts.append({
                        'budget_id': budget['budget_id'],
                        'category_id': budget['category_id'],
                        'spent_percent': spent_percent,
                        'threshold': budget['alert_threshold'],
                        'amount': budget['amount'],
                        'spent_amount': budget['spent_amount'],
                        'remaining_amount': budget['remaining_amount']
                    })
                    
        return alerts
    
    def add_history(self, budget_id=None, user_id=None, change_type=None, old_amount=None, new_amount=None, 
                   old_alert_threshold=None, new_alert_threshold=None, reason=None, changed_by=None):
        """Thêm lịch sử thay đổi"""
        if None in [budget_id, user_id, change_type, reason, changed_by]:
            return False
            
        history_entry = {
            'history_id': generate_id('hist', self.history),
            'budget_id': budget_id,
            'user_id': user_id,
            'change_type': change_type,
            'old_amount': old_amount,
            'new_amount': new_amount,
            'old_alert_threshold': old_alert_threshold,
            'new_alert_threshold': new_alert_threshold,
            'reason': reason,
            'changed_by': changed_by,
            'changed_at': get_current_datetime()
        }
        
        self.history.append(history_entry)
        return True
    
    def get_budget_history(self, user_id=None, budget_id=None):
        """Lấy lịch sử thay đổi của một budget"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or budget_id is None:
            return []
            
        budget = self.get_budget_by_id(user_id, budget_id)
        return [h for h in self.history if h['budget_id'] == budget_id]
    
    def get_budget_summary(self, user_id, is_admin=False):
        """Get budget summary for user or all if admin"""
        budgets = self.get_user_budgets(user_id, is_admin)
        active_budgets = [b for b in budgets if b.get('is_active', True)]
        total_amount = sum(b['amount'] for b in active_budgets)
        total_spent = sum(b['spent_amount'] for b in active_budgets)
        over_budget = len([b for b in active_budgets if b['spent_amount'] > b['amount']])
        return {
            'total_budgets': len(budgets),
            'active_budgets': len(active_budgets),
            'total_amount': total_amount,
            'total_spent': total_spent,
            'total_remaining': total_amount - total_spent,
            'over_budget_count': over_budget,
            'budgets': active_budgets
        }
    
    def renew_monthly_budgets(self):
        """Gia hạn tự động các budget hàng tháng"""
        today = datetime.now()
        first_day = today.replace(day=1).strftime('%Y-%m-%d')
        last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1]).strftime('%Y-%m-%d')
        
        for budget in self.budgets:
            if (budget.get('is_active') and budget.get('auto_renew') and 
                budget.get('period') == 'monthly' and 
                budget.get('end_date') < first_day):
                
                # Tạo budget mới cho tháng hiện tại
                self.create_budget(
                    user_id=budget['user_id'],
                    category_id=budget['category_id'],
                    amount=budget['amount'],
                    period='monthly',
                    alert_threshold=budget['alert_threshold'],
                    notes=budget['notes'],
                    start_date=first_day,
                    end_date=last_day,
                    auto_renew=True
                )
    
    def delete_user_budgets(self, user_id):
        """Delete all budgets for a user
        
        Args:
            user_id (str): ID of the user whose budgets should be deleted
        """
        if not user_id:
            return
        
        budgets = self.load_budgets()
        budgets = [b for b in budgets if b['user_id'] != user_id]
        self.save_budgets(budgets)
        
        # Also delete budget change history
        history = self.load_budget_history()
        history = [h for h in history if h['user_id'] != user_id]
        self.save_budget_history(history)
        
        print(f"Đã xóa tất cả ngân sách của người dùng: {user_id}")
        return True