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
        self.current_user_id = None
        self.transactions = self.load_transactions()

    def set_current_user(self, user_id):
        """Thiết lập người dùng hiện tại
        Args:
            user_id (str): ID của người dùng
        """
        self.current_user_id = user_id
        self.category_manager.set_current_user(user_id)
        # Reload transactions when user changes
        self.transactions = self.load_transactions()

    def load_transactions(self):
        """Tải danh sách giao dịch từ file"""
        return load_json(self.transaction_file)

    def save_transactions(self, transactions):
        """Lưu danh sách giao dịch vào file"""
        return save_json(self.transaction_file, transactions)

    def get_all_transactions(self, user_id=None, target_user_id=None, transaction_type=None):
        """Lấy tất cả giao dịch, có thể lọc theo user_id và loại giao dịch
        
        Args:
            user_id (str): ID của người dùng thực hiện yêu cầu
            target_user_id (str): ID của người dùng cần lấy giao dịch (dùng cho admin)
            transaction_type (str): Loại giao dịch ('income' hoặc 'expense')
        """
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            return []
            
        if target_user_id and target_user_id != user_id and not self.user_manager.is_admin(user_id):
            raise ValueError("Không có quyền truy cập dữ liệu của người dùng khác")
        
        transactions = self.load_transactions()
        filtered_transactions = []
        
        for txn in transactions:
            # Filter by user
            if target_user_id and txn['user_id'] != target_user_id:
                continue
            if not target_user_id and txn['user_id'] != user_id:
                continue
                
            # Filter by type if specified
            if transaction_type and txn.get('type') != transaction_type:
                continue
                
            filtered_transactions.append(txn)
            
        return filtered_transactions

    def get_transaction_by_id(self, user_id=None, transaction_id=None, is_admin=False):
        """Tìm giao dịch theo ID"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or transaction_id is None:
            return None
            
        transactions = self.get_all_transactions(user_id, user_id)
        for transaction in transactions:
            if transaction['transaction_id'] == transaction_id:
                if is_admin or transaction['user_id'] == user_id:
                    return transaction
        return None

    def get_transaction_by_id_no_auth(self, transaction_id):
        """Tìm giao dịch theo ID mà không kiểm tra quyền"""
        if transaction_id is None:
            return None
            
        transactions = self.load_transactions()
        for transaction in transactions:
            if transaction['transaction_id'] == transaction_id:
                return transaction
        return None

    def add_transaction(self, user_id=None, category_id=None, amount=None, transaction_type=None, 
                       description="", date=None, tags=None, location=""):
        """Thêm giao dịch mới"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or category_id is None or amount is None or transaction_type is None:
            raise ValueError("Thiếu thông tin bắt buộc")
            
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

    def update_transaction(self, user_id=None, transaction_id=None, **kwargs):
        """Cập nhật giao dịch"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or transaction_id is None:
            raise ValueError("Thiếu thông tin bắt buộc")
            
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

    def delete_transaction(self, user_id=None, transaction_id=None):
        """Xóa giao dịch"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or transaction_id is None:
            raise ValueError("Thiếu thông tin bắt buộc")
            
        transaction = self.get_transaction_by_id(user_id, transaction_id)
        
        transactions = self.load_transactions()
        for i, txn in enumerate(transactions):
            if txn['transaction_id'] == transaction_id:
                del transactions[i]
                self.save_transactions(transactions)
                print(f"Đã xóa giao dịch: {transaction_id}")
                return True
        
        raise ValueError(f"Không tìm thấy giao dịch với ID: {transaction_id}")

    def get_transactions_by_date_range(self, user_id=None, start_date=None, end_date=None):
        """Lấy giao dịch trong khoảng thời gian"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or start_date is None or end_date is None:
            return []
            
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

    def get_transactions_by_category(self, user_id=None, category_id=None, start_date=None, end_date=None):
        """Lấy giao dịch theo danh mục"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or category_id is None:
            return []
            
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

    def search_transactions(self, user_id=None, keyword=None, transaction_type=None, category_id=None):
        """Tìm kiếm giao dịch theo từ khóa"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or keyword is None:
            return []
            
        transactions = self.get_all_transactions(user_id, user_id)
        keyword = keyword.lower()
        results = []
        
        for txn in transactions:
            if (keyword in txn['description'].lower() or 
                keyword in txn['location'].lower() or
                any(keyword in tag.lower() for tag in txn.get('tags', []))):
                
                if transaction_type and txn['type'] != transaction_type:
                    continue
                    
                if category_id and txn['category_id'] != category_id:
                    continue
                    
                results.append(txn)
                
        return results

    def get_transaction_summary(self, user_id=None, start_date=None, end_date=None):
        """Lấy tổng kết giao dịch"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            return {
                'total_income': 0,
                'total_expense': 0,
                'net_amount': 0,
                'transaction_count': 0
            }
            
        transactions = self.get_all_transactions(user_id, user_id)
        
        if start_date and end_date:
            transactions = self.get_transactions_by_date_range(user_id, start_date, end_date)
            
        total_income = sum(txn['amount'] for txn in transactions if txn['type'] == 'income')
        total_expense = sum(txn['amount'] for txn in transactions if txn['type'] == 'expense')
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'net_amount': total_income - total_expense,
            'transaction_count': len(transactions)
        }

    def get_category_breakdown(self, user_id=None, transaction_type=None, start_date=None, end_date=None):
        """Lấy phân tích theo danh mục"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            return {}
            
        transactions = self.get_all_transactions(user_id, user_id)
        
        if start_date and end_date:
            transactions = self.get_transactions_by_date_range(user_id, start_date, end_date)
            
        if transaction_type:
            transactions = [txn for txn in transactions if txn['type'] == transaction_type]
            
        breakdown = {}
        for txn in transactions:
            category = self.category_manager.get_category_by_id(user_id, txn['category_id'])
            if category:
                category_name = category['name']
                if category_name not in breakdown:
                    breakdown[category_name] = {
                        'amount': 0,
                        'count': 0,
                        'category_id': category['category_id']
                    }
                breakdown[category_name]['amount'] += txn['amount']
                breakdown[category_name]['count'] += 1
                
        return breakdown

    def get_monthly_report(self, user_id=None, year=None, month=None):
        """Lấy báo cáo tháng"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or year is None or month is None:
            return {
                'income': [],
                'expense': [],
                'total_income': 0,
                'total_expense': 0,
                'net_amount': 0
            }
            
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
            
        transactions = self.get_transactions_by_date_range(user_id, start_date, end_date)
        
        income_transactions = [t for t in transactions if t['type'] == 'income']
        expense_transactions = [t for t in transactions if t['type'] == 'expense']
        
        total_income = sum(t['amount'] for t in income_transactions)
        total_expense = sum(t['amount'] for t in expense_transactions)
        
        return {
            'income': income_transactions,
            'expense': expense_transactions,
            'total_income': total_income,
            'total_expense': total_expense,
            'net_amount': total_income - total_expense
        }

    def export_transactions(self, user_id=None, file_path=None, start_date=None, end_date=None):
        """Xuất giao dịch ra file"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            return False
            
        transactions = self.get_all_transactions(user_id, user_id)
        
        if start_date and end_date:
            transactions = self.get_transactions_by_date_range(user_id, start_date, end_date)
            
        if file_path:
            # TODO: Implement export to file
            pass
            
        return transactions

    def get_user_transactions(self, user_id, is_admin=False):
        """Get all transactions for a user or all if admin"""
        if is_admin:
            return self.transactions
        return [t for t in self.transactions if t['user_id'] == user_id]

    def get_monthly_summary(self, user_id=None, year=None, month=None):
        """Lấy tổng kết tháng"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or year is None or month is None:
            return {
                'total_income': 0,
                'total_expense': 0,
                'net_amount': 0,
                'category_breakdown': {}
            }
            
        report = self.get_monthly_report(user_id, year, month)
        category_breakdown = self.get_category_breakdown(user_id)
        
        return {
            'total_income': report['total_income'],
            'total_expense': report['total_expense'],
            'net_amount': report['net_amount'],
            'category_breakdown': category_breakdown
        }

    def delete_user_transactions(self, user_id):
        """Delete all transactions for a user
        
        Args:
            user_id (str): ID of the user whose transactions should be deleted
        """
        if not user_id:
            return
        
        transactions = self.load_transactions()
        transactions = [t for t in transactions if t['user_id'] != user_id]
        self.save_transactions(transactions)
        print(f"Đã xóa tất cả giao dịch của người dùng: {user_id}")
        return True