# -*- coding:utf-8 -*-
import re

__author__ = 'DreamCathcer'


import traceback
import json
from thulac import thulac

from setting import local_hotel_setting
from service.nlp.HotelNLP import HotelNLP
from dao.hotel.TuniuDao import TuniuDAO
from dao.hotel.HotelDAO import HotelDAO

dao_setting = local_hotel_setting


class HotelSentimentProcessor(object):

    def __init__(self):
        self.hotel_dao = HotelDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])
        self.dao = TuniuDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])

    def set_sentiment_and_viewpoint(self):
        self.hotelnlp = HotelNLP()
        self.thu = thulac("")
        comm_list = self.hotel_dao.get_remarks()
        print len(comm_list)
        sentiment_comm_list = []
        i = 0
        for comm in comm_list:
            if comm[8] is None or comm[9] is None:
                sentiment_value = None
                viewpoint = None
                remark = re.sub(u"\@",u"",comm[2])
                try:
                    sentiment_value = self.hotelnlp.sentiment(remark.encode("utf-8"))
                    sentiment_value = round(sentiment_value*1000)/1000
                    print sentiment_value
                except:
                    print comm[2]
                    traceback.print_exc()
                try:
                    viewpoint = self.hotelnlp.viewpoint(remark.encode("utf-8"),decoding="utf-8")
                    viewpoint = json.dumps(viewpoint, ensure_ascii=False)
                except:
                    print remark
                    traceback.print_exc()
                comm = {"guid":comm[0], "senti_value":sentiment_value, "viewpoint":viewpoint}
                sentiment_comm_list.append(comm)
            if len(sentiment_comm_list)==10000:
                i+=1
                print "update %d time"%i
                self.hotel_dao.update_remarks(sentiment_comm_list)
                sentiment_comm_list = []


    def count_word_frq(self):
        self.thu =  thulac("-input cs.txt")
        comm_list = self.hotel_dao.get_remarks()
        sentiment_comm_list = []
        i = 0
        for comm in comm_list:
            a_dict = {}
            try:
                cut_comm = map(lambda x: x.split("_"), self.thu.cut(comm[2].encode("utf-8")))
            except:
                cut_comm = []
                print comm[2]
                traceback.print_exc()
            for word in cut_comm:
                if word[1].decode("utf-8") == "a":
                    if word[0].decode("utf-8") not in a_dict:
                        a_dict[word[0].decode("utf-8")] = 1
                    else:
                        a_dict[word[0].decode("utf-8")] += 1
            comm = {"guid":comm[0], "word_freq":json.dumps(a_dict, ensure_ascii=False)}
            sentiment_comm_list.append(comm)
            if len(sentiment_comm_list)==10000:
                i+=1
                print "update %d time"%i
                self.hotel_dao.update_hotel_comm_word_freq(sentiment_comm_list)
                sentiment_comm_list = []

if __name__ == "__main__":
    HotelSentimentProcessor().count_word_frq()