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
    
    def get_all_budgets(self, user_id, target_user_id=None, active_only=True):
        """
        Lấy tất cả budgets
        Args:
            user_id: ID người dùng thực hiện yêu cầu
            target_user_id: ID người dùng cần lấy dữ liệu (None để lấy tất cả nếu là admin)
            active_only: True để chỉ lấy budgets đang hoạt động
        """
        if target_user_id and target_user_id != user_id and not self.user_manager.is_admin(user_id):
            raise ValueError("Không có quyền truy cập dữ liệu của người dùng khác")
        
        result = self.budgets.copy()
        
        if target_user_id:
            result = [budget for budget in result if budget['user_id'] == target_user_id]
        
        if active_only:
            result = [budget for budget in result if budget.get('is_active', True)]
        
        return result
    
    def get_budget_by_id(self, user_id, budget_id):
        """Lấy budget theo ID"""
        budget = None
        for b in self.budgets:
            if b['budget_id'] == budget_id:
                budget = b
                break
        if not budget:
            raise ValueError(f"Không tìm thấy budget với ID: {budget_id}")
        if budget['user_id'] != user_id and not self.user_manager.is_admin(user_id):
            raise ValueError("Không có quyền truy cập budget này")
        return budget
    
    def create_budget(self, user_id, category_id, amount, period='monthly', 
                     alert_threshold=80, notes='', start_date=None, end_date=None, auto_renew=True):
        """
        Tạo budget mới
        """
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
    
    def update_budget(self, user_id, budget_id, **kwargs):
        """
        Cập nhật budget
        """
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
    
    def update_spent_amount(self, user_id, budget_id, spent_amount):
        """Cập nhật số tiền đã chi tiêu"""
        budget = self.get_budget_by_id(user_id, budget_id)
        
        budget['spent_amount'] = spent_amount
        budget['remaining_amount'] = budget['amount'] - spent_amount
        budget['updated_at'] = get_current_datetime()
        
        return self.save_budgets()
    
    def add_transaction_to_budget(self, user_id, budget_id, transaction_amount):
        """Thêm giao dịch vào budget (tăng spent_amount)"""
        budget = self.get_budget_by_id(user_id, budget_id)
        
        budget['spent_amount'] += abs(transaction_amount)
        budget['remaining_amount'] = budget['amount'] - budget['spent_amount']
        budget['updated_at'] = get_current_datetime()
        
        return self.save_budgets()
    
    def delete_budget(self, user_id, budget_id):
        """Xóa budget (soft delete)"""
        budget = self.get_budget_by_id(user_id, budget_id)
        
        budget['is_active'] = False
        budget['updated_at'] = get_current_datetime()
        
        if self.save_budgets():
            return True, "Đã xóa budget thành công"
        return False, "Lỗi khi lưu file"
    
    def get_budgets_by_user(self, user_id, active_only=True):
        """Lấy tất cả budgets của user"""
        return self.get_all_budgets(user_id, user_id, active_only)
    
    def get_budget_alerts(self, user_id, target_user_id=None):
        """Lấy danh sách budgets cần cảnh báo"""
        budgets = self.get_all_budgets(user_id, target_user_id, active_only=True)
        alerts = []
        
        for budget in budgets:
            spent_percentage = (budget['spent_amount'] / budget['amount']) * 100 if budget['amount'] > 0 else 0
            if spent_percentage >= budget['alert_threshold']:
                alerts.append({
                    'budget': budget,
                    'spent_percentage': round(spent_percentage, 1),
                    'over_budget': spent_percentage > 100
                })
        
        return alerts
    
    def add_history(self, budget_id, user_id, change_type, old_amount, new_amount, 
                   old_alert_threshold, new_alert_threshold, reason, changed_by):
        """Thêm lịch sử thay đổi budget"""
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
            'changed_at': get_current_datetime(),
            'changed_by': changed_by
        }
        
        self.history.append(history_entry)
    
    def get_budget_history(self, user_id, budget_id):
        """Lấy lịch sử thay đổi của một budget"""
        budget = self.get_budget_by_id(user_id, budget_id)
        return [hist for hist in self.history if hist['budget_id'] == budget_id]
    
    def get_budget_summary(self, user_id):
        """Tổng hợp thông tin budgets của user"""
        budgets = self.get_budgets_by_user(user_id)
        
        total_budgets = len(budgets)
        total_amount = sum(budget['amount'] for budget in budgets)
        total_spent = sum(budget['spent_amount'] for budget in budgets)
        total_remaining = sum(budget['remaining_amount'] for budget in budgets)
        
        alerts = self.get_budget_alerts(user_id)
        over_budget_count = len([alert for alert in alerts if alert['over_budget']])
        
        return {
            'total_budgets': total_budgets,
            'total_amount': total_amount,
            'total_spent': total_spent,
            'total_remaining': total_remaining,
            'alerts_count': len(alerts),
            'over_budget_count': over_budget_count,
            'spent_percentage': round((total_spent / total_amount) * 100, 1) if total_amount > 0 else 0
        }
    
    def renew_monthly_budgets(self):
        """Gia hạn ngân sách hàng tháng: reset spent_amount và tạo ngân sách mới cho tháng tiếp theo"""
        today = datetime.now()
        updated = False
        new_budgets = []
        
        for budget in self.budgets:
            if (budget.get('is_active', True) and budget.get('period') == 'monthly' and 
                budget.get('auto_renew', True)):
                end_date = datetime.strptime(budget['end_date'], '%Y-%m-%d')
                if end_date < today:
                    budget['is_active'] = False
                    budget['updated_at'] = get_current_datetime()
                    updated = True
                    
                    next_month = end_date.replace(day=1) + timedelta(days=32)
                    next_month = next_month.replace(day=1)
                    last_day = calendar.monthrange(next_month.year, next_month.month)[1]
                    
                    new_budget = {
                        'budget_id': generate_id('budget', self.budgets + new_budgets),
                        'user_id': budget['user_id'],
                        'category_id': budget['category_id'],
                        'amount': budget['amount'],
                        'period': 'monthly',
                        'start_date': next_month.strftime('%Y-%m-%d'),
                        'end_date': f"{next_month.year}-{next_month.month:02d}-{last_day:02d}",
                        'spent_amount': 0,
                        'remaining_amount': budget['amount'],
                        'alert_threshold': budget['alert_threshold'],
                        'is_active': True,
                        'created_at': get_current_datetime(),
                        'updated_at': get_current_datetime(),
                        'notes': budget['notes'],
                        'auto_renew': budget['auto_renew']
                    }
                    
                    new_budgets.append(new_budget)
                    
                    self.add_history(
                        budget_id=new_budget['budget_id'],
                        user_id=budget['user_id'],
                        change_type='create',
                        old_amount=None,
                        new_amount=budget['amount'],
                        old_alert_threshold=None,
                        new_alert_threshold=budget['alert_threshold'],
                        reason='Gia hạn ngân sách hàng tháng',
                        changed_by=budget['user_id']
                    )
        
        if new_budgets:
            self.budgets.extend(new_budgets)
            updated = True
        
        if updated and self.save_budgets() and self.save_history():
            return True, f"Đã gia hạn {len(new_budgets)} ngân sách"
        return False, "Không có ngân sách nào được gia hạn"