from . import admin
from flask import render_template, request, redirect, url_for, flash, session
from app.admin.forms import LoginForm, TagForm, MovieAddForm, PreviewForm, PassWordForm, AuthForm
from app.models import Admin, Tag, Movie, Preview, User, Comment, Moviecol, OpLog, AdminLog, UserLog, Auth
from flask_login import login_user, logout_user, login_required
# from flask_login import login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import db
from werkzeug.utils import secure_filename
import uuid, os, datetime
from config import Config

from functools import wraps


# 上下文处理器
@admin.context_processor
def context_data():
    data = dict(
        online_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        admin_name=session["admin"]
    )
    return data


# 验证登录函数
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# 修改文件名称
# 文件名称为：创建时间+uuid+文件的后缀，这样来唯一标识一个文件
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


# 后台主页
@admin.route("/")
@admin_login_required
# @login_required
def index():
    return render_template("admin/index.html")


# 后台登录页面
@admin.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data["name"]).first()
        print(admin.name, admin.check_password(data["password"]))
        if not admin.check_password(data["password"]):
            flash(u"密码错误", "error")
            return redirect(url_for("admin.login"))
        login_user(admin)
        session["admin"] = data['name']
        session["admin_id"] = admin.id
        adminlog = AdminLog(
            admin_id=admin.id,
            ip=request.remote_addr  # 获取ip地址
        )
        db.session.add(adminlog)
        db.session.commit()
        # 判断是从那个页面跳转到登录页面的
        next_page = request.args.get("next")
        # 如果没有跳转页面，默认设置为登录成功后返回到index页面
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for("admin.index")
        return redirect(next_page)
    return render_template("admin/login.html", form=form)


# 后台登出
@admin.route("/logout/")
@login_required
def logout():
    logout_user()
    session.pop("admin", None)
    session.pop("admin_id", None)
    return redirect(url_for("admin.login"))


# 后台修改密码页面
@admin.route("/pwd/", methods=["GET", "POST"])
# @admin_login_required
def pwd():
    form = PassWordForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=session["admin"]).first()
        admin.set_password(data['new_password'])
        db.session.add(admin)
        db.session.commit()
        flash("修改密码成功,请重新登录", "success")
        return redirect(url_for("admin.logout"))
    return render_template("admin/password.html", form=form)


# 后台添加标签页面
@admin.route("/tag/add/", methods=["GET", "POST"])
# @admin_login_required
def tag_add():
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        tag = Tag.query.filter_by(name=data["tag_name"]).first()
        if tag:
            flash("名称已经存在", "error")
            return redirect(url_for("admin.tag_add"))
        tag = Tag(name=data['tag_name'])
        db.session.add(tag)
        db.session.commit()
        flash("标签添加成功", "success")
        # print(type(session['admin_id']))
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,  # 获取ip地址
            reason="添加标签 %s" % data["tag_name"]
        )
        db.session.add(oplog)
        db.session.commit()
        return redirect(url_for("admin.tag_add"))
    return render_template("admin/tag_add.html", form=form)


# 后台显示标签列表页面
@admin.route("/tag/list/")
@admin_login_required
def tag_list():
    page_index = request.args.get('page', 1, type=int)
    # 实现分页信息
    pagination = Tag.query.order_by(Tag.addtime.desc()).paginate(page=page_index, per_page=Config.PER_PAGE)
    # tag的信息
    tag_data = pagination.items
    return render_template("admin/tag_list.html", tag_data=tag_data, pagination=pagination)


# 编辑标签页面
@admin.route("/tag/edit/<int:id>", methods=["GET", "POST"])
@admin_login_required
def tag_edit(id):
    form = TagForm()
    tag = Tag.query.get_or_404(id)
    if form.validate_on_submit():
        data = form.data
        oldtag = Tag.query.filter_by(name=data["tag_name"]).first()
        if tag.name != data['tag_name'] and oldtag:
            flash("名称已经存在", "error")
            return redirect(url_for("admin.tag_edit", id=id))
        tag.name = data['tag_name']
        db.session.add(tag)
        db.session.commit()
        flash("标签修改成功", "success")
        return redirect(url_for("admin.tag_edit", id=id))
    return render_template("admin/tag_edit.html", form=form, tag=tag)


# 标签的删除
@admin.route("/tag/delete/<int:id>/")
# @admin_login_required
def tag_delete(id=None):
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash("删除标签成功", "success")
    return redirect(url_for("admin.tag_list"))


# 后台添加电影页面
@admin.route("/movie/add/", methods=["GET", "POST"])
# @admin_login_required
def movie_add():
    form = MovieAddForm()
    if form.validate_on_submit():
        data = form.data
        movie = Movie.query.filter_by(title=data["title"]).first()
        if movie:
            flash("该电影已经存在", "error")
            return redirect(url_for("admin.movie"))
        # 上传的电影的文件，url
        movie_url = secure_filename(form.url.data.filename)
        cover_url = secure_filename(form.cover.data.filename)
        if not os.path.exists(Config.UPLOAD_DIR):
            os.makedirs(Config.UPLOAD_DIR)
            # os.chmod(Config.UPLOAD_DIR)
        url = change_filename(movie_url)
        cover = change_filename(cover_url)
        form.url.data.save(Config.UPLOAD_DIR + url)
        form.cover.data.save(Config.UPLOAD_DIR + cover)
        movie = Movie(
            title=data['title'],
            url=url,
            info=data['info'],
            logo=cover,
            score=float(data['score']),
            playnum=0,
            tag_id=int(data['tag_id']),
            area=data['area'],
            release_time=data['release_time'],
            length=data['length']
        )
        db.session.add(movie)
        db.session.commit()
        flash(u"电影添加成功", "success")
        return redirect(url_for("admin.movie_add"))
    return render_template("admin/movie_add.html", form=form)


# 后台电影列表页面
@admin.route("/movie/list/")
@admin_login_required
def movie_list():
    page_index = request.args.get('page', 1, type=int)
    # 实现分页信息
    pagination = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page_index, per_page=Config.PER_PAGE)
    # 电影的信息
    movie_data = pagination.items
    return render_template("admin/movie_list.html", movie_data=movie_data, pagination=pagination)


# 删除电影
@admin.route("/movie/delete/<int:id>/")
def movie_delete(id=None):
    movie = Movie.query.get_or_404(int(id))
    db.session.delete(movie)
    db.session.commit()
    flash("删除电影成功", "success")
    return redirect(url_for("admin.movie_list"))


# 后台修改电影页面
@admin.route("/movie/edit/<int:id>", methods=["GET", "POST"])
# @admin_login_required
def movie_edit(id=None):
    form = MovieAddForm()
    form.url.validators = []
    form.cover.validators = []
    movie = Movie.query.get_or_404(int(id))
    if request.method == "GET":
        form.info.data = movie.info
        form.tag_id.data = movie.tag_id
    if form.validate_on_submit():
        data = form.data
        movie_statu = Movie.query.filter_by(title=data["title"]).first()
        if movie_statu and movie.title != data['title']:
            flash("片名已经存在", "error")
            return redirect(url_for("admin.movie_edit", id=id))

        if not os.path.exists(Config.UPLOAD_DIR):
            os.makedirs(Config.UPLOAD_DIR)
            # os.chmod(Config.UPLOAD_DIR)

        # 更改了视频
        if form.url.data.filename != "":
            movie_url = secure_filename(form.url.data.filename)
            movie.url = change_filename(movie_url)
            form.url.data.save(Config.UPLOAD_DIR + movie.url)

        # 更改了图片
        if form.cover.data.filename != "":
            cover_url = secure_filename(form.cover.data.filename)
            movie.logo = change_filename(cover_url)
            form.cover.data.save(Config.UPLOAD_DIR + movie.logo)
        movie.title = data['title']
        movie.info = data['info']
        movie.score = data['score']
        movie.tag_id = data['tag_id']
        movie.area = data['area']
        movie.length = data['length']
        movie.release_time = data['release_time']
        db.session.add(movie)
        db.session.commit()
        flash(u"电影修改成功", "success")
        return redirect(url_for("admin.movie_edit", id=id))

    return render_template("admin/movie_edit.html", form=form, movie=movie)


# 后台添加预告页面
@admin.route("/preview/add/", methods=["GET", "POST"])
# @admin_login_required
def preview_add():
    form = PreviewForm()
    if form.validate_on_submit():
        data = form.data
        logo_url = secure_filename(form.logo.data.filename)
        if not os.path.exists(Config.UPLOAD_DIR):
            os.makedirs(Config.UPLOAD_DIR)
            # os.chmod(Config.UPLOAD_DIR)
        logo = change_filename(logo_url)
        form.logo.data.save(Config.UPLOAD_DIR + logo)
        preview = Preview(
            title=data['title'],
            logo=logo
        )
        db.session.add(preview)
        db.session.commit()
        flash("添加预告成功", "success")
        return redirect(url_for("admin.preview_add"))
    return render_template("admin/preview_add.html", form=form)


# 电影预告列表页
@admin.route("/preview/list/")
# @admin_login_required
def preview_list():
    page_index = request.args.get('page', 1, type=int)
    # 实现分页信息
    pagination = Preview.query.order_by(Preview.addtime.desc()).paginate(page=page_index, per_page=Config.PER_PAGE)
    # 电影的信息
    preview_data = pagination.items
    return render_template("admin/preview_list.html", preview_data=preview_data, pagination=pagination)


# 删除预告
@admin.route("/preview/delete/<int:id>/")
def preview_delete(id=None):
    preview = Preview.query.get_or_404(int(id))
    db.session.delete(preview)
    db.session.commit()
    flash("删除预告成功", "success")
    return redirect(url_for("admin.preview_list"))


# 后台修改预告页面
@admin.route("/preview/edit/<int:id>", methods=["GET", "POST"])
# @admin_login_required
def preview_edit(id=None):
    form = PreviewForm()
    preview = Preview.query.get_or_404(int(id))
    if request.method == "GET":
        form.title.data = preview.title
        form.logo.validators = []
    if form.validate_on_submit():
        data = form.data
        # 更改了图片
        if form.logo.data.filename != "":
            cover_url = secure_filename(form.logo.data.filename)
            preview.logo = change_filename(cover_url)
            form.logo.data.save(Config.UPLOAD_DIR + preview.logo)
        preview.title = data['title']
        db.session.add(preview)
        db.session.commit()
        flash("修改预告成功", "success")
        return redirect(url_for("admin.preview_edit", id=id))
    return render_template("admin/preview_edit.html", form=form, preview=preview)


# 会员列表页
@admin.route("/user/list/")
# @admin_login_required
@login_required
def user_list():
    page_index = request.args.get('page', 1, type=int)
    # 实现分页信息
    pagination = User.query.order_by(User.addtime.desc()).paginate(page=page_index, per_page=Config.PER_PAGE)
    # 电影的信息
    user_data = pagination.items
    return render_template("admin/user_list.html", user_data=user_data, pagination=pagination)


# 查看会员详细信息页面
@admin.route("/user/view/<int:id>")
# @admin_login_required
def user_view(id):
    user = User.query.get_or_404(id)
    return render_template("admin/user_view.html", user=user)


# 删除会员
@admin.route("/user/delete/<int:id>/")
def user_delete(id=None):
    user = User.query.get_or_404(int(id))
    db.session.delete(user)
    db.session.commit()
    flash("删除用户成功", "success")
    return redirect(url_for("admin.user_list"))


# 评论列表页面
@admin.route("/comment/list/")
# @admin_login_required
@login_required
def comment_list():
    page_index = request.args.get('page', 1, type=int)
    # 实现分页信息
    pagination = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == Comment.user_id
    ).order_by(Comment.addtime.desc()
               ).paginate(page=page_index, per_page=Config.PER_PAGE)
    # 电影的信息
    comm_data = pagination.items
    return render_template("admin/comment_list.html", comm_data=comm_data, pagination=pagination)


# 删除评论
@admin.route("/comment/delete/<int:id>/")
def comment_delete(id=None):
    comment = Comment.query.get_or_404(int(id))
    db.session.delete(comment)
    db.session.commit()
    flash("删除评论成功", "success")
    return redirect(url_for("admin.comment_list"))


# 收藏电影列表页面
@admin.route("/movie/collection/list")
# @admin_login_required
@login_required
def moviecol_list():
    page_index = request.args.get('page', 1, type=int)
    # 实现分页信息
    pagination = Moviecol.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Moviecol.movie_id,
        User.id == Moviecol.user_id
    ).order_by(Moviecol.addtime.desc()
               ).paginate(page=page_index, per_page=Config.PER_PAGE)
    # 电影的信息
    mcl_data = pagination.items
    return render_template("admin/moviecol_list.html", mcl_data=mcl_data, pagination=pagination)


# 删除评论
@admin.route("/moviecol/delete/<int:id>/")
def moviecol_delete(id=None):
    moviecol = Moviecol.query.get_or_404(int(id))
    db.session.delete(moviecol)
    db.session.commit()
    flash("删除收藏成功", "success")
    return redirect(url_for("admin.moviecol_list"))


# 操作日志列表页面
@admin.route("/oplog/list/")
# @admin_login_required
def oplog_list():
    page_index = request.args.get('page', 1, type=int)
    # 实现分页信息
    pagination = OpLog.query.join(
        Admin
    ).filter(
        Admin.id == OpLog.admin_id
    ).order_by(OpLog.addtime.desc()
               ).paginate(page=page_index, per_page=Config.PER_PAGE)
    # 电影的信息
    op_data = pagination.items
    return render_template("admin/oplog_list.html", op_data=op_data, pagination=pagination)


# 管理员登录日志列表页
@admin.route("/adminlogin/log/list/")
# @admin_login_required
def adminlogin_log_list():
    page_index = request.args.get('page', 1, type=int)
    # 实现分页信息
    pagination = AdminLog.query.join(
        Admin
    ).filter(
        Admin.id == AdminLog.admin_id
    ).order_by(AdminLog.addtime.desc()
               ).paginate(page=page_index, per_page=Config.PER_PAGE)
    # 电影的信息
    admin_data = pagination.items
    return render_template("admin/adminlogin_log_list.html", admin_data=admin_data, pagination=pagination)


# 会员登录日志列表页
@admin.route("/userlogin/log/list/")
# @admin_login_required
def userlogin_log_list():
    page_index = request.args.get('page', 1, type=int)
    # 实现分页信息
    pagination = UserLog.query.join(
        User
    ).filter(
        User.id == UserLog.user_id
    ).order_by(UserLog.addtime.desc()
               ).paginate(page=page_index, per_page=Config.PER_PAGE)
    # 电影的信息
    user_data = pagination.items
    return render_template("admin/userlogin_log_list.html", user_data=user_data, pagination=pagination)


# 角色添加
@admin.route("/role/add/")
# @admin_login_required
def role_add():
    return render_template("admin/role_add.html")


# 角色列表页
@admin.route("/role/list/")
# @admin_login_required
def role_list():
    return render_template("admin/role_list.html")


# 添加权限
@admin.route("/auth/add/", methods=["GET", "POST"])
# @admin_login_required
def auth_add():
    form = AuthForm()
    if form.validate_on_submit():
        data = form.data
        auth = Auth.query.filter_by(name=data["name"]).first()
        if auth:
            flash("权限已经存在", "error")
            return redirect(url_for("admin.auth_add"))
        auth = Auth(name=data['name'], url=data["url"])
        db.session.add(auth)
        db.session.commit()
        flash("标签权限成功", "success")
        # print(type(session['admin_id']))
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,  # 获取ip地址
            reason="添加权限 %s" % data["name"]
        )
        db.session.add(oplog)
        db.session.commit()
        return redirect(url_for("admin.auth_add"))
    return render_template("admin/auth_add.html", form=form)


# 权限列表页
@admin.route("/auth/list/")
@admin_login_required
def auth_list():
    page_index = request.args.get('page', 1, type=int)
    # 实现分页信息
    pagination = Auth.query.order_by(Auth.addtime.desc()).paginate(page=page_index, per_page=Config.PER_PAGE)
    # tag的信息
    auth_data = pagination.items
    return render_template("admin/auth_list.html", auth_data=auth_data, pagination=pagination)


# 编辑权限页面
@admin.route("/auth/edit/<int:id>", methods=["GET", "POST"])
@admin_login_required
def auth_edit(id):
    form = AuthForm()
    auth = Auth.query.get_or_404(id)
    if form.validate_on_submit():
        data = form.data
        auth.name = data['name']
        db.session.add(auth)
        db.session.commit()
        flash("权限修改成功", "success")
        return redirect(url_for("admin.auth_edit", id=id))
    return render_template("admin/auth_edit.html", form=form, auth=auth)


# 删除权限
@admin.route("/auth/delete/<int:id>/")
# @admin_login_required
def auth_delete(id=None):
    auth = Auth.query.filter_by(id=id).first_or_404()
    db.session.delete(auth)
    db.session.commit()
    flash("删除权限成功", "success")
    return redirect(url_for("admin.auth_list"))


# 添加管理员
@admin.route("/admin/add/")
# @admin_login_required
def admin_add():
    return render_template("admin/admin_add.html")


# 管理员列表页
@admin.route("/admin/list/")
# @admin_login_required
def admin_list():
    return render_template("admin/admin_list.html")
