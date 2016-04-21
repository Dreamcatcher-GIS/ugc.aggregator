# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'


import unittest
import os
import codecs
from snownlp import SnowNLP
from snownlp.sentiment import Sentiment


class SnowNLPTest(unittest.TestCase):

    def setUp(self):
        print "setUp"

    def test_sentiment(self):
        s = u"这个电影挺好看的"
        snow = SnowNLP(s)
        print snow.sentiments

    def test_sentences(self):
        s = "这个电影挺好看的，有点好玩"
        snow = SnowNLP(s)
        print snow.sentences

    def test_path(self):
        data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..\\..\\main\\python\\service\\nlp\\neg.txt')
        print data_path

    def test_train(self):
        classifier = Sentiment()
        neg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..\\..\\main\\python\\service\\nlp\\neg.txt')
        pos_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..\\..\\main\\python\\service\\nlp\\pos.txt')
        neg_docs = codecs.open(neg_path, 'r', 'utf-8').readlines()
        pos_docs = codecs.open(pos_path, 'r', 'utf-8').readlines()
        classifier.train(neg_docs, pos_docs)
        classifier.save("sentiment.marshal")

    def test_decode(self):
        neg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..\\..\\main\\python\\service\\nlp\\neg.txt')
        neg_docs = codecs.open(neg_path, 'r', 'utf-8').readlines()
        print neg_docs[0]
        neg_docs[0].encode("utf-8")

    def test_hotel_sentiment(self):
        classifier = Sentiment()
        train_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sentiment.marshal')
        classifier.load(train_file)
        print classifier.classify(u"布丁")

    def tearDown(self):
        print "tearDown"

if __name__ == "__main__":
    unittest.main()
