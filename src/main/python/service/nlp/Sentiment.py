# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer，LiuYang'

import os
import codecs
from thulac import thulac

from service.nlp.Bayes import Bayes


data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'sentiment.marshal')

class Sentiment():

    def __init__(self):
        self.classifier = Bayes()
        self.thu = thulac("-seg_only")
        train_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sentiment.marshal')
        self.load(train_file)

    '''
    保存训练结果
    '''
    def save(self, fname, iszip=True):
        self.classifier.save(fname, iszip)

    '''
    加载训练结果
    '''
    def load(self, fname=data_path, iszip=True):
        self.classifier.load(fname, iszip)

    '''
    分词并过滤停止词
    '''
    def handle(self, doc):
        words = self.thu.cut(doc)
        words = filter_stop(words)
        return words

    '''
    语料训练
    对输入正负语料进行训练,统计词频
    '''
    def train(self, neg_docs, pos_docs):
        data = []
        for sent in neg_docs:
            data.append([self.handle(sent), 'neg'])
        for sent in pos_docs:
            data.append([self.handle(sent), 'pos'])
        self.classifier.train(data)

    '''
    分类
    将输入的文本进行使用NB分类，通过拉布拉斯平滑得到归一化结果
    '''
    def classify(self, sent):
        ret, prob = self.classifier.classify(self.handle(sent))
        if ret == 'pos':
            return prob
        return 1-prob

stop_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'stopwords.txt')
stop = set()
fr = codecs.open(stop_path, 'r', 'utf-8')
for word in fr:
    stop.add(word.encode("utf-8").strip())
fr.close()

def filter_stop(words):
    return list(filter(lambda x: x not in stop, words))