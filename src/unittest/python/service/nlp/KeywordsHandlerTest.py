# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

from service.nlp.KeywordsHandler import KeywordsHandler
import unittest


'''
关键词处理服务
'''
class KeywordsHandlerTest(unittest.TestCase):

    keywordsHandler = KeywordsHandler()

    def setUp(self):
        print 'setUp...'

    def test_extract_keyword(self):
        counter = self.keywordsHandler.extract_keyword()
        print "The number of key is %s"%len(counter)
        for x in counter[0:200]:
            print x[0],x[1]

    def test_extract_keyword_by_thulac(self):
        counter = self.keywordsHandler.extract_keyword_by_thulac()
        print "The number of key is %s"%len(counter)
        for x in counter[0:200]:
            print x[0].decode("utf-8")

    def tearDown(self):
        print 'tearDown...'

if __name__ == "__main__":
    unittest.main()