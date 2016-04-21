# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

from thulac import thulac
import unittest
import os
import codecs


class ThulacTest(unittest.TestCase):

    def setUp(self):
        print "setUp"

    def test_cut(self):
        s = "住宿都是途牛给推荐的，杭州的两天说实话，有点偏，吃饭打车都不太方便，又赶上下雨带着孩子游玩比较费劲。不过住的挺舒服的。南京这个酒店不知道是订单到酒店的问题，还是什么问题，第一天到了，我们要的是两间房1天，可是酒店的订单是1间房2天。而且我们在这个酒店还预定了隔一天的房间，也没有订单。给途牛打电话，说肯定没问题。结果第3天回来，没房。投诉了半天，才解决的（以后还是提前给预定的酒店打电话确认）。在扬州的住宿非常好。"
        thu = thulac("-seg_only")
        print " ".join(thu.cut(s)).decode("utf-8")

    def test_pos(self):
        thu2 = thulac("-input cs.txt") #设置模式为分词和词性标注模式
        # thu2.run() #根据参数运行分词和词性标注程序，从cs.txt文件中读入，屏幕输出结果
        print " ".join(thu2.cut("住宿都是途牛给推荐的，杭州的两天说实话，有点偏，吃饭打车都不太方便，又赶上下雨带着孩子游玩比较费劲")).decode("utf-8")

    def test_cut_from_file(self):
        thu = thulac("-input cs.txt")
        neg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..\\..\\main\\python\\service\\nlp\\pos.txt')
        neg_docs = codecs.open(neg_path, 'r', 'utf-8').readlines()
        for sent in neg_docs:
            try:
                thu.cut(sent.encode("utf-8"))
            except:
                print sent
                continue

    def tearDown(self):
        print "tearDown"

if __name__ == "__main__":
    unittest.main()
