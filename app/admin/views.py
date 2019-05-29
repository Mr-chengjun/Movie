from . import admin
from flask import render_template, request, redirect, url_for, flash, session
from app.admin.forms import LoginForm, TagForm, MovieAddForm, PreviewForm
from app.models import Admin, Tag, Movie, Preview
from flask_login import login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import db
from werkzeug.utils import secure_filename
import uuid, os, datetime
from config import Config
from functools import wraps


# 验证登录函数
# 文件名称为：创建时间+uuid+文件的后缀，这样来唯一标识一个文件
# def admin_login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if session["admin"] is None:
#             return redirect(url_for("admin.login", next=request.url))
#         return f(*args, **kwargs)
#
#     return decorated_function


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


# 后台主页
@admin.route("/")
# @admin_login_required
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
            flash(u"密码错误")
            return redirect(url_for("admin.login"))
        login_user(admin)
        session["admin"] = data['name']
        # 判断是从那个页面跳转到登录页面的
        next_page = request.args.get("next")
        # 如果没有跳转页面，默认设置为登录成功后返回到index页面
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for("admin.index")
        return redirect(next_page)
    return render_template("admin/login.html", form=form)


# 后台登出
@admin.route("/logout/")
# @admin_login_required
def logout():
    logout_user()
    session.pop("name", None)
    return redirect(url_for("admin.login"))


# 后台修改密码页面
@admin.route("/pwd/")
# @admin_login_required
def pwd():
    return render_template("admin/password.html")


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
        return redirect(url_for("admin.tag_add"))
    return render_template("admin/tag_add.html", form=form)


# 后台显示标签列表页面
@admin.route("/tag/list/")
# @admin_login_required
def tag_list():
    page_index = request.args.get('page', 1, type=int)
    # 实现分页信息
    pagination = Tag.query.order_by(Tag.addtime.desc()).paginate(page=page_index, per_page=1)
    # tag的信息
    tag_data = pagination.items
    return render_template("admin/tag_list.html", tag_data=tag_data, pagination=pagination)


# 编辑标签页面
@admin.route("/tag/edit/<int:id>", methods=["GET", "POST"])
# @admin_login_required
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
# @admin_login_required
def movie_list():
    page_index = request.args.get('page', 1, type=int)
    # 实现分页信息
    pagination = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page_index, per_page=1)
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
    pagination = Preview.query.order_by(Preview.addtime.desc()).paginate(page=page_index, per_page=1)
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
        form.logo.validators =[]
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
        return redirect(url_for("admin.preview_edit",id=id))
    return render_template("admin/preview_edit.html", form=form, preview=preview)


# 会员列表页
@admin.route("/user/list/")
# @admin_login_required
def user_list():
    return render_template("admin/user_list.html")


# 查看会员详细信息页面
@admin.route("/user/view/")
# @admin_login_required
def user_view():
    return render_template("admin/user_view.html")


# 评论列表页面
@admin.route("/comment/list/")
# @admin_login_required
def comment_list():
    return render_template("admin/comment_list.html")


# 收藏电影列表页面
@admin.route("/movie/collection/list")
# @admin_login_required
def moviecol_list():
    return render_template('admin/moviecol_list.html')


# 操作日志列表页面
@admin.route("/oplog/list/")
# @admin_login_required
def oplog_list():
    return render_template('admin/oplog_list.html')


# 管理员登录日志列表页
@admin.route("/adminlogin/log/list/")
# @admin_login_required
def adminlogin_log_list():
    return render_template('admin/adminlogin_log_list.html')


# 会员登录日志列表页
@admin.route("/userlogin/log/list/")
# @admin_login_required
def userlogin_log_list():
    return render_template('admin/userlogin_log_list.html')


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
@admin.route("/auth/add/")
# @admin_login_required
def auth_add():
    return render_template("admin/auth_add.html")


# 权限列表页
@admin.route("/auth/list/")
# @admin_login_required
def auth_list():
    return render_template("admin/auth_list.html")


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
