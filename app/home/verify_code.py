# coding:utf-8
from . import home
from app.libs.utils.captcha.captcha import captcha
from app.libs.constants import IMAGE_CODE_REDIS_EXPIRES
from flask import current_app, jsonify, make_response
from app.libs.utils.status_code import RET
from app import redis_store
from flask import session

# # 创建redis连接对象
# redis_store = None
# # 初始化redis工具
# redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)


# GET 127.0.0.1/api/v1.0/image_codes/<image_code_id>
@home.route('/image_codes/<image_code_id>')
def get_image_code(image_code_id):
    """
    获取图片验证码
    : params image_code_id：图片验证码编号
    :return: 正常情况下：验证码图片  异常：返回json
    """
    # 业务逻辑处理
    # 生成验证码图片
    # 名字，真实文本，图片数据
    name, text, image_data = captcha.generate_captcha()
    # 将验证码真实值与编号保存到redis中,设置有效期
    # redis中的数据类型：字符串   列表  哈希  set
    # "key": xxx
    # 使用哈希维护有效期的时候只能整体设置，对于本需求来说不是很合理，因为如果有效时间一到，整个数据都会被清除，这样不符合需求
    # "image_codes": {"编号1"："真实文本1","编号2"："真实文本2"}  哈希
    # 在python中
    # 利用命令hset('image_codes',"id1","abc")、
    # hset('image_codes',"id2","def")向redis中添加数据
    # 获取redis中的数据 hget("image_codes",'id1')

    # 单条维护记录，选用字符串
    # "image_code_编号1"："真实值"
    # "image_code_编号2"："真实值"
    # redis_store.set('image_code_%s' % image_code_id, text)
    # 设置有效期, 3分钟有效期
    # redis_store.expire("image_code_%s" % image_code_id, IMAGE_CODE_REDIS_EXPIRES)

    # 将上边两步合成一步写
    #                   记录名字                        有效期                  记录值
    try:
        redis_store.setex('image_code_%s' % image_code_id, IMAGE_CODE_REDIS_EXPIRES, text)
        # 记录验证码到session：https://www.bbsmax.com/A/n2d9bYK0zD/
        session['image_code_id'] = image_code_id

    except Exception as e:
        # 捕获异常，记录日志
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u"save image verify code failed")
    # 返回图片
    resp = make_response(image_data)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp
