from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('mobile', validators=[DataRequired()],
                           render_kw={'class': 'form-control', 'placeholder': '用户名/邮箱/手机号'})
    password = PasswordField('password', validators=[DataRequired(), Length(6, 128, message="密码长度必须是6-128位")],
                             render_kw={'class': 'form-control', 'placeholder': '密码'})
    imagecode = StringField('imagecode', validators=[DataRequired()],
                            render_kw={'class': 'form-control', 'placeholder': '图片验证码'})
    remeber_me = BooleanField(u'记住我')
    submit = SubmitField(u'登录', render_kw={'class': 'btn btn-lg btn-theme btn-block'})


class RegisterForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(message="请输入用户名")],
                           render_kw={'class': 'form-control', 'placeholder': '昵称'})
    email = StringField('email', validators=[DataRequired(message="请输入邮箱"),
                                             Email(message="邮箱格式不正确")],
                        render_kw={'class': 'form-control', 'placeholder': '邮箱'})
    phonenumber = StringField("phonenumber",
                              validators=[DataRequired(message="请输入手机号"), Regexp("1[34578]\\d{9}", message="手机号不符合规范")],
                              render_kw={'class': 'form-control', 'placeholder': '手机号'})
    password = PasswordField("password",
                             validators=[DataRequired(message="请输入密码"), Length(6, 128, message="密码长度至少是6位")],
                             render_kw={'class': 'form-control', 'placeholder': '密码'})
    password2 = PasswordField("password2",
                              validators=[DataRequired(message="请输入确认密码"), Length(6, 128, message="密码长度至少是6位"),
                                          EqualTo('password', message="两次密码不一致")],
                              render_kw={'class': 'form-control', 'placeholder': '确认密码'})
    submit = SubmitField(u'注册', render_kw={'class': 'btn btn-lg btn-theme btn-block'})

    def validate_username(self, username):
        user = User.query.filter_by(name=username.data).first()
        if user is not None:
            raise ValidationError("昵称已经存在")

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError("邮箱已经存在")

    def validate_phonenumber(self, phonenumber):
        phone = User.query.filter_by(phone=phonenumber.data).first()
        if phone is not None:
            raise ValidationError("手机号已经存在")


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(u'邮箱', validators=[DataRequired(), Email(message='邮箱格式不正确')])
    submit = SubmitField('发送邮件')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(u'密码', validators=[DataRequired()])
    password2 = PasswordField(
        u'确认密码', validators=[DataRequired(),
                             EqualTo('password')])
    submit = SubmitField(u'确认重置')
