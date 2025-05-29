# transaction_manager.py

from datetime import datetime, timedelta
from utils.file_helper import load_json, save_json, generate_id, get_current_datetime, validate_date_format
from data_manager.category_manager import CategoryManager
from data_manager.user_manager import UserManager

class TransactionManager:
    def __init__(self, transaction_file='transactions.json'):
        import os
        # Get the directory where the package is installed
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(package_dir, 'data')
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        self.transaction_file = os.path.join(data_dir, transaction_file)
        self.category_manager = CategoryManager()
        self.user_manager = UserManager()

    def load_transactions(self):
        """Tải danh sách giao dịch từ file"""
        return load_json(self.transaction_file)

    def save_transactions(self, transactions):
        """Lưu danh sách giao dịch vào file"""
        return save_json(self.transaction_file, transactions)

    def get_all_transactions(self, user_id, target_user_id=None):
        """Lấy tất cả giao dịch, có thể lọc theo user_id"""
        if target_user_id and target_user_id != user_id and not self.user_manager.is_admin(user_id):
            raise ValueError("Không có quyền truy cập dữ liệu của người dùng khác")
        
        transactions = self.load_transactions()
        if target_user_id:
            return [txn for txn in transactions if txn['user_id'] == target_user_id]
        return transactions

    def get_transaction_by_id(self, user_id, transaction_id):
        """Tìm giao dịch theo ID"""
        transaction = self.get_transaction_by_id_no_auth(transaction_id)
        if not transaction:
            raise ValueError(f"Không tìm thấy giao dịch với ID: {transaction_id}")
        if transaction['user_id'] != user_id and not self.user_manager.is_admin(user_id):
            raise ValueError("Không có quyền truy cập giao dịch này")
        return transaction

    def get_transaction_by_id_no_auth(self, transaction_id):
        """Tìm giao dịch theo ID mà không kiểm tra quyền"""
        transactions = self.load_transactions()
        for transaction in transactions:
            if transaction['transaction_id'] == transaction_id:
                return transaction
        return None

    def add_transaction(self, user_id, category_id, amount, transaction_type, description="", 
                       date=None, tags=None, location=""):
        """Thêm giao dịch mới"""
        # Kiểm tra user_id
        if not self.user_manager.get_user_by_id(user_id):
            raise ValueError(f"Không tìm thấy người dùng với ID: {user_id}")
        
        # Kiểm tra category_id
        category = self.category_manager.get_category_by_id(user_id, category_id)
        if not category:
            raise ValueError(f"Không tìm thấy danh mục với ID: {category_id} hoặc không có quyền")
        
        # Kiểm tra type phù hợp với category
        if category['type'] != transaction_type:
            raise ValueError(f"Loại giao dịch không phù hợp với danh mục")
        
        # Kiểm tra amount > 0
        if amount <= 0:
            raise ValueError("Số tiền phải lớn hơn 0")
        
        # Kiểm tra type hợp lệ
        if transaction_type not in ['income', 'expense']:
            raise ValueError("Loại giao dịch phải là 'income' hoặc 'expense'")
        
        # Xử lý ngày
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        if not validate_date_format(date):
            raise ValueError("Ngày giao dịch không đúng định dạng YYYY-MM-DD")
        
        # Xử lý tags
        if tags is None:
            tags = []
        
        transactions = self.load_transactions()
        new_transaction = {
            "transaction_id": generate_id("txn", transactions),
            "user_id": user_id,
            "category_id": category_id,
            "amount": amount,
            "type": transaction_type,
            "description": description,
            "date": date,
            "created_at": get_current_datetime(),
            "updated_at": get_current_datetime(),
            "tags": tags,
            "location": location
        }
        
        transactions.append(new_transaction)
        self.save_transactions(transactions)
        print(f"Đã thêm giao dịch mới: {new_transaction['transaction_id']}")
        return new_transaction['transaction_id']

    def update_transaction(self, user_id, transaction_id, **kwargs):
        """Cập nhật giao dịch"""
        transaction = self.get_transaction_by_id(user_id, transaction_id)
        
        transactions = self.load_transactions()
        for idx, txn in enumerate(transactions):
            if txn['transaction_id'] == transaction_id:
                for key, value in kwargs.items():
                    if key in txn and value is not None:
                        if key == 'category_id':
                            category = self.category_manager.get_category_by_id(user_id, value)
                            if not category:
                                raise ValueError(f"Không tìm thấy danh mục với ID: {value} hoặc không có quyền")
                            if category['type'] != txn['type']:
                                raise ValueError(f"Loại giao dịch không phù hợp với danh mục")
                        elif key == 'amount' and value <= 0:
                            raise ValueError("Số tiền phải lớn hơn 0")
                        elif key == 'type' and value not in ['income', 'expense']:
                            raise ValueError("Loại giao dịch phải là 'income' hoặc 'expense'")
                        elif key == 'date' and not validate_date_format(value):
                            raise ValueError("Ngày giao dịch không đúng định dạng YYYY-MM-DD")
                        
                        txn[key] = value
                
                txn['updated_at'] = get_current_datetime()
                transactions[idx] = txn
                self.save_transactions(transactions)
                print(f"Đã cập nhật giao dịch: {transaction_id}")
                return txn
        
        raise ValueError(f"Không tìm thấy giao dịch với ID: {transaction_id}")

    def delete_transaction(self, user_id, transaction_id):
        """Xóa giao dịch"""
        transaction = self.get_transaction_by_id(user_id, transaction_id)
        
        transactions = self.load_transactions()
        for i, txn in enumerate(transactions):
            if txn['transaction_id'] == transaction_id:
                del transactions[i]
                self.save_transactions(transactions)
                print(f"Đã xóa giao dịch: {transaction_id}")
                return True
        
        raise ValueError(f"Không tìm thấy giao dịch với ID: {transaction_id}")

    def get_transactions_by_date_range(self, user_id, start_date, end_date):
        """Lấy giao dịch trong khoảng thời gian"""
        transactions = self.get_all_transactions(user_id, user_id)
        
        if not validate_date_format(start_date) or not validate_date_format(end_date):
            raise ValueError("Ngày không đúng định dạng YYYY-MM-DD")
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        filtered_transactions = []
        for txn in transactions:
            txn_date = datetime.strptime(txn['date'], '%Y-%m-%d')
            if start_date <= txn_date <= end_date:
                filtered_transactions.append(txn)
        
        return filtered_transactions

    def get_transactions_by_category(self, user_id, category_id, start_date=None, end_date=None):
        """Lấy giao dịch theo danh mục"""
        category = self.category_manager.get_category_by_id(user_id, category_id)
        if not category:
            raise ValueError(f"Không tìm thấy danh mục với ID: {category_id} hoặc không có quyền")
        
        transactions = self.get_all_transactions(user_id, user_id)
        filtered = [txn for txn in transactions if txn['category_id'] == category_id]
        
        if start_date and end_date:
            if not validate_date_format(start_date) or not validate_date_format(end_date):
                raise ValueError("Ngày không đúng định dạng YYYY-MM-DD")
            filtered = [txn for txn in filtered 
                       if datetime.strptime(start_date, '%Y-%m-%d') <= datetime.strptime(txn['date'], '%Y-%m-%d') <= datetime.strptime(end_date, '%Y-%m-%d')]
        
        return filtered

    def search_transactions(self, user_id, keyword, transaction_type=None, category_id=None):
        """Tìm kiếm giao dịch theo từ khóa"""
        transactions = self.get_all_transactions(user_id, user_id)
        keyword = keyword.lower()
        results = []
        
        for txn in transactions:
            if (keyword in txn['description'].lower() or 
                keyword in txn['location'].lower() or
                any(keyword in tag.lower() for tag in txn.get('tags', []))):
                
                if transaction_type and txn['type'] != transaction_type:
                    continue
                
                if category_id:
                    category = self.category_manager.get_category_by_id(user_id, category_id)
                    if not category or txn['category_id'] != category_id:
                        continue
                
                results.append(txn)
        
        return results

    def get_transaction_summary(self, user_id, start_date=None, end_date=None):
        """Thống kê tổng quan giao dịch"""
        if start_date and end_date:
            transactions = self.get_transactions_by_date_range(user_id, start_date, end_date)
        else:
            transactions = self.get_all_transactions(user_id, user_id)
        
        total_income = sum(txn['amount'] for txn in transactions if txn['type'] == 'income')
        total_expense = sum(txn['amount'] for txn in transactions if txn['type'] == 'expense')
        
        summary = {
            'total_transactions': len(transactions),
            'total_income': total_income,
            'total_expense': total_expense,
            'net_amount': total_income - total_expense,
            'income_count': len([txn for txn in transactions if txn['type'] == 'income']),
            'expense_count': len([txn for txn in transactions if txn['type'] == 'expense'])
        }
        
        return summary

    def get_category_breakdown(self, user_id, transaction_type, start_date=None, end_date=None):
        """Phân tích theo danh mục"""
        if start_date and end_date:
            transactions = self.get_transactions_by_date_range(user_id, start_date, end_date)
        else:
            transactions = self.get_all_transactions(user_id, user_id)
        
        transactions = [txn for txn in transactions if txn['type'] == transaction_type]
        
        category_data = {}
        for txn in transactions:
            category_id = txn['category_id']
            if category_id not in category_data:
                category = self.category_manager.get_category_by_id(user_id, category_id)
                category_data[category_id] = {
                    'category_name': category['name'] if category else 'Unknown',
                    'total_amount': 0,
                    'transaction_count': 0,
                    'transactions': []
                }
            
            category_data[category_id]['total_amount'] += txn['amount']
            category_data[category_id]['transaction_count'] += 1
            category_data[category_id]['transactions'].append(txn)
        
        return category_data

    def get_monthly_report(self, user_id, year, month):
        """Báo cáo tháng"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        transactions = self.get_transactions_by_date_range(user_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        summary = self.get_transaction_summary(user_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        income_breakdown = self.get_category_breakdown(user_id, 'income', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        expense_breakdown = self.get_category_breakdown(user_id, 'expense', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        return {
            'month': month,
            'year': year,
            'summary': summary,
            'income_breakdown': income_breakdown,
            'expense_breakdown': expense_breakdown,
            'transactions': transactions
        }

    def export_transactions(self, user_id, file_path=None, start_date=None, end_date=None):
        """Xuất giao dịch ra file"""
        if file_path is None:
            file_path = f"transactions_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        transactions = self.get_all_transactions(user_id, user_id)
        
        if start_date and end_date:
            transactions = self.get_transactions_by_date_range(user_id, start_date, end_date)
        
        save_json(file_path, transactions)
        print(f"Đã xuất {len(transactions)} giao dịch ra file: {file_path}")
        return file_path

    def get_transactions_by_user(self, user_id):
        """Lấy tất cả giao dịch của một user"""
        transactions = self.load_transactions() 
        return [txn for txn in transactions if txn['user_id'] == user_id]

    def get_monthly_summary(self, user_id, year, month):
        """Tóm tắt giao dịch theo tháng cho báo cáo ngân sách"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        transactions = self.get_transactions_by_date_range(user_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        income_breakdown = {}
        expense_breakdown = {}
        for txn in transactions:
            cat_name = self.category_manager.get_category_name(txn['category_id'])
            if txn['type'] == 'income':
                income_breakdown[cat_name] = income_breakdown.get(cat_name, 0) + txn['amount']
            elif txn['type'] == 'expense':
                expense_breakdown[cat_name] = expense_breakdown.get(cat_name, 0) + txn['amount']
        return {
            'income_breakdown': income_breakdown,
            'expense_breakdown': expense_breakdown,
            'transactions': transactions
        }