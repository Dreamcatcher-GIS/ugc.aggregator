# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer，LiuYang'

import re
import os

from service.nlp.Sentiment import Sentiment


class HotelNLP(object):

    def __init__(self):
        self.sentiment_parser = Sentiment()
        keywords_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keywords.txt')
        with open(keywords_file,"r") as f:
            self.keywords = [x.strip() for x in f.readlines()]

    def sentiment(self, sent):
        return self.sentiment_parser.classify(sent)

    def viewpoint(self, sent, decoding=None):
        viewpoint = {}
        # 切分句子
        subsents = self.subsentence(sent, decoding)
        for subsent in subsents:
            sentiment_value = None
            for keyword in self.keywords:
                # 判断关键字是否在句子中出现过
                if keyword in subsent:
                    # 计算子句的情感值
                    if sentiment_value == None:
                        sentiment_value = self.sentiment(subsent)
                    # 得到关键字的情感值
                    if keyword.decode("utf-8") not in viewpoint:
                            viewpoint[keyword.decode("utf-8")] = sentiment_value
                    else:
                        viewpoint[keyword.decode("utf-8")] = (viewpoint[keyword.decode("utf-8")] + sentiment_value)/2
        return viewpoint

    '''
    传入句子,切分为子句
    默认输入输出格式为unicode
    '''
    def subsentence(self, sent, decoding=None):
        if decoding != None:
            sent = sent.decode(decoding)
        line_break = re.compile(u'[\r\n]')
        delimiter = re.compile(u'[，。？！；,.?!;]')
        sentences = []
        for line in line_break.split(sent):
            line = line.strip()
            if not line:
                continue
            for sent in delimiter.split(line):
                sent = sent.strip()
                if not sent:
                    continue
                if decoding != None:
                    sentences.append(sent.encode("utf-8"))
                else:
                    sentences.append(sent)
        return sentences