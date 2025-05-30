from data_manager.user_manager import UserManager

# Test đăng nhập với tài khoản dvthao
manager = UserManager()
result = manager.authenticate_user("dvthao", "123456aA@")
if result:
    print("Đăng nhập thành công!")
    print(f"Thông tin user: {result}")
else:
    print("Đăng nhập thất bại!")