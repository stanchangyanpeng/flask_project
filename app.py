#pip install flask  -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
from flask import Flask,Blueprint
from gevent import pywsgi
from flask import request,url_for,redirect,flash,session
from flask import render_template
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import text
from datetime import timedelta

from flask_login import login_required

#创建一个Web应用的实例”app”
app = Flask(__name__)  # 创建 Flask 应用
app.config['SECRET_KEY'] = '123456cyp' # 设置表单交互密钥

#前端实时同步更新后端数据
app.debug = True

#数据库信息
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123123@10.44.203.30:3306/dimension_dt'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控

db = SQLAlchemy(app)
    
#模板上下文处理函数，可在所有模板中直接调用train_name变量
@app.context_processor
def inject_user():
    user= db.session.execute(text('select username,password from can_business_check')).fetchall()[0][0]
    return dict(train_name=user)
    
#主页面   
@app.route('/', methods=['GET', 'POST'])
@login_required# 需要登录才能访问
def index():
    if request.method == 'POST':  # 判断是否是 POST 请求
        # 获取表单数据
        title = request.form.get('title')  # 传入表单对应输入字段的 name 值
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')  # 显示错误提示
            return redirect(url_for('index'))  # 重定向回主页
        # 保存表单数据到数据库 
        sql_form="INSERT INTO movie(title,year) VALUES ('{}','{}')".format(title,year)
        db.session.execute(text(sql_form))# 插入数据
        db.session.commit()# 提交数据库会话
        flash('Item created.')  # 显示成功创建的提示
        return redirect(url_for('index'))  # 重定向回主页
    else :
        movie=[]
    
    movie_ =db.session.execute(text('select title,year from movie')).fetchall()    
    return render_template('index.html', movies=movie_)

#动态图    
@app.route('/pic')
@login_required
def hello():
    return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'  
    
#404错误页面
@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    return render_template('404.html'), 404  # 返回模板和状态码 

with app.app_context() :
    from views.authlogin import  auth
app.register_blueprint(auth, url_prefix='/auth')  

#启动服务
if __name__ == '__main__':
    server = pywsgi.WSGIServer(('127.0.0.1', 5000), app)
    server.serve_forever()



