# -*- coding:utf-8 -*-
import unittest

from service.map.baidu.SnatcherService import BaiduMapSnatcherService

class GeocodingTest(unittest.TestCase):
    snatcherService=None

    @classmethod
    def setUpClass(cls):
        print "set up..."
        snatcherService = BaiduMapSnatcherService()

    @classmethod
    def tearDownClass(cls):
        print "teardownClass..."

    def test_getAddress(self):
        print "fetchAddressNode"
        # self.snatcherService.fetchAddressNode(113.145877,22.990029,113.147877,22.990029)

if __name__=="__main__":
    unittest.main()