# report_manager.py

from datetime import datetime, timedelta
from collections import defaultdict
from utils.file_helper import get_current_datetime, save_json, validate_date_format
from data_manager.transaction_manager import TransactionManager
from data_manager.budget_manager import BudgetManager
from data_manager.category_manager import CategoryManager
from data_manager.user_manager import UserManager

class ReportManager:
    def __init__(self):
        self.transaction_manager = TransactionManager()
        self.budget_manager = BudgetManager()
        self.category_manager = CategoryManager()
        self.user_manager = UserManager()

    def get_financial_summary(self, user_id, start_date=None, end_date=None):
        """
        Tạo báo cáo tóm tắt tài chính cho một người dùng trong một khoảng thời gian.
        Bao gồm tổng thu nhập, tổng chi tiêu, và số dư.
        """
        transactions = self.transaction_manager.get_transactions_by_date_range(user_id, start_date, end_date)
        
        total_income = sum(txn['amount'] for txn in transactions if txn['type'] == 'income')
        total_expense = sum(txn['amount'] for txn in transactions if txn['type'] == 'expense')
        balance = total_income - total_expense

        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'start_date': start_date,
            'end_date': end_date
        }

    def get_category_report(self, user_id, report_type='expense', start_date=None, end_date=None):
        """
        Tạo báo cáo chi tiêu hoặc thu nhập theo danh mục.
        report_type: 'income' hoặc 'expense'.
        """
        if report_type not in ['income', 'expense']:
            raise ValueError("report_type phải là 'income' hoặc 'expense'.")

        transactions = self.transaction_manager.get_transactions_by_date_range(user_id, start_date, end_date)
        category_breakdown = defaultdict(float)
        
        for txn in transactions:
            if txn['type'] == report_type:
                category_name = self.category_manager.get_category_name(txn['category_id'])
                category_breakdown[category_name] += txn['amount']
        
        sorted_breakdown = sorted(category_breakdown.items(), key=lambda item: item[1], reverse=True)
        return {
            'report_type': report_type,
            'breakdown': dict(sorted_breakdown),
            'start_date': start_date,
            'end_date': end_date
        }

    def get_budget_vs_actual_report(self, user_id, month=None, year=None):
        """
        Tạo báo cáo so sánh ngân sách và chi tiêu thực tế cho một tháng/năm cụ thể.
        Nếu month và year là None, sẽ lấy tháng hiện tại.
        """
        if not month:
            month = datetime.now().month
        if not year:
            year = datetime.now().year

        # Get monthly summary of transactions
        transaction_summary = self.transaction_manager.get_monthly_summary(user_id, year, month)
        actual_expenses_by_category = transaction_summary['expense_breakdown']

        # Get active budgets for the user
        budgets = self.budget_manager.get_all_budgets(user_id, active_only=True)
        
        report_data = []
        for budget in budgets:
            category_name = self.category_manager.get_category_name(budget['category_id'])
            budgeted_amount = budget['amount']
            
            # Find actual spending for this budget's category in the current month
            actual_spent = actual_expenses_by_category.get(category_name, 0)
            
            remaining = budgeted_amount - actual_spent
            
            report_data.append({
                'budget_name': budget['name'],
                'category_name': category_name,
                'budgeted_amount': budgeted_amount,
                'actual_spent': actual_spent,
                'remaining': remaining,
                'status': 'over budget' if actual_spent > budgeted_amount else 'within budget'
            })
        
        return {
            'month': month,
            'year': year,
            'budget_vs_actual': report_data
        }

    def get_transaction_trend_report(self, user_id, period='monthly', num_periods=6):
        """
        Tạo báo cáo xu hướng giao dịch (thu nhập/chi tiêu) theo tháng hoặc năm.
        period: 'monthly' hoặc 'yearly'.
        num_periods: Số lượng tháng/năm gần nhất để báo cáo.
        """
        today = datetime.now()
        trends = defaultdict(lambda: {'income': 0, 'expense': 0})

        for i in range(num_periods):
            if period == 'monthly':
                target_month = today.month - i
                target_year = today.year
                while target_month <= 0:
                    target_month += 12
                    target_year -= 1
                
                start_date = datetime(target_year, target_month, 1).strftime('%Y-%m-%d')
                end_date = (datetime(target_year, target_month % 12 + 1, 1) - timedelta(days=1)).strftime('%Y-%m-%d') if target_month != 12 else datetime(target_year, 12, 31).strftime('%Y-%m-%d')
                label = f"{target_month:02d}/{target_year}"
            elif period == 'yearly':
                target_year = today.year - i
                start_date = datetime(target_year, 1, 1).strftime('%Y-%m-%d')
                end_date = datetime(target_year, 12, 31).strftime('%Y-%m-%d')
                label = str(target_year)
            else:
                raise ValueError("Period phải là 'monthly' hoặc 'yearly'.")

            summary = self.get_financial_summary(user_id, start_date, end_date)
            trends[label]['income'] = summary['total_income']
            trends[label]['expense'] = summary['total_expense']
        
        # Sort trends by date (oldest to newest)
        if period == 'monthly':
            sorted_trends = sorted(trends.items(), key=lambda item: datetime.strptime(item[0], '%m/%Y'))
        else: # yearly
            sorted_trends = sorted(trends.items(), key=lambda item: int(item[0]))

        return {
            'period': period,
            'num_periods': num_periods,
            'trends': dict(sorted_trends)
        }

    def export_report(self, user_id, report_type, file_format='json', **kwargs):
        """
        Xuất báo cáo ra file.
        report_type: 'summary', 'category', 'budget_vs_actual', 'trend'.
        file_format: 'json' (có thể mở rộng sang csv, pdf trong tương lai).
        """
        report_data = {}
        if report_type == 'summary':
            report_data = self.get_financial_summary(user_id, **kwargs)
        elif report_type == 'category':
            report_data = self.get_category_report(user_id, **kwargs)
        elif report_type == 'budget_vs_actual':
            report_data = self.get_budget_vs_actual_report(user_id, **kwargs)
        elif report_type == 'trend':
            report_data = self.get_transaction_trend_report(user_id, **kwargs)
        else:
            return False, "Loại báo cáo không hợp lệ."

        if file_format == 'json':
            file_name = f"reports/{report_type}_report_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            if save_json(file_name, report_data):
                return True, f"Báo cáo đã được xuất thành công tới {file_name}"
            return False, "Lỗi khi lưu báo cáo."
        else:
            return False, "Định dạng file không được hỗ trợ."