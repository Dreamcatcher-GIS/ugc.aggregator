# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import unittest

from service.nlp.HotelNLP import HotelNLP


class HotelNLPTest(unittest.TestCase):

    hotelNLP = HotelNLP()

    s = "整体不错，就是朝阳的房间少"

    def setUp(self):
        print 'setUp...'

    def test_viewpoint(self):
        print self.hotelNLP.viewpoint(self.s,decoding="utf-8")

    def test_sentiment(self):
        print self.hotelNLP.sentiment(self.s)

    def test_subsentence(self):
        print " ".join(self.hotelNLP.subsentence(self.s,decoding="utf-8"))

    def tearDown(self):
        print 'tearDown...'

if __name__ == "__main__":
    unittest.main()