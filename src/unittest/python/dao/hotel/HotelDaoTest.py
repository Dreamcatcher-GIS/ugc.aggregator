# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'


import unittest
from dao.hotel.HotelDAO import HotelDAO
from setting import local_hotel_setting

# 配置数据库
dao_setting = local_hotel_setting

class HotelDaoTest(unittest.TestCase):

    hotel_dao = HotelDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])

    def setUp(self):
        print "setUp"

    def test_get_hotel_trace_user(self):
        print self.hotel_dao.get_hotel_trace_users('a147089e-0a4f-11e6-a508-84fe22347625')

    def test_get_remarks_by_username(self):
        print self.hotel_dao.get_remarks_by_username('-雅雅-')

    def tearDown(self):
        print "tearDown"