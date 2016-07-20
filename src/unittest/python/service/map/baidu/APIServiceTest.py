# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'


import unittest
import codecs
import re
from service.map.baidu.APIService import BaiduMapAPIService

class SnatcherServiceTest(unittest.TestCase):

    baidu_map_api_service = BaiduMapAPIService("GOnUNZzHBUlVsSbuZIfr8XCCqLRonKjM")

    def setUp(self):
        print 'setUp...'

    def test_doGeocoding(self):
        print self.baidu_map_api_service.doGeocoding(addressText="高淳县镇兴路208-7号，123省道西侧",city='南京')

    def tearDown(self):
        print 'tearDown...'

if __name__ == "__main__":
    unittest.main()