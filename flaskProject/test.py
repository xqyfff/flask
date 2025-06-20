from datetime import datetime
from app import app, db
from models import Conversation, UserConversationList, Feedback, User

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

    feedback_list = Feedback.query.order_by(Feedback.timestamp.desc()).all()

    print(f"共 {len(feedback_list)} 条反馈：\n")
    for feedback in feedback_list:

        print(f"用户: {feedback.user_id}")
        print(f"时间: {feedback.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"内容: {feedback.message}")
        print("-" * 50)

