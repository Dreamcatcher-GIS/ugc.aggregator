# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import unittest

from dao.map.BaiduMapDAO import BaiduMapDAO

class BaiduMapDaoTest(unittest.TestCase):

    baiduMapDao = BaiduMapDAO()

    def setUp(self):
        print "setUp"

    def test_setNullStrToNull(self):
        self.baiduMapDao.setNullStrToNull('AddressNode_Suzhou_GYYQ')

    def tearDown(self):
        print "tearDown"