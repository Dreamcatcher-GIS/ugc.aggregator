# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'


import unittest

from service.map.tian.APIService import TianMapAPIService


class TiandituAPIServiceTest(unittest.TestCase):

    tian_map_api_service = TianMapAPIService()

    def setUp(self):
        print 'setUp...'

    def test_doGeocoding(self):
        print self.tian_map_api_service.tdtGeocoding("江苏省南京市雨花台区燕西线")

    def tearDown(self):
        print 'tearDown...'