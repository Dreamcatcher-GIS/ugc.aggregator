# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import unittest
from dao.hotel.TuniuDao import TuniuDAO
from setting import local_hotel_setting

# 配置数据库
dao_setting = local_hotel_setting

class TuniuDAOTest(unittest.TestCase):

    tuniuDAO = TuniuDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])

    def setUp(self):
        print "setUp"

    def test_getAllUrl(self):
        urlList = self.tuniuDAO.getAllUrl(u'南京')
        urlList = list(urlList)
        for i in range(0, len(urlList)):
            if "49fe2e90-f021-11e5-8a75-9dd8c78807c9" == urlList[i][0]:
                print i
        for info in urlList[0:641]:
            if "49fe2e90-f021-11e5-8a75-9dd8c78807c9" == info[0]:
                print info

    def test_get_all_room_info(self):
        room_info = self.tuniuDAO.get_all_room_info()
        url_list = self.tuniuDAO.getAllUrl(u'南京')
        min_index = len(url_list)
        for room in room_info:
            if room[8]=="2016-04-15":
                for x in range(0, len(url_list)):
                    if room[9] == url_list[x][0]:
                        if x < min_index:
                            min_index = x
                            print min_index
                        break
        print min_index

    def test_get_comm_type_num(self):
        print self.tuniuDAO.get_comm_type_num("南京路客酒店公寓")

    def tearDown(self):
        print "tearDown"
