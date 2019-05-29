# coding:utf8
from . import home
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from .forms import LoginForm, RegisterForm, ResetPasswordRequestForm, ResetPasswordForm
from .email import send_password_reset_email
from app import redis_store, db
from flask import session
from flask_login import current_user
from flask_login import login_user, logout_user, login_required
from app.models import User, UserLog
import uuid  # 唯一标识符


# 主页
@home.route("/")
def index():
    return render_template("home/index.html")


# 会员注册
@home.route("/register/", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        print(form.validate_on_submit())
        data = form.data
        user = User(name=data['username'], email=data['email'], phone=data['phonenumber'], uuid=uuid.uuid4().hex)
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        flash("注册成功", "OK")
        return redirect(url_for("home.login"))
    return render_template("home/register.html", form=form)


# 登录
@home.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # 从前端获取form表单的数据（字典形式）
        data = form.data
        # username = data["username"]
        # password = data["password"]
        # print(data)
        # 从redis中获取图片验证码
        real_image_code = redis_store.get("image_code_%s" % session.get("image_code_id")).decode()
        # 如果验证码None，说明验证码失效
        if real_image_code is None:
            flash("图片验证码失效", "error")
            return redirect(url_for("home.login"))
        # 如果输入的验证码和redis真实值不一样，验证失败
        if data['imagecode'].lower() != real_image_code.lower():
            flash("验证码不正确", "error")
            return redirect(url_for("home.login"))
        # 验证码输入正确
        # 验证用户
        user = User.query.filter_by(name=data['username']).first()
        # 验证用和密码是否正确
        if user is None or not user.check_password(data["password"]):
            flash("用户名或密码错误", "error")
            return redirect(url_for("home.login"))
        login_user(user, data['remeber_me'])
        # 判断是从那个页面跳转到登录页面的
        next_page = request.args.get("next")
        # 如果没有跳转页面，默认设置为登录成功后返回到index页面
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for("home.index")
        # 记录登录日志
        userlog = UserLog(
            user_id=user.id,
            ip=request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()
        return redirect(next_page)
    return render_template("home/login.html", form=form)


# 退出登录
@home.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for("home.login"))


# 电影上映预告轮播图
@home.route('/animation/')
def animation():
    return render_template('home/animation.html')


# 播放
@home.route('/play/')
def play():
    return render_template('home/play.html')


# 修改密码请求
@home.route('/reset_password_request/', methods=['GET', 'POST'])
def reset_password_request():
    # if current_user.is_authenticated:
    #     return redirect(url_for('home.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print(user)
        if user is None:
            flash("用户不存在")
            return redirect(url_for("home.reset_password_request"))
        if user:
            send_password_reset_email(user)
            flash('重置密码邮件已发送，请检查您的电子邮件重置密码')
        return redirect(url_for('home.login'))
    return render_template('home/email/reset_password_request.html', form=form)


# 修改密码
@home.route('/reset_password/<token>/', methods=['GET', 'POST'])
def reset_password(token):
    # if current_user.is_authenticated:
    #     return redirect(url_for('home.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('home.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('密码重置成功')
        return redirect(url_for('home.login'))
    return render_template('home/email/reset_password.html', form=form)


# 会员中心
@home.route("/user/")
def user():
    return render_template("home/user.html")


# 修改密码
@home.route("/pwd/")
def pwd():
    return render_template("home/password.html")


# 评论
@home.route("/comments/")
def comments():
    return render_template("home/comments.html")


# 登录日志
@home.route("/loginlog/")
def loginlog():
    return render_template("home/loginlog.html")


# 电影收藏
@home.route("/moviecol/")
def moviecol():
    return render_template("home/moviecol.html")


# 搜索页面
@home.route("/search/")
def search():
    return render_template("home/search.html")
