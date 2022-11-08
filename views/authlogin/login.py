from flask import Blueprint
from flask import current_app as app
from flask import request,url_for,redirect,flash,session
from flask import render_template
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import text

from flask_login import login_user, login_required, logout_user, current_user
from flask_login import LoginManager
from werkzeug.security import generate_password_hash,check_password_hash
import uuid
from flask_login import UserMixin  # 引入用户基类

auth = Blueprint('auth', __name__)
db = SQLAlchemy(app)

login_manager = LoginManager()  # 实例化登录管理对象
login_manager.init_app(app)  # 初始化应用
login_manager.login_view = 'auth.login'  # 设置用户登录视图函数 endpoint
login_manager.login_message = u'please log in'
login_manager.login_message_category = 'info'

#提取mysql的账户密码表
def get_sasl():
    sasl_info=[]
    users=db.session.execute(text('select username,password from can_business_check')).fetchall()
    for i in users:
        user={"name": i._data[0],"password": generate_password_hash(i._data[1]),"id": uuid.uuid4()}
        sasl_info.append(user)
    return sasl_info
sasl_info=get_sasl()     

#根据用户名获得用户记录
def get_user(user_name):
    for user in sasl_info:
        if user.get("name") == user_name:
            return user
    return None

#创建一个用户类,类维护用户的登录状态
class UserL(UserMixin):
    """用户类"""
    def __init__(self, user):
        self.username = user.get("name")
        self.password_hash = user.get("password")
        self.id = user.get("id")

    def verify_password(self, password):
        """密码验证"""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """获取用户ID"""
        return self.id

    @staticmethod
    def get(user_id):
        """根据用户ID获取用户实体，为 login_user 方法提供支持"""
        if not user_id:
            return None
        for user in sasl_info:
            if user.get('id') == user_id:
                return UserL(user)
        return None

# 定义获取登录用户的方法
@login_manager.user_loader  
def load_user(user_id):
    return UserL.get(user_id)

#登录页面
@auth.route('/login',methods=['GET', 'POST'])
def login():
    emsg = None
    if request.method == 'POST':
        user_name = request.form.get('login_usr')
        password = request.form.get('login_password')
        user_info = get_user(user_name)  # 从用户数据中查找用户记录
        if user_info is None:
            emsg = "用户名或密码密码有误"
        else:
            user = UserL(user_info)  # 创建用户实体
            if user.verify_password(password):  # 校验密码
                login_user(user)  # 创建用户 Session
                return redirect(url_for('index'))  #进入密码认证成功的页面
            else:
                emsg = "用户名或密码密码有误"       
    else:
        return  render_template('login.html')  

#登出操作
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('auth.login')) 




















  