# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import unittest

from service.weibo.APIService import WeiboAPIService


class APIServiceTest(unittest.TestCase):

    weiboAPIService = WeiboAPIService()

    def setUp(self):
        print 'setUp...'

    def test_getUserInfo(self):
        print self.weiboAPIService.getUserInfo("DreamCatcher-GIS")

    def test_getWeibo_nearbyline(self):
        print len(self.weiboAPIService.getWeibo_nearbyline(31.40456,118.39862,1420045261,1444233600)["statuses"])

    def test_get_address_to_geo(self):
        print self.weiboAPIService.get_address_to_geo("南京安达饭店")

    def tearDown(self):
        print 'tearDown...'


if __name__=="__main__":
    unittest.main()

