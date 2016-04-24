# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import unittest
import json
import time

from service.weibo.WeiboService import WeiboService


class WeiboServiceTest(unittest.TestCase):

    weiboService = WeiboService()

    def setUp(self):
        self.time1 = time.time()
        print 'setUp...'

    def test_get_all_weibo_nearby(self):
        data = self.weiboService.get_all_weibo_nearby(32.06852648986326,118.78607144238758,1384876800,1461772800,120)
        # statis_item = self.weiboService.nearby_weibo_statis_wrapper(data)
        print json.dumps(data)

    def test_get_all_weibo_nearby_async(self):
        data = self.weiboService.get_all_weibo_nearby_async(32.06852648986326,118.78607144238758,1384876800,1461772800,120)
        statis_item = self.weiboService.nearby_weibo_statis_wrapper(data)
        print json.dumps(statis_item)

    def test_save_weibo_by_cycle(self):
        self.weiboService.saveWeibo_byCycle(31.40456,118.39862,1420045261,1444233600)

    def test_get_weibo_users_timeline(self):
        data = self.weiboService.get_weibo_users_timeline("2089426035,3184474850,2791587541,2387367447,3753741655,2868119530,5668346330,1783003347,5048084657")
        print json.dumps(data)

    def test_get_weibo_users_timeline_async(self):
        data = self.weiboService.get_weibo_users_timeline_async("2089426035,3184474850,2791587541,2387367447,3753741655,2868119530,5668346330,1783003347,5048084657")
        print len(data)

    def test_get_weibo_users_timeline_statics(self):
        id_str = "2089426035,3184474850,2791587541,2387367447,3753741655,2868119530,5668346330,1783003347,5048084657"
        data = self.weiboService.get_weibo_users_timeline_statics(id_str)
        print json.dumps(data)

    def tearDown(self):
        self.time2 = time.time()
        print self.time2-self.time1
        print 'tearDown...'

if __name__=="__main__":
    unittest.main()