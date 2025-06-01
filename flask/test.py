from datetime import datetime
from app import app, db
from models import Conversation, UserConversationList

with app.app_context():
    """db.create_all()  # 确保表存在
    success = Conversation.save_message(
        user_id='testuser',
        conversation_id='conv1',
        role='user',
        content='这是第二条测试消息'
    )
    print("保存成功吗？", success)

    # 查询打印看看
    msgs = Conversation.get_history('testuser', 'conv1')"""
    """msgs = Conversation.get_history('wjn', 'test')
    for m in msgs:
        print(m.role, m.content, m.timestamp)"""

    records = UserConversationList.query.filter_by(username='wjn').all()
    for record in records:
        print(record.conversation_id)
        print(record.summary)

