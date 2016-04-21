# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'


import unittest
import random

from dao.weibo.WeiboDAO import WeiboDAO
from setting import setting

db_setting = setting["weibo"]

class WeiboDAOTest(unittest.TestCase):

    weibo_dao = WeiboDAO(db_setting["host"], db_setting["db"], db_setting["user"], db_setting["password"])

    def setUp(self):
        print "setUp"

    def test_get_weibo_accounts(self):
        print len(self.weibo_dao.get_weibo_accounts())

    def test_get_location(self):
        print self.weibo_dao.get_location("安徽 亳州")

    def tearDown(self):
        print "tearDown"