from . import admin
from flask import jsonify

import psutil


# CPU监控
@admin.route('/cpuused/')
def data1():
    result = psutil.cpu_percent(1)
    dics = {'dat': float(result)}
    # print(result)
    return jsonify(dics)


# 内存使用率
@admin.route('/memused/')
def data2():
    result = psutil.virtual_memory().percent
    dics = {'dat': float(result)}
    # print(result)
    return jsonify(dics)

