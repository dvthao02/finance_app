# file_helper.py

import json
import os
from datetime import datetime

def load_json(file_path):
    """Đọc dữ liệu từ file JSON"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        return []
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Lỗi khi đọc file {file_path}: {e}")
        return []

def save_json(file_path, data):
    """Lưu dữ liệu vào file JSON"""
    try:
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Lỗi khi lưu file {file_path}: {e}")
        return False

def generate_id(prefix=None, data_list=None):
    """Tạo ID tự động dựa trên prefix và danh sách hiện có"""
    if data_list is None:
        data_list = []
    if not prefix:
        prefix = "id"
    if not data_list:
        return f"{prefix}_001"
    
    # Lấy số cao nhất hiện có
    max_num = 0
    for item in data_list:
        # Lấy key đầu tiên có chứa _id
        id_key = next((key for key in item.keys() if key.endswith('_id')), None)
        if id_key and item[id_key].startswith(prefix):
            try:
                num = int(item[id_key].split('_')[-1])
                max_num = max(max_num, num)
            except (ValueError, IndexError):
                continue
    
    return f"{prefix}_{max_num + 1:03d}"

def get_current_datetime():
    """Lấy thời gian hiện tại theo format ISO"""
    return datetime.now().isoformat()

def validate_date_format(date_string):
    """Kiểm tra format ngày tháng YYYY-MM-DD"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_datetime_format(datetime_string):
    """Kiểm tra format datetime ISO"""
    try:
        datetime.fromisoformat(datetime_string.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False