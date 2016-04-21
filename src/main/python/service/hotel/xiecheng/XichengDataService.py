# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import re

from dao.hotel.xiechengdao.xiecheng import xiechengDAO
from setting import local_hotel_setting

# 配置数据库
dao_setting = local_hotel_setting

class XichengDataService(object):

    def __init__(self):
        self.dao = xiechengDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])

    def get_max_distance(self):
        data = self.dao.get_max_distance_data()
        return data

    def get_around_facilities(self):
        data = self.dao.get_around_facilities_data()
        return data
