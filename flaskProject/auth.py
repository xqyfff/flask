from werkzeug.security import generate_password_hash, check_password_hash
from models import User


def register_user(username, password):
    hashed = generate_password_hash(password)
    user = User(id=None, username=username)  # id 由数据库自增生成
    print(f"{username},{password} saved")
    return user.save_to_db(hashed)


def verify_user(username, password):
    user = User.get_by_username(username)
    if user and check_password_hash(user.password, password):
        return user  # ✅ 返回 User 实例以供 login_user() 使用
    return None
