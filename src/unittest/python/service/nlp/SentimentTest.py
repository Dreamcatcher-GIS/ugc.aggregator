# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import unittest
import os
import codecs

from service.nlp.Sentiment import Sentiment


class SentimentTest(unittest.TestCase):

    def setUp(self):
        print 'setUp...'

    def test_sentiment(self):
        classifier = Sentiment()
        print classifier.classify("前台态度超级好,强烈推荐!!")

    def test_train(self):
        classifier = Sentiment()
        neg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..\\..\\..\\..\\main\\python\\service\\nlp\\neg.txt')
        pos_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..\\..\\..\\..\\main\\python\\service\\nlp\\pos.txt')
        with open(neg_path, 'r') as f:
            neg_docs = [x for x in f.readlines()]
        with open(pos_path, 'r') as f:
            pos_docs = [x for x in f.readlines()]
        classifier.train(neg_docs, pos_docs)
        classifier.save("sentiment.marshal")

    def tearDown(self):
        print 'tearDown...'

if __name__ == "__main__":
    unittest.main()