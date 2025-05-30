# budget_manager.py

from finance_app.utils.file_helper import load_json, save_json, generate_id, get_current_datetime, validate_date_format
from datetime import datetime, timedelta
import calendar
from finance_app.data_manager.user_manager import UserManager
from finance_app.data_manager.category_manager import CategoryManager

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
        self.budgets = None # Defer loading
        self.history = None # Defer loading
        self.user_manager = UserManager()
        self.category_manager = CategoryManager()
        self.current_user_id = None

    def _load_data_if_needed(self):
        if self.budgets is None:
            self.budgets = self.load_budgets_internal()
        if self.history is None:
            self.history = self.load_history_internal()

    def set_current_user(self, user_id):
        """Thiết lập người dùng hiện tại
        Args:
            user_id (str): ID của người dùng
        """
        self.current_user_id = user_id
        self.category_manager.set_current_user(user_id)

    def load_budgets_internal(self):
        """Tải danh sách budgets từ file, thêm auto_renew nếu thiếu"""
        budgets = load_json(self.budget_file)
        for budget in budgets:
            if 'auto_renew' not in budget:
                budget['auto_renew'] = True  # Mặc định gia hạn tự động
        return budgets
    
    def load_history_internal(self):
        """Tải lịch sử thay đổi budgets từ file"""
        return load_json(self.history_file)
    
    def save_budgets(self, budgets=None):
        """Lưu danh sách budgets vào file"""
        if budgets is None:
            budgets = self.budgets
        return save_json(self.budget_file, budgets)

    def save_history(self, history=None):
        """Lưu lịch sử thay đổi vào file"""
        self._load_data_if_needed() # Ensure history is loaded before saving
        if history is None:
            history = self.history
        return save_json(self.history_file, history)

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
            
        self._load_data_if_needed() # Load data if not already loaded
        
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
    
    def get_user_budgets(self, user_id, period=None):
        """Get all budgets for a user with optional period filter
        
        Args:
            user_id (str): User ID to get budgets for
            period (str, optional): Period filter ('tháng này', 'quý này', 'năm nay')
            
        Returns:
            list: List of budget dictionaries
        """
        self._load_data_if_needed() # Load data if not already loaded
        budgets = [b for b in self.budgets if b['user_id'] == user_id]
        
        if not period:
            return budgets
            
        today = datetime.now()
        start_date = None
        end_date = None
        
        # Convert period to lowercase for comparison
        period = period.lower()
        
        if period == 'tháng này':
            # Current month
            start_date = datetime(today.year, today.month, 1)
            end_date = datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        elif period == 'quý này':
            # Current quarter
            quarter = (today.month - 1) // 3
            start_date = datetime(today.year, quarter * 3 + 1, 1)
            end_month = (quarter + 1) * 3
            if end_month > 12:
                end_month = 12
            end_date = datetime(today.year, end_month, calendar.monthrange(today.year, end_month)[1])
        elif period == 'năm nay':
            # Current year
            start_date = datetime(today.year, 1, 1)
            end_date = datetime(today.year, 12, 31)
            
        if start_date and end_date:
            filtered_budgets = []
            for budget in budgets:
                budget_start = datetime.strptime(budget['start_date'], '%Y-%m-%d')
                if budget.get('end_date'):
                    budget_end = datetime.strptime(budget['end_date'], '%Y-%m-%d')
                else:
                    budget_end = end_date
                    
                # Check if budget period overlaps with filter period
                if (budget_start <= end_date and budget_end >= start_date):
                    filtered_budgets.append(budget)
            return filtered_budgets
            
        return budgets
    
    def get_user_budgets_by_date_range(self, user_id, start_date_str=None, end_date_str=None):
        """Get all budgets for a user that overlap with the given date range.

        Args:
            user_id (str): User ID to get budgets for.
            start_date_str (str, optional): Start date of the filter range (YYYY-MM-DD).
            end_date_str (str, optional): End date of the filter range (YYYY-MM-DD).
            
        Returns:
            list: List of budget dictionaries.
        """
        self._load_data_if_needed()
        user_budgets = [b for b in self.budgets if b['user_id'] == user_id and b.get('is_active', True)]

        if not start_date_str or not end_date_str:
            # If no date range is provided, return all active user budgets
            # or consider returning budgets for the current month/default period.
            # For now, returning all active if no specific range.
            return user_budgets

        try:
            filter_start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            filter_end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            # Invalid date format, return empty or all, or raise error
            # For now, returning all active budgets of the user if date parsing fails.
            # Consider logging this error.
            return user_budgets

        filtered_budgets = []
        for budget in user_budgets:
            try:
                budget_start_date = datetime.strptime(budget['start_date'], '%Y-%m-%d')
                # Budgets might not have an end_date if they are continuous or based on period only
                # For simplicity, if end_date is missing or empty, we might need a rule.
                # Assuming if budget has no end_date, it's ongoing.
                # If budget has an end_date, use it for comparison.
                budget_end_date_str = budget.get('end_date')
                if budget_end_date_str:
                    budget_end_date = datetime.strptime(budget_end_date_str, '%Y-%m-%d')
                else:
                    # If a budget has no end_date, how does it interact with a filter_end_date?
                    # Option 1: Assume it's ongoing indefinitely beyond filter_end_date if budget_start_date <= filter_end_date
                    # Option 2: If budget is e.g. monthly and filter is for a specific month, it should match.
                    # The original get_user_budgets had logic for 'monthly', 'quarterly', etc.
                    # This date range filter is more generic.
                    # For now, let's assume a budget without an end_date is active until the filter_end_date if it started before/during the filter period.
                    # This might need more sophisticated handling based on budget.period if available.
                    budget_end_date = filter_end_date # Effectively, consider it active for the purpose of the filter period if it started.

                # Check for overlap: (StartA <= EndB) and (EndA >= StartB)
                if budget_start_date <= filter_end_date and budget_end_date >= filter_start_date:
                    filtered_budgets.append(budget)
            except ValueError:
                # Skip budget if its dates are malformed, or log an error
                continue
        
        return filtered_budgets
    
    def get_budget_by_id(self, user_id, budget_id, is_admin=False):
        """Get a budget by id, check permission"""
        self._load_data_if_needed() # Load data if not already loaded
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
        self._load_data_if_needed() # Load data if not already loaded
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
        self._load_data_if_needed() # Load data if not already loaded
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
        """Cập nhật số tiền đã chi cho budget"""
        self._load_data_if_needed() # Load data if not already loaded
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
        """Thêm giao dịch vào budget và cập nhật spent_amount"""
        self._load_data_if_needed() # Load data if not already loaded
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or budget_id is None or transaction_amount is None:
            return False, "Thiếu thông tin bắt buộc"
            
        budget = self.get_budget_by_id(user_id, budget_id)
        
        new_spent = budget['spent_amount'] + transaction_amount
        return self.update_spent_amount(user_id, budget_id, new_spent)
    
    def delete_budget(self, user_id=None, budget_id=None):
        """Xóa budget và lịch sử liên quan"""
        self._load_data_if_needed() # Load data if not already loaded
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or budget_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        budget = self.get_budget_by_id(user_id, budget_id)
        if not budget:
            return False, "Không tìm thấy budget"
        
        budget['is_active'] = False
        budget['updated_at'] = get_current_datetime()
        
        if self.save_budgets():
            return True, "Đã xóa budget thành công"
        return False, "Lỗi khi lưu file"
    
    def get_budget_alerts(self, user_id=None, target_user_id=None):
        """
        Lấy cảnh báo budget
        """
        self._load_data_if_needed() # Load data if not already loaded
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
        """Thêm một bản ghi vào lịch sử thay đổi budgets"""
        self._load_data_if_needed() # Load data if not already loaded
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
        """
        Lấy lịch sử thay đổi của một budget
        """
        self._load_data_if_needed() # Load data if not already loaded
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or budget_id is None:
            return []
            
        budget = self.get_budget_by_id(user_id, budget_id)
        return [h for h in self.history if h['budget_id'] == budget_id]
    
    def get_budget_summary(self, user_id, is_admin=False):
        """
        Lấy tóm tắt tình hình budget của người dùng
        """
        self._load_data_if_needed() # Load data if not already loaded
        if not user_id:
            return {}
        
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
        """Tự động gia hạn các budgets hàng tháng nếu cần"""
        self._load_data_if_needed() # Load data if not already loaded
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
        """Xóa tất cả budgets và lịch sử liên quan của một người dùng"""
        self._load_data_if_needed() # Load data if not already loaded
        if not user_id:
            return False, "Thiếu thông tin người dùng"
        
        self.budgets = [b for b in self.budgets if b['user_id'] != user_id]
        self.history = [h for h in self.history if h['user_id'] != user_id]
        
        if self.save_budgets() and self.save_history():
            print(f"Đã xóa tất cả ngân sách của người dùng: {user_id}")
            return True, "Đã xóa tất cả ngân sách thành công"
        return False, "Lỗi khi lưu file"