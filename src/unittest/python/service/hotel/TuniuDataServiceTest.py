# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import unittest

from service.hotel.TuniuDataService import TuniuDataService


class TuniuDataServiceTest(unittest.TestCase):

    data_service = TuniuDataService()

    def setUp(self):
        print 'setUp...'

    def test_get_comm_by_text(self):
        print len(self.data_service.get_comm_by_text("桔子酒店（南京夫子庙店）","酒店",1)["comments_info"])

    def tearDown(self):
        print 'tearDown...'