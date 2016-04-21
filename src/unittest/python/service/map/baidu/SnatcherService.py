# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import unittest
from service.map.baidu.SnatcherService import  BaiduMapSnatcherService

class SnatcherServiceTest(unittest.TestCase):

    snatcherService = BaiduMapSnatcherService()

    def setUp(self):
        print 'setUp...'

    def test_fetchAddressNode(self):
        self.snatcherService.fetchAddressNode(0,['31.317616,120.732580'],"AddressNode_Suzhou_GYYQ",placeTableName="Place_SuZhou_GYYQ")

    def tearDown(self):
        print 'tearDown...'

if __name__ == "__main__":
    unittest.main()