from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError
from app.models import User
from flask_wtf.file import FileAllowed, FileRequired, FileField


# 登录表单
class LoginForm(FlaskForm):
    username = StringField(
        'mobile',
        validators=[
            DataRequired()
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': '用户名/邮箱/手机号'
        })
    password = PasswordField(
        'password',
        validators=[
            DataRequired(),
            Length(6, 128, message="密码长度必须是6-128位")
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': '密码'
        })
    imagecode = StringField(
        'imagecode',
        validators=[
            DataRequired()
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': '图片验证码'
        })
    remeber_me = BooleanField(u'记住我')
    submit = SubmitField(
        u'登录',
        render_kw={
            'class': 'btn btn-lg btn-theme btn-block'
        })


# 注册表单
class RegisterForm(FlaskForm):
    username = StringField(
        'username',
        validators=[
            DataRequired(message="请输入用户名")
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': '昵称'
        })
    email = StringField(
        'email',
        validators=[
            DataRequired(message="请输入邮箱"),
            Email(message="邮箱格式不正确")
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': '邮箱'
        })
    phonenumber = StringField(
        "phonenumber",
        validators=[
            DataRequired(message="请输入手机号"),
            Regexp("1[34578]\\d{9}", message="手机号不符合规范")
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': '手机号'
        })
    password = PasswordField(
        "password",
        validators=[
            DataRequired(message="请输入密码"),
            Length(6, 128, message="密码长度至少是6位")
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': '密码'
        })
    password2 = PasswordField(
        "password2",
        validators=[
            DataRequired(message="请输入确认密码"),
            Length(6, 128, message="密码长度至少是6位"),
            EqualTo('password', message="两次密码不一致")
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': '确认密码'
        })
    submit = SubmitField(
        u'注册',
        render_kw={
            'class': 'btn btn-lg btn-theme btn-block'
        })

    # 验证用户名
    def validate_username(self, username):
        user = User.query.filter_by(name=username.data).first()
        if user is not None:
            raise ValidationError("昵称已经存在")

    # 验证邮箱
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError("邮箱已经存在")

    # 验证手机号
    def validate_phonenumber(self, phonenumber):
        phone = User.query.filter_by(phone=phonenumber.data).first()
        if phone is not None:
            raise ValidationError("手机号已经存在")


# 重置密码请求表单
class ResetPasswordRequestForm(FlaskForm):
    email = StringField(
        u'邮箱',
        validators=[
            DataRequired(),
            Email(message='邮箱格式不正确')
        ])
    submit = SubmitField('发送邮件')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        u'密码',
        validators=[
            DataRequired()
        ])
    password2 = PasswordField(
        u'确认密码',
        validators=[
            DataRequired(),
            EqualTo('password')
        ])
    submit = SubmitField(u'确认重置')


# 用户中心表单
class UserForm(FlaskForm):
    name = StringField(
        label=u"昵称",
        render_kw={
            "class": "form-control",
            "autofocus": "autofocus",
            "placeholder": u"昵称"
        }
    )
    email = StringField(
        label=u"邮箱",
        validators=[
            Email(message=u"邮箱格式不正确")
        ],
        render_kw={
            "class": "form-control",
            "autofocus": "autofocus",
            "placeholder": u"邮箱"
        }
    )
    phone = StringField(
        label=u"phone",
        validators=[
            Regexp("1[34578]\\d{9}", message="手机号不符合规范")
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': '手机号'
        }
    )
    face = FileField('头像', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    info = TextAreaField(
        label=u"简介",
        validators=[

        ],
        render_kw={
            'class': 'form-control',
            "rows": 10
        }
    )
    submit = SubmitField(
        label=u"提交",
        render_kw={
            "class": "btn btn-success"
        }
    )


class CommentForm(FlaskForm):
    content = TextAreaField(
        label=u'评论',
        validators=[
            DataRequired(message=u'评论不能为空')
        ],
        render_kw={
            'id': 'input_content'
        }
    )
    submit = SubmitField(
        label=u"提交评论",
        render_kw={
            "class": "btn btn-success",
            "id": "btn-sub"
        }
    )


class PwdWordForm(FlaskForm):
    old_pwd = PasswordField(
        label=u"旧密码",
        validators=[
            DataRequired(message=u"旧密码不能为空")
        ],
        render_kw={
            "class": "form-control",
            "placeholder": u"请输入旧密码",
            "autofocus":True
        }
    )

    new_pwd = PasswordField(
        label=u"新密码",
        validators=[
            DataRequired(message=u"新密码不能为空"),
            Length(min=6,max=128, message=u"密码的长度为6-128")
        ],
        render_kw={
            "class": "form-control",
            "placeholder": u"请输入新密码"
        }
    )

    submit = SubmitField(
        label=u"修改密码",
        render_kw={
            "class": "btn btn-success"
        }
    )

    def validate_old_pwd(self, filed):
        from flask_login import current_user
        user = User.query.filter_by(name=current_user.name).first()
        if not user.check_password(filed.data):
            raise ValidationError(u"旧密码错误")
