import os
from PIL import Image, ImageTk

# Get absolute path to assets directory relative to this file
ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))

def load_image(filename, size=None):
    """
    Load một ảnh từ thư mục assets và trả về đối tượng ImageTk.PhotoImage.
    
    Args:
        filename (str): Tên file ảnh (ví dụ: 'logo.png')
        size (tuple): Kích thước mong muốn (width, height), hoặc None để giữ nguyên
    
    Returns:
        ImageTk.PhotoImage hoặc None nếu không tìm thấy ảnh
    """
    filepath = os.path.join(ASSETS_DIR, filename)
    if not os.path.isfile(filepath):
        print(f"[Assets] Không tìm thấy ảnh: {filepath}")
        return None

    try:
        img = Image.open(filepath)
        if size:
            img = img.resize(size, Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"[Assets] Lỗi khi tải ảnh '{filename}': {e}")
        return None
