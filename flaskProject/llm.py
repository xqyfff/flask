import datetime
import sqlite3
import time

import openai
from openai import OpenAI
from flask import Blueprint, Response, json, request, jsonify, stream_with_context
from flask_login import login_required, current_user
from flask_cors import cross_origin
import requests
import json
from http import HTTPStatus

from sqlalchemy.exc import IntegrityError

from models import Conversation, db, UserConversationList

# deepseek sk-a73628b63ebd40218a128fa0ce8c725b
# doubao-1-5-thinking-pro-250415 0608cc4d-73b5-482d-8fae-15d2f8508d4b


llm_bp = Blueprint('llm', __name__)
client = OpenAI(api_key="sk-a73628b63ebd40218a128fa0ce8c725b", base_url="https://api.deepseek.com")
client_doubao = OpenAI(api_key="0608cc4d-73b5-482d-8fae-15d2f8508d4b",
                       base_url="https://ark.cn-beijing.volces.com/api/v3")
client_tongyi = OpenAI(api_key="sk-8b83f21bb3704383a0929a661153e21b",
                       base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")


@llm_bp.route('/deepseek')
@cross_origin(supports_credentials=True)
@login_required
def get_deepseek_answer():
    if not current_user.is_authenticated:
        return jsonify({'error': '请先登录'}), 401

    query = request.args.get('query')
    conversation_id = request.args.get('conversation_id')
    username = current_user.username

    if not query:
        return "query 参数缺失", 400

        # 检查是否已有该 conversation_id 的摘要，如果没有则生成并保存
    existing = UserConversationList.query.filter_by(username=username, conversation_id=conversation_id).first()

    if not existing:
        summary = get_summary(query)[:10]
        new_record = UserConversationList(
            username=username,
            conversation_id=conversation_id,
            summary=summary
        )
        db.session.add(new_record)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            # 插入失败说明有并发插入了，查出来尝试更新
            existing = UserConversationList.query.filter_by(username=username, conversation_id=conversation_id).first()
            if existing and existing.summary == "新会话":
                existing.summary = summary
                db.session.commit()
    else:
        if existing.summary == "新会话":
            summary = get_summary(query)[:10]
            existing.summary = summary
            db.session.commit()

    # 获取历史对话作为上下文
    history_records = Conversation.get_history(user_id=username, conversation_id=conversation_id)
    messages = [{"role": record.role, "content": record.content} for record in history_records]
    messages.append({"role": "user", "content": query})

    def event_stream(query):
        Conversation.save_message(user_id=username, conversation_id=conversation_id,
                                  role="user", content=query)

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True
        )

        assistant_reply = ""
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                assistant_reply += delta.content
                yield f"data: {delta.content}\n\n"

        Conversation.save_message(user_id=username, conversation_id=conversation_id,
                                  role="assistant", content=assistant_reply)
        yield "data: [DONE]\n\n"

    return Response(stream_with_context(event_stream(query)), mimetype='text/event-stream')


@llm_bp.route('/doubao')
@cross_origin(supports_credentials=True)
@login_required
def get_doubao_answer():
    if not current_user.is_authenticated:
        return jsonify({'error': '请先登录'}), 401

    query = request.args.get('query')
    conversation_id = request.args.get('conversation_id')
    username = current_user.username

    if not query:
        return "query 参数缺失", 400

    # 检查是否已有该 conversation_id 的摘要，如果没有则生成并保存
    existing = UserConversationList.query.filter_by(username=username, conversation_id=conversation_id).first()

    if not existing:
        summary = get_summary(query)[:10]
        new_record = UserConversationList(
            username=username,
            conversation_id=conversation_id,
            summary=summary
        )
        db.session.add(new_record)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            # 插入失败说明有并发插入了，查出来尝试更新
            existing = UserConversationList.query.filter_by(username=username, conversation_id=conversation_id).first()
            if existing and existing.summary == "新会话":
                existing.summary = summary
                db.session.commit()
    else:
        if existing.summary == "新会话":
            summary = get_summary(query)[:10]
            existing.summary = summary
            db.session.commit()

    # 获取历史对话作为上下文
    history_records = Conversation.get_history(user_id=username, conversation_id=conversation_id)
    messages = [{"role": record.role, "content": record.content} for record in history_records]
    messages.append({"role": "user", "content": query})

    def event_stream(query):
        Conversation.save_message(user_id=username, conversation_id=conversation_id,
                                  role="user", content=query)

        response = client_doubao.chat.completions.create(
            model="doubao-1-5-thinking-pro-250415",
            messages=messages,
            stream=True
        )

        assistant_reply = ""
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                assistant_reply += delta.content
                yield f"data: {delta.content}\n\n"

        Conversation.save_message(user_id=username, conversation_id=conversation_id,
                                  role="assistant", content=assistant_reply)
        yield "data: [DONE]\n\n"

    return Response(stream_with_context(event_stream(query)), mimetype='text/event-stream')


@llm_bp.route('/tongyi')
@cross_origin(supports_credentials=True)
@login_required
def get_tongyi_answer():
    if not current_user.is_authenticated:
        return jsonify({'error': '请先登录'}), 401

    query = request.args.get('query')
    conversation_id = request.args.get('conversation_id')
    username = current_user.username

    if not query:
        return "query 参数缺失", 400

    # 检查是否已有该 conversation_id 的摘要，如果没有则生成并保存
    existing = UserConversationList.query.filter_by(username=username, conversation_id=conversation_id).first()

    if not existing:
        summary = get_summary(query)[:10]
        new_record = UserConversationList(
            username=username,
            conversation_id=conversation_id,
            summary=summary
        )
        db.session.add(new_record)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            # 插入失败说明有并发插入了，查出来尝试更新
            existing = UserConversationList.query.filter_by(username=username, conversation_id=conversation_id).first()
            if existing and existing.summary == "新会话":
                existing.summary = summary
                db.session.commit()
    else:
        if existing.summary == "新会话":
            summary = get_summary(query)[:10]
            existing.summary = summary
            db.session.commit()

    # 获取历史对话作为上下文
    history_records = Conversation.get_history(user_id=username, conversation_id=conversation_id)
    messages = [{"role": record.role, "content": record.content} for record in history_records]
    messages.append({"role": "user", "content": query})

    def event_stream(query):
        Conversation.save_message(user_id=username, conversation_id=conversation_id,
                                  role="user", content=query)

        response = client_tongyi.chat.completions.create(
            model="qwen-plus-latest",
            messages=messages,
            stream=True
        )

        assistant_reply = ""
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                assistant_reply += delta.content
                yield f"data: {delta.content}\n\n"

        Conversation.save_message(user_id=username, conversation_id=conversation_id,
                                  role="assistant", content=assistant_reply)
        yield "data: [DONE]\n\n"

    return Response(stream_with_context(event_stream(query)), mimetype='text/event-stream')


@llm_bp.route('/list')
@cross_origin(supports_credentials=True)
@login_required
def list_conversations():
    username = current_user.username
    print(f"查询用户 {username} 的所有对话")

    records = UserConversationList.query.filter_by(username=username).all()

    result = []
    for record in records:
        result.append({
            'conversation_id': record.conversation_id,
            'summary': record.summary
        }
        )
        print(record.conversation_id)
        print(record.summary)

    return jsonify({'data': result})


@llm_bp.route('/create_conversation', methods=['POST'])
@cross_origin(supports_credentials=True)
@login_required
def create_conversation():
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    summary = data.get('summary')[:20] if data.get('summary') else '新会话'

    new_conv = UserConversationList(
        username=current_user.username,
        conversation_id=conversation_id,
        summary=summary
    )
    db.session.add(new_conv)
    db.session.commit()
    return jsonify({'status': 'ok'})


# 获取
@llm_bp.route('/conversation_history')
@cross_origin(supports_credentials=True)
@login_required
def get_conversation_history():
    username = current_user.username
    conversation_id = request.args.get('conversation_id')

    if not conversation_id:
        return jsonify({'error': '缺少 conversation_id 参数'}), 400

    # 查询历史记录
    try:
        history_records = Conversation.get_history(user_id=username, conversation_id=conversation_id)
    except Exception as e:
        return jsonify({'error': f'查询历史失败: {str(e)}'}), 500

    # 格式化输出
    messages = []
    for record in history_records:
        messages.append({
            'role': record.role,
            'content': record.content,
            'timestamp': record.timestamp.isoformat() if record.timestamp else None
        })

    return jsonify({'conversation_id': conversation_id, 'messages': messages})


def get_summary(query):
    prompt = f"请用不超过10个汉字对下面的问题做一个简短总结：\n问题：{query}"
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=20,
            stream=False
        )
        summary = response.choices[0].message.content.strip()
        return summary[:10]  # 截断为最多10个字
    except Exception as e:
        print(f"生成摘要失败：{e}")
        return "无摘要"


@llm_bp.route('/deepseek_s')
@cross_origin(supports_credentials=True)
@login_required
def get_deepseek_s_answer():
    if not current_user.is_authenticated:
        return jsonify({'error': '请先登录'}), 401

    query = request.args.get('query')
    username = current_user.username

    if not query:
        return "query 参数缺失", 400

    messages = [{"role": "user", "content": query}]

    def event_stream(query):

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True
        )

        assistant_reply = ""
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                assistant_reply += delta.content
                yield f"data: {delta.content}\n\n"

        yield "data: [DONE]\n\n"

    return Response(stream_with_context(event_stream(query)), mimetype='text/event-stream')


@llm_bp.route('/doubao_s')
@cross_origin(supports_credentials=True)
@login_required
def get_doubao_s_answer():
    if not current_user.is_authenticated:
        return jsonify({'error': '请先登录'}), 401

    query = request.args.get('query')
    username = current_user.username

    if not query:
        return "query 参数缺失", 400

    messages = [{"role": "user", "content": query}]

    def event_stream(query):

        response = client_doubao.chat.completions.create(
            model="doubao-1-5-thinking-pro-250415",
            messages=messages,
            stream=True
        )

        assistant_reply = ""
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                assistant_reply += delta.content
                yield f"data: {delta.content}\n\n"

        yield "data: [DONE]\n\n"

    return Response(stream_with_context(event_stream(query)), mimetype='text/event-stream')

@llm_bp.route('/tongyi_s')
@cross_origin(supports_credentials=True)
@login_required
def get_tongyi_s_answer():
    if not current_user.is_authenticated:
        return jsonify({'error': '请先登录'}), 401

    query = request.args.get('query')
    username = current_user.username

    if not query:
        return "query 参数缺失", 400

    messages = [{"role": "user", "content": query}]

    def event_stream(query):

        response = client_tongyi.chat.completions.create(
            model="qwen-plus-latest",
            messages=messages,
            stream=True
        )

        assistant_reply = ""
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                assistant_reply += delta.content
                yield f"data: {delta.content}\n\n"

        yield "data: [DONE]\n\n"

    return Response(stream_with_context(event_stream(query)), mimetype='text/event-stream')
