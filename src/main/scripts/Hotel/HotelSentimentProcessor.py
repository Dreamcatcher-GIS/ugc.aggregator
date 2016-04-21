# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'


import traceback
import json
from thulac import thulac

from setting import local_hotel_setting
from service.nlp.HotelNLP import HotelNLP
from dao.hotel.TuniuDao import TuniuDAO

dao_setting = local_hotel_setting



dao = TuniuDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])


class HotelSentimentProcessor(object):

    def __init__(self):
        self.dao = TuniuDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])
        self.thu =  thulac("-input cs.txt")
        self.hotelnlp = HotelNLP()

    def set_sentiment_and_viewpoint(self):
        self.thu = thulac("")
        comm_list = dao.get_hotel_comments()
        sentiment_comm_list = []
        for comm in comm_list:
            if comm[7] is None or comm[8] is None:
                sentiment_value = None
                viewpoint = None
                try:
                    sentiment_value = self.hotelnlp.sentiment(comm[2].encode("utf-8"))
                except:
                    print comm[2]
                    traceback.print_exc()
                try:
                    viewpoint = self.hotelnlp.viewpoint(comm[2].encode("utf-8"),decoding="utf-8")
                    viewpoint = json.dumps(viewpoint, ensure_ascii=False)
                except:
                    print comm[2]
                    traceback.print_exc()
                comm = {"guid":comm[0], "senti_value":sentiment_value, "viewpoint":viewpoint}
                sentiment_comm_list.append(comm)
        print len(sentiment_comm_list)
        dao.update_hotel_comm(sentiment_comm_list)

    def count_word_frq(self):
        comm_list = dao.get_hotel_comments()
        sentiment_comm_list = []
        i = 0
        for comm in comm_list:
            i+=1
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
            print i
        print len(sentiment_comm_list)
        dao.update_hotel_comm_word_freq(sentiment_comm_list)

if __name__ == "__main__":
    HotelSentimentProcessor().count_word_frq()