import os
import json

def init_data_files():
    """Initialize necessary data files if they don't exist"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    # Create data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # List of required data files with their default content
    required_files = {
        'users.json': {'users': []},
        'transactions.json': {'transactions': []},
        'budgets.json': {'budgets': []},
        'categories.json': {'categories': [
            {'id': 1, 'name': 'Thực phẩm', 'type': 'expense'},
            {'id': 2, 'name': 'Di chuyển', 'type': 'expense'},
            {'id': 3, 'name': 'Tiện ích', 'type': 'expense'},
            {'id': 4, 'name': 'Lương', 'type': 'income'},
            {'id': 5, 'name': 'Thưởng', 'type': 'income'}
        ]},
        'notifications.json': {'notifications': []},
        'settings.json': {'settings': {}},
        'recurring_transactions.json': {'recurring_transactions': []}
    }
    
    # Create files if they don't exist
    for filename, default_content in required_files.items():
        file_path = os.path.join(data_dir, filename)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_content, f, ensure_ascii=False, indent=4)

# Initialize data files when module is imported
init_data_files()
