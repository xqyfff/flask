import sqlite3


def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # 创建 users 表
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # 创建 conversation 表
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        conversation_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 创建 user_conversation_list 表（对应 UserConversationList 类）
    c.execute('''
            CREATE TABLE IF NOT EXISTS user_conversation_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                conversation_id TEXT NOT NULL,
                summary TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(username, conversation_id)
            )
        ''')

    conn.execute("PRAGMA foreign_keys = ON")

    conn.commit()
    conn.close()
    print("数据库初始化完成")


if __name__ == '__main__':
    init_db()
