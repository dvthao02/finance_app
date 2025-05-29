from pathlib import Path
import datetime
from utils.file_helper import load_json, save_json, generate_id, validate_date_format
from data_manager.user_manager import UserManager
from data_manager.category_manager import CategoryManager

class RecurringTransaction:
    VALID_FREQUENCIES = ["daily", "weekly", "monthly", "quarterly", "yearly"]

    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data"
        self.recurring_file = self.data_dir / "recurring_transactions.json"
        self.user_manager = UserManager()
        self.category_manager = CategoryManager()

    def get_all(self, user_id, target_user_id=None, active_only=True):
        if target_user_id and target_user_id != user_id and not self.user_manager.is_admin(user_id):
            raise ValueError("Không có quyền truy cập dữ liệu của người dùng khác")
        
        data = load_json(self.recurring_file)
        if target_user_id:
            data = [r for r in data if r.get("user_id") == target_user_id]
        if active_only:
            data = [r for r in data if r.get("is_active", True)]
        return data

    def get_by_id(self, user_id, recurring_id):
        data = load_json(self.recurring_file)
        for item in data:
            if item.get("recurring_id") == recurring_id:
                if item['user_id'] != user_id and not self.user_manager.is_admin(user_id):
                    raise ValueError("Không có quyền truy cập giao dịch định kỳ này")
                return item
        return None

    def create(self, user_id, category_id, amount, transaction_type, description,
               frequency="monthly", start_date=None, end_date=None, tags=None, auto_create=True):
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
        
        data = load_json(self.recurring_file)
        new_id = generate_id("rec", data)
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
        
        data.append(new_item)
        if save_json(self.recurring_file, data):
            return new_id, new_item
        return None, "Lỗi khi lưu file"

    def update(self, user_id, recurring_id, **kwargs):
        recurring = self.get_by_id(user_id, recurring_id)
        if not recurring:
            return False, "Không tìm thấy giao dịch định kỳ hoặc không có quyền"
        
        data = load_json(self.recurring_file)
        for i, r in enumerate(data):
            if r.get("recurring_id") == recurring_id:
                changed = False
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
                        
                        r[key] = kwargs[key]
                        changed = True
                
                if changed:
                    r["updated_at"] = datetime.datetime.now().isoformat()
                    if "frequency" in kwargs or "start_date" in kwargs:
                        r["next_date"] = self._next_date(r.get("start_date"), r.get("frequency"))
                    data[i] = r
                    return save_json(self.recurring_file, data), "Cập nhật thành công"
        return False, "Không tìm thấy giao dịch định kỳ"

    def delete(self, user_id, recurring_id):
        recurring = self.get_by_id(user_id, recurring_id)
        if not recurring:
            return False, "Không tìm thấy giao dịch định kỳ hoặc không có quyền"
        
        data = load_json(self.recurring_file)
        data = [r for r in data if r.get("recurring_id") != recurring_id]
        return save_json(self.recurring_file, data), "Xóa thành công"

    def deactivate(self, user_id, recurring_id):
        return self.update(user_id, recurring_id, is_active=False)

    def activate(self, user_id, recurring_id):
        return self.update(user_id, recurring_id, is_active=True)

    def get_due(self, user_id=None):
        today = datetime.datetime.now().isoformat()
        data = self.get_all(user_id, user_id, active_only=True)
        return [
            r for r in data
            if r.get("next_date") and r["next_date"] <= today
            and (not r.get("end_date") or r["end_date"] > today)
            and r.get("auto_create", True)
        ]

    def get_upcoming(self, user_id, days=7):
        today = datetime.datetime.now()
        future = today + datetime.timedelta(days=days)
        data = self.get_all(user_id, user_id, active_only=True)
        upcoming = [
            r for r in data
            if r.get("next_date") and today.isoformat() <= r["next_date"] <= future.isoformat()
        ]
        return sorted(upcoming, key=lambda r: r.get("next_date"))

    def process_due(self):
        from .transaction_manager import TransactionManager
        from .notification_manager import NotificationManager
        
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

    def _validate_amount(self, amount, trans_type, freq):
        if not isinstance(amount, (int, float)) or amount <= 0:
            return False, "Số tiền phải là số dương"
        if trans_type not in ["income", "expense"]:
            return False, "Loại giao dịch không hợp lệ"
        if freq not in self.VALID_FREQUENCIES:
            return False, f"Tần suất phải là: {', '.join(self.VALID_FREQUENCIES)}"
        return True, ""

    def _next_date(self, date_str, freq="monthly"):
        date = self._parse_date(date_str)
        today_date = datetime.datetime.now()
        if date > today_date:
            return date.isoformat()
        
        if freq == "daily":
            date += datetime.timedelta(days=1)
        elif freq == "weekly":
            date += datetime.timedelta(weeks=1)
        elif freq == "monthly":
            date = self._add_months(date, 1)
        elif freq == "quarterly":
            date = self._add_months(date, 3)
        elif freq == "yearly":
            date = date.replace(year=date.year + 1)
        return date.isoformat()

    def _add_months(self, date, months):
        month = date.month - 1 + months
        year = date.year + (month // 12)
        month = month % 12 + 1
        day = min(date.day, self._days_in_month(year, month))
        return datetime.datetime(year, month, day, date.hour, date.minute, date.second)

    def _days_in_month(self, year, month):
        if month == 2:
            return 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28
        return 30 if month in [4, 6, 9, 11] else 31

    def _parse_date(self, s):
        try:
            return datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))
        except ValueError:
            try:
                return datetime.datetime.strptime(s, "%Y-%m-%d")
            except ValueError:
                return datetime.datetime.now()