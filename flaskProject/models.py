from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from flask_login import UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conversations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# TODO:定义USer模型

class User(UserMixin):
    def __init__(self, id, username, password=None):
        self.id = id  # Flask-Login 依赖这个字段
        self.username = username
        self.password = password  # 明文密码或哈希（根据使用场景）

    @staticmethod
    def get_by_username(username):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()
        if row:
            return User(id=row[0], username=row[1], password=row[2])
        return None

    @staticmethod
    def get_by_id(user_id):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT id, username, password FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return User(id=row[0], username=row[1], password=row[2])
        return None

    def save_to_db(self, hashed_password):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (self.username, hashed_password))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# 定义对话历史模型
class Conversation(db.Model):
    __tablename__ = 'conversation'  # 确保表名
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    conversation_id = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def get_history(cls, user_id, conversation_id):
        return cls.query.filter_by(user_id=user_id, conversation_id=conversation_id) \
            .order_by(cls.timestamp.asc()).all()

    @classmethod
    def save_message(cls, user_id, conversation_id, role, content):
        msg = cls(
            user_id=user_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )
        db.session.add(msg)
        db.session.commit()


class UserConversationList(db.Model):
    __tablename__ = 'user_conversation_list'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    conversation_id = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.String(20))  # 限定十字以内
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('username', 'conversation_id', name='user_convo_uc'),
    )

def get_user_by_id(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return User(id=row[0], username=row[1], password=row[2])
    return None
