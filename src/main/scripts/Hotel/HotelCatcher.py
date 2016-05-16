# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'


from service.hotel.TuniuService import TuniuService
from service.hotel.xiecheng.DriveServices import XiechengDriverService
import time


class HotelCatcher(object):

    def __init__(self):
        pass

    '''
    抓取酒店链接页
    '''
    def startCrawlListPage(self, service, city):
        # 如果爬取成功，则存储数据
        service.set_city(city)
        while 1:
            if(service.crawlListPage()):
                service.saveListPageInfo()
                # service.closeDriver()
                break
            else:
                service.listPageInfo = []

    '''
    抓取酒店详情页
    '''
    def startCrawlDetail(self, service, city):
        service.set_city(city)
        listPageInfo = list(service.getListPageInfo())
        listPageInfo = listPageInfo[0:]
        loop = 0
        while len(listPageInfo)>0:
            # 从listPageInfo中pop出一个酒店的数据，抓取该酒店的信息
            target = listPageInfo.pop()
            result = False
            while 1:
                if loop > 3:
                    result = False
                    loop = 0
                    print "False at guid:%s,url:%s" % (target[0], target[2])
                    break
                try:
                    result = service.crawlHotelInfo(target)
                    # 如果爬取结果有误，记录循环,重新爬取
                    if result == False:
                        print "Flase %d time"%loop
                        loop += 1
                        continue
                    loop = 0
                    break
                except Exception, e:
                    loop += 1
                    print e
                    time.sleep(10)
                    continue
            if result:
                service.saveHotelInfo()

if __name__ == "__main__":
    hotelCatcher = HotelCatcher()
    hotel_service = TuniuService()
    # hotel_service = XiechengDriverService()

    # hotelCatcher.startCrawlListPage(hotel_service, "南京")
    # 设置爬取的内容
    hotel_service.set_crawl_content(if_crawl_hotel_comment=False,if_crawl_hotel_info=False,if_crawl_hotel_price=True)
    # # 开始爬取
    hotelCatcher.startCrawlDetail(hotel_service,"南京")