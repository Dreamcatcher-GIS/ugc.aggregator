# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer，LiuYang'

import csv
from snownlp.sentiment import Sentiment
import jieba.posseg as pseg
from thulac import thulac
from snownlp import normal
from dao.hotel.TuniuDao import TuniuDAO
from setting import local_hotel_setting

dao_setting = local_hotel_setting


class KeywordsHandler(object):

    def __init__(self):
        self.dao = TuniuDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])
        self.thu =  thulac("-input cs.txt")

    def extract_keyword(self):
        sents = []
        comm_list = self.dao.get_hotel_comments()
        # 从语料中读取每一行并切分成子句
        for comm in comm_list:
            sents.extend(normal.get_sentences(comm[2]))
        print "length of sentences:%d"%len(sents)
        # 每个子句进行词性判读
        pos_sents = []
        for sent in sents:
            pos_sents.append(pseg.cut(sent))
        print "length of pos_sents:%d"%len(pos_sents)
        # 分拣出名词,并进行统计
        print "counting"
        noun_dict = {}
        for pos_sent in pos_sents:
            for key,type in pos_sent:
                if type == "n":
                    if key not in noun_dict:
                        noun_dict[key] = 1
                    else:
                        noun_dict[key] = noun_dict[key] + 1
        a = sorted(noun_dict.iteritems(),key=lambda asd:asd[1],reverse=True)
        return a

    def extract_keyword_by_thulac(self):
        sents = []
        comm_list = self.dao.get_hotel_comments()
        # 从语料中读取每一行并切分成子句
        for comm in comm_list:
            sents.extend(normal.get_sentences(comm[2]))
        print "length of sentences:%d"%len(sents)
        # 每个子句进行词性判读
        pos_sents = []
        for sent in sents:
            try:
                pos_sents.append(map(lambda x: x.split("_"), self.thu.cut(sent.encode("utf-8"))))
            except:
                print sent
                continue
        print "length of pos_sents:%d"%len(pos_sents)
        # 分拣出名词,并进行统计
        print "counting"
        noun_dict = {}
        for pos_sent in pos_sents:
            for word in pos_sent:
                if word[1] == "n":
                    if word[0] not in noun_dict:
                        noun_dict[word[0]] = 1
                    else:
                        noun_dict[word[0]] = noun_dict[word[0]] + 1
        a = sorted(noun_dict.iteritems(),key=lambda asd:asd[1],reverse=True)
        return a
