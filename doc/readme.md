### 1. 项目情况
入口文件：manager.py
前后台模块：home、admin
模板目录：templates
数据处理模型文件：models.py
表单处理文件：forms.py
视图处理文件：views.py
初始化文件：__init__.py
分为了前后端，前后端分别为home和admin两个
forms作为表单，models作为数据库使用。整体放在app里边
### 2. 使用蓝图来模块化项目
 home、admin两个蓝图
### 3. 数据模型SQLAchemy
#### 1. 定义会员数据模型
id: 编号、name：账号、pwd：密码、email：邮箱
phone：手机号、info：简介、face：头像
addtime：注册时间、uuid：唯一标识符
comments：评论外键关联、userlogs：会员登录日志外键关联
moviecols：电影收藏外键关联
#### 2. 定义会员登录日志数据模型
id：编号
user_id：所属会员编号
ip：最近登录ip地址
addtime：最近登录时间
#### 3. 标签、电影、上映预告数据模型设计
##### 3.1. 定义标签数据模型
id：编号
name：标题
movies：电影外键关联
addtime：创建时间
##### 3.2. 定义电影数据模型
id：编号、title：电影标题、url：电影地址、
info：电影简介、logo：电影封面、start：星级、
playnum：电影播放量、commentnum：电影评论量、tag_id：所属标签、
area：地区、release_time：发布时间、length：电影时长
addtime：添加时间、comments：电影评论外键关联、moviecols：电影收藏外键关联
##### 3.3. 定义上映预告数据模型
id：编号
title：上映预告标题
logo：上映预告封面
addtime：创建时间

#### 4. 评论及收藏电影数据模型设计
##### 4.1. 定义评论数据模型
id：编号
content：评论内容
movie_id：所属电影
user_id：所属用户
addtime：最近登录时间
##### 4.2. 定义收藏电影数据模型
id：编号
movie_id：所属电影
user_id：所属用户
addtime：最近登录时间(收藏时间)

#### 5. 权限及角色数据模型设计
##### 5.1. 定义权限数据模型
id：编号
name：名称
url：地址
addtime：创建时间

##### 5.2. 定义角色数据模型
id：编号
name：名称
auths：权限列表
addtime：创建时间
admins：管理员外键关联

#### 6. 管理员、登录日志、操作日志数据模型设计
##### 6.1. 定义管理员数据模型
id：编号
name：管理员名称
pwd：管理员密码
is_super：是否超级管理员
role_id：角色编号
addtime：创建时间
adminlogs：管理员登录日志外键关联
oplogs：操作日志外键关联

##### 6.2. 定义管理员登录日志数据模型
id：编号
admin_id：所属管理员编号
ip：最近登录IP地址
addtime：最近登录时间

##### 6.3. 定义操作日志数据模型
id：编号
admin_id：所属管理员编号
ip：操作IP地址
reason：操作原因
addtime：创建时间

##### 创建数据库movie，然后创建数据表，运行models.py
进入app 使用命令
```python models.py``` 以创建数据表

##### 会员登录页面搭建
\#登录
@home.route("/login/")
def login():
    return render_template("home/login.html")
 \# 退出
 @home.route("/logout/")
 
 ##### 注册界面的搭建
 @home.register("/register")
 
 #### 在搭建后台管理时，遇到的错误
 https://blog.csdn.net/Darkman_EX/article/details/85288894
https://blog.csdn.net/zhongqiushen/article/details/79162792