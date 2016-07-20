# -*- coding:utf-8 -*-
__author__ = 'geosmart'

import unittest

from service.map.baidu.SnatcherService import BaiduMapSnatcherService

class PlaceCrawlTest(unittest.TestCase):

    snatcherService=BaiduMapSnatcherService('B3Z9TG0QdQ5omGKLnPqEm3OWeMbogln8')

    @classmethod
    def setUpClass(cls):
        print "set up..."

    def test_getSimplePlaceTest(self):
        #按关键词查询
        #self.snatcherService.fetchAddressNode(113.145877,22.990029,113.147877,22.990029)#测试
        keywords=["购物","酒店","美食","休闲娱乐","交通设施","房地产","金融","医疗","生活服务","汽车服务","教育培训","公司企业","政府机构","丽人"]
        for keyword in keywords:
            self.snatcherService.fetchPlace(113.145877, 22.990029, 113.250943, 23.072378, keyword)

    def test_getPlaceDetail(self):
        self.snatcherService.fetchPlaceDetail(111.235197,21.322359, 118.681503,24.521525, "酒店")

if __name__=="__main__":
    unittest.main()
    #73.072506, 40.102541, 76.949836, 42.352596