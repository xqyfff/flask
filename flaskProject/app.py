from datetime import datetime

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, logout_user, login_required, current_user
from llm import llm_bp
from flask import Flask, render_template, request, redirect, url_for, session, flash
from init_db import init_db
from auth import register_user, verify_user
from models import get_user_by_id, User, db, Feedback
from flask_login import login_user
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
CORS(app, supports_credentials=True)  # 允许跨域
app.register_blueprint(llm_bp, url_prefix='/llm')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('home.html', username=current_user.username)
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return f"欢迎你，{current_user.username}"


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if register_user(username, password):
            flash('注册成功，请登录')
            return redirect(url_for('login'))
        else:
            flash('用户名已存在')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.get_by_username(username)
        if user and check_password_hash(user.password, password):
            login_user(user)  # 正式登录
            flash('登录成功')
            return redirect(url_for('home'))

        flash('用户名或密码错误')
    return render_template('login.html')


@app.route('/feedback', methods=['POST'])
@login_required
def feedback():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求体不能为空'}), 400

    message = data.get('message')
    if not message:
        return jsonify({'error': '反馈内容不能为空'}), 400

    try:
        new_feedback = Feedback(
            user_id=current_user.id,
            message=message,
            timestamp=datetime.utcnow()
        )

        db.session.add(new_feedback)
        db.session.commit()

        return jsonify({'message': '反馈提交成功'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500


@app.route('/logout')
def logout():
    logout_user()  # ✅ 清除 Flask-Login 的登录状态
    flash('已登出')
    return redirect(url_for('login'))


@app.route('/deepseek_test')
def deepseek_test():
    if 'username' in session:
        print("!!!!!")
        print(session['username'])
    return render_template('test_deepseek.html')


@app.route('/conversation_test')
def conversation_test():
    return render_template('conversation_test.html')


@app.route('/feedback_test')
def feedback_test():
    return render_template('feedback.html')


@app.route('/chat_test')
def chat_test():
    return render_template('/chat_test_3.html')

@app.route('/models')
def models():
    return render_template('/chat_test_2.html')

if __name__ == '__main__':
    app.run(debug=True)
