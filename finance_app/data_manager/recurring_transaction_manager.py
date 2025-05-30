from pathlib import Path
import datetime
from finance_app.utils.file_helper import load_json, save_json, generate_id, validate_date_format
from finance_app.data_manager.user_manager import UserManager
from finance_app.data_manager.category_manager import CategoryManager

class RecurringTransactionManager:
    VALID_FREQUENCIES = ["daily", "weekly", "monthly", "quarterly", "yearly"]

    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data"
        self.recurring_file = self.data_dir / "recurring_transactions.json"
        self.user_manager = UserManager()
        self.category_manager = CategoryManager()
        self.current_user_id = None
        self.recurring_transactions = None # Defer loading

    def _load_data_if_needed(self):
        if self.recurring_transactions is None:
            self.recurring_transactions = load_json(self.recurring_file)

    def set_current_user(self, user_id):
        """Thiết lập người dùng hiện tại
        Args:
            user_id (str): ID của người dùng
        """
        self.current_user_id = user_id
        self.category_manager.set_current_user(user_id)

    def _save_data(self):
        return save_json(self.recurring_file, self.recurring_transactions)

    def get_all(self, user_id=None, target_user_id=None, active_only=True):
        self._load_data_if_needed()
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            return []
            
        if target_user_id and target_user_id != user_id and not self.user_manager.is_admin(user_id):
            raise ValueError("Không có quyền truy cập dữ liệu của người dùng khác")
        
        data_to_filter = self.recurring_transactions
        if target_user_id:
            data_to_filter = [r for r in data_to_filter if r.get("user_id") == target_user_id]
        else:
            data_to_filter = [r for r in data_to_filter if r.get("user_id") == user_id]
            
        if active_only:
            data_to_filter = [r for r in data_to_filter if r.get("is_active", True)]
        return data_to_filter

    def get_by_id(self, user_id=None, recurring_id=None):
        self._load_data_if_needed()
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or recurring_id is None:
            return None
            
        for item in self.recurring_transactions:
            if item.get("recurring_id") == recurring_id:
                if item['user_id'] != user_id and not self.user_manager.is_admin(user_id):
                    raise ValueError("Không có quyền truy cập giao dịch định kỳ này")
                return item
        return None

    def create(self, user_id=None, category_id=None, amount=None, transaction_type=None, description=None,
               frequency="monthly", start_date=None, end_date=None, tags=None, auto_create=True):
        self._load_data_if_needed()
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or category_id is None or amount is None or transaction_type is None or description is None:
            return None, "Thiếu thông tin bắt buộc"
            
        # Kiểm tra user_id
        if not self.user_manager.get_user_by_id(user_id):
            return None, f"Không tìm thấy người dùng với ID: {user_id}"
        
        # Kiểm tra category_id
        category = self.category_manager.get_category_by_id(user_id, category_id)
        if not category:
            return None, f"Không tìm thấy danh mục với ID: {category_id} hoặc không có quyền"
        
        if not self._validate(amount, transaction_type, frequency):
            return None, "Dữ liệu không hợp lệ"
        
        if start_date and not validate_date_format(start_date):
            return None, "Ngày bắt đầu không đúng định dạng YYYY-MM-DD"
        if end_date and not validate_date_format(end_date):
            return None, "Ngày kết thúc không đúng định dạng YYYY-MM-DD"
        
        new_id = generate_id("rec", self.recurring_transactions)
        now = datetime.datetime.now().isoformat()
        start_date = start_date or now[:10]
        
        new_item = {
            "recurring_id": new_id,
            "user_id": user_id,
            "category_id": category_id,
            "amount": float(amount),
            "type": transaction_type,
            "description": description,
            "frequency": frequency,
            "start_date": start_date,
            "end_date": end_date,
            "next_date": self._next_date(start_date, frequency),
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "tags": tags or [],
            "auto_create": auto_create
        }
        
        self.recurring_transactions.append(new_item)
        if self._save_data():
            return new_id, new_item
        return None, "Lỗi khi lưu file"

    def update(self, user_id=None, recurring_id=None, **kwargs):
        self._load_data_if_needed()
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or recurring_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        recurring = self.get_by_id(user_id, recurring_id)
        if not recurring:
            return False, "Không tìm thấy giao dịch định kỳ hoặc không có quyền"
        
        item_updated = False
        for i, r_txn in enumerate(self.recurring_transactions):
            if r_txn.get("recurring_id") == recurring_id:
                # Double check permission here, though get_by_id should have handled it
                if r_txn['user_id'] != user_id and not self.user_manager.is_admin(user_id):
                    return False, "Không có quyền cập nhật giao dịch định kỳ này"

                changed_locally = False # Track if changes were made in this iteration
                for key in [
                    "category_id", "amount", "type", "description",
                    "frequency", "start_date", "end_date", "tags", 
                    "auto_create", "is_active", "next_date"
                ]:
                    if key in kwargs:
                        if key == 'category_id':
                            category = self.category_manager.get_category_by_id(user_id, kwargs[key])
                            if not category:
                                return False, f"Không tìm thấy danh mục với ID: {kwargs[key]} hoặc không có quyền"
                        elif key in ['start_date', 'end_date'] and kwargs[key] and not validate_date_format(kwargs[key]):
                            return False, f"Ngày {key} không đúng định dạng YYYY-MM-DD"
                        elif key == 'amount' and kwargs[key] <= 0:
                            return False, "Số tiền phải lớn hơn 0"
                        elif key == 'type' and kwargs[key] not in ['income', 'expense']:
                            return False, "Loại giao dịch phải là 'income' hoặc 'expense'"
                        elif key == 'frequency' and kwargs[key] not in self.VALID_FREQUENCIES:
                            return False, f"Tần suất phải là: {', '.join(self.VALID_FREQUENCIES)}"
                        
                        r_txn[key] = kwargs[key]
                        changed_locally = True
                
                if changed_locally:
                    r_txn["updated_at"] = datetime.datetime.now().isoformat()
                    if "frequency" in kwargs or "start_date" in kwargs or "next_date" in kwargs:
                        # Recalculate next_date if relevant fields change, or if explicitly provided
                        r_txn["next_date"] = kwargs.get("next_date", self._next_date(r_txn.get("start_date"), r_txn.get("frequency")))
                    self.recurring_transactions[i] = r_txn
                    item_updated = True # Mark that an update occurred in the broader list
                    break # Found and updated the item
        
        if item_updated:
            if self._save_data():
                return True, "Cập nhật thành công"
            else:
                # Potentially rollback or log error more thoroughly if save fails
                return False, "Lỗi khi lưu file sau khi cập nhật"
                
        return False, "Không tìm thấy giao dịch định kỳ hoặc không có thay đổi nào được thực hiện"

    def delete(self, user_id=None, recurring_id=None):
        self._load_data_if_needed()
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or recurring_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        # Verify existence and permission first using get_by_id
        item_to_delete = self.get_by_id(user_id, recurring_id) 
        if not item_to_delete:
            return False, "Không tìm thấy giao dịch định kỳ hoặc không có quyền"
        
        self.recurring_transactions = [r for r in self.recurring_transactions if r.get("recurring_id") != recurring_id]
        if self._save_data():
            return True, "Xóa thành công"
        return False, "Lỗi khi lưu file sau khi xóa"

    def deactivate(self, user_id=None, recurring_id=None):
        self._load_data_if_needed()
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or recurring_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        return self.update(user_id, recurring_id, is_active=False)

    def activate(self, user_id=None, recurring_id=None):
        self._load_data_if_needed() # ensure data is loaded before update call
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or recurring_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        return self.update(user_id, recurring_id, is_active=True)

    def get_due(self, user_id=None):
        self._load_data_if_needed()
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            return []
            
        today = datetime.datetime.now().isoformat()
        data = self.get_all(user_id, user_id, active_only=True)
        return [
            r for r in data
            if r.get("next_date") and r["next_date"] <= today
            and (not r.get("end_date") or r["end_date"] > today)
            and r.get("auto_create", True)
        ]

    def get_upcoming(self, user_id=None, days=7):
        self._load_data_if_needed()
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None:
            return []
            
        today = datetime.datetime.now()
        future = today + datetime.timedelta(days=days)
        data = self.get_all(user_id, user_id, active_only=True)
        upcoming = [
            r for r in data
            if r.get("next_date") and today.isoformat() <= r["next_date"] <= future.isoformat()
        ]
        return sorted(upcoming, key=lambda r: r.get("next_date"))

    def process_due(self):
        # Ensure this method doesn't load data for all users if not intended.
        # It should operate on a specific user context or be run by an admin for all.
        # For now, assuming it uses current_user_id if set, or needs explicit user_id if run globally.
        # The original get_due() call inside here implies it might be for the current_user_id context.
        # If this is a system-wide process, it needs to iterate through users.
        
        # Clarification: get_due() internally uses self.current_user_id.
        # If process_due is called without a user context, get_due() will return empty.
        # This method should ideally be called within a user session or pass a user_id.
        
        self._load_data_if_needed() # Load data for the current context

        from finance_app.data_manager.transaction_manager import TransactionManager
        from finance_app.data_manager.notification_manager import NotificationManager
        
        transaction_mgr = TransactionManager()
        notification_mgr = NotificationManager()
        due_items = self.get_due()
        count = 0
        
        for item in due_items:
            trans_id = transaction_mgr.add_transaction(
                user_id=item["user_id"],
                category_id=item["category_id"],
                amount=item["amount"],
                transaction_type=item["type"],
                description=item.get("description", "") + " (Tự động)",
                date=item["next_date"][:10],
                tags=["recurring"]
            )
            
            if trans_id:
                self.update(
                    item["user_id"],
                    item["recurring_id"],
                    next_date=self._next_date(item["next_date"], item["frequency"]),
                    last_processed=datetime.datetime.now().isoformat()
                )
                success, message = notification_mgr.create_notification(
                    user_id=item["user_id"],
                    notification_type="recurring_reminder",
                    title="Đã thực hiện giao dịch định kỳ",
                    message=f"Giao dịch '{item['description']}' đã được xử lý.",
                    priority="medium",
                    data={"transaction_id": trans_id}
                )
                if success:
                    count += 1
        
        return count

    def delete_user_recurring_transactions(self, user_id):
        """Delete all recurring transactions for a user
        
        Args:
            user_id (str): ID of the user whose recurring transactions should be deleted
        """
        self._load_data_if_needed()
        if not user_id:
            return
        
        self.recurring_transactions = [r for r in self.recurring_transactions if r.get("user_id") != user_id]
        if self._save_data():
            print(f"Đã xóa tất cả giao dịch định kỳ của người dùng: {user_id}")
            return True
        return False

    def _validate(self, amount, trans_type, freq):
        if not isinstance(amount, (int, float)) or amount <= 0:
            return False
        if trans_type not in ["income", "expense"]:
            return False
        if freq not in self.VALID_FREQUENCIES:
            return False
        return True

    def _next_date(self, date_str, freq="monthly"):
        if not date_str:
            return None
            
        date = self._parse_date(date_str)
        if not date:
            return None
            
        if freq == "daily":
            next_date = date + datetime.timedelta(days=1)
        elif freq == "weekly":
            next_date = date + datetime.timedelta(days=7)
        elif freq == "monthly":
            next_date = self._add_months(date, 1)
        elif freq == "quarterly":
            next_date = self._add_months(date, 3)
        elif freq == "yearly":
            next_date = date.replace(year=date.year + 1)
        else:
            return None
            
        return next_date.isoformat()

    def _add_months(self, date, months):
        month = date.month - 1 + months
        year = date.year + month // 12
        month = month % 12 + 1
        day = min(date.day, self._days_in_month(year, month))
        return date.replace(year=year, month=month, day=day)

    def _days_in_month(self, year, month):
        if month == 2:
            return 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28
        return [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]

    def _parse_date(self, s):
        try:
            return datetime.datetime.fromisoformat(s)
        except (ValueError, TypeError):
            return None