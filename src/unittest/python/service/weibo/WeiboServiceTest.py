# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import unittest

from service.weibo.WeiboService import WeiboService


class WeiboServiceTest(unittest.TestCase):

    weiboService = WeiboService()

    def setUp(self):
        print 'setUp...'

    def test_get_all_weibo_nearby(self):
        data = self.weiboService.get_all_weibo_nearby(32.06852648986326,118.78607144238758,1384876800,1461772800,120)
        statis_item = self.weiboService.nearby_weibo_statis_wrapper(data)
        print statis_item

    def test_save_weibo_by_cycle(self):
        self.weiboService.saveWeibo_byCycle(31.40456,118.39862,1420045261,1444233600)

    def tearDown(self):
        print 'tearDown...'

if __name__=="__main__":
    unittest.main()