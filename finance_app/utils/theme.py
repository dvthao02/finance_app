# utils/theme.py

# Lưu theme hiện tại (ban đầu là light mode)
current_theme = "light"

# Định nghĩa màu cho mỗi theme
THEMES = {
    "light": {
        "bg": "#f0f0f0",       # background màu xám sáng
        "fg": "#000000",       # chữ đen
        "entry_bg": "#ffffff", # ô nhập liệu màu trắng
        "entry_fg": "#000000",
        "button_bg": "#4caf50", # nút màu xanh lá
        "button_fg": "#ffffff",
        "error_fg": "#ff0000"
    },
    "dark": {
        "bg": "#2e2e2e",        # nền đen
        "fg": "#ffffff",        # chữ trắng
        "entry_bg": "#3c3f41",  # ô nhập màu xám đậm
        "entry_fg": "#ffffff",
        "button_bg": "#007acc", # nút màu xanh dương
        "button_fg": "#ffffff",
        "error_fg": "#ff6666"
    }
}

def get_theme():
    """Trả về theme hiện tại (dạng dict màu sắc)."""
    return THEMES[current_theme]

def toggle_theme():
    """Chuyển đổi giữa light và dark mode."""
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"

def set_theme(theme_name):
    """Đặt theme theo tên nếu hợp lệ."""
    global current_theme
    if theme_name in THEMES:
        current_theme = theme_name
