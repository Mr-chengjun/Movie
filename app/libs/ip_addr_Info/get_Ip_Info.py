import requests, json
import geoip2.database

'''
GeoLite2-City:使用版本为 20190604
下载地址：https://dev.maxmind.com/geoip/geoip2/geolite2/
参考：https://blog.csdn.net/xslxhn/article/details/83867949
'''

import os


class Ip_Info(object):
    """
    返回省份和城市
    如果是本机地址或者局域网，返回None
    """
    # print("当前路径", os.path.join(os.path.abspath(os.path.dirname(__file__)), "GeoLite2-City/GeoLite2-City.mmdb"))

    def __init__(self):
        # print("当前路径", os.path.join(os.path.abspath(os.path.dirname(__file__)), "GeoLite2-City/GeoLite2-City.mmdb"))
        file_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "GeoLite2-City/GeoLite2-City.mmdb")
        self.reader = geoip2.database.Reader(file_dir)

    # 获取ip地址对应的地理位置
    def get_Addr(self, ip):
        try:
            # 载入指定IP相关数据

            response = self.reader.city(ip)
            # 获取国家名字
            country_name_en = response.country.name
            # 中文显示国家名字
            country_name_cn = response.country.names['zh-CN']
            # 获取城市名称
            city_name = response.city.names['ja']  # 到市
            # 获取城市名称（没有市）
            city_name_cn = response.city.names['zh-CN']
            # 获取省名称
            province_name_en = response.subdivisions.most_specific.name
            # 获取省名称(中文显示)
            province_name_cn = response.subdivisions.most_specific.names['zh-CN']
            return {"province_name": province_name_cn, "city_name": city_name}
        except:
            return {"province_name": None, "city_name": None}


ip_info = Ip_Info()
