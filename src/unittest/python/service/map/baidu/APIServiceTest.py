# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'


import unittest
from service.map.baidu.APIService import BaiduMapAPIService

class SnatcherServiceTest(unittest.TestCase):

    baidu_map_api_service = BaiduMapAPIService("MviPFAcx5I6f1FkRQlq6iTxc")

    def setUp(self):
        print 'setUp...'

    def test_doGeocoding(self):
        print self.baidu_map_api_service.doGeocoding("安徽省芜湖市鸠江区南阳路")

    def tearDown(self):
        print 'tearDown...'

if __name__ == "__main__":
    unittest.main()