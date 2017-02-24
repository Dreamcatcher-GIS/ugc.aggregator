# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer,LiuYang'


from service.hotel.TuniuService import TuniuService
from service.hotel.xiecheng.DriveServices import XiechengDriverService
import time


class HotelCatcher(object):

    def __init__(self,service):
        self.service = service
        pass

    '''
    抓取酒店链接页
    '''
    def startCrawlListPage(self, city):
        # 如果爬取成功，则存储数据
        self.service.set_city(city)
        while 1:
            if(self.service.crawlListPage()):
                self.service.saveListPageInfo()
                # service.closeDriver()
                break
            else:
                self.service.listPageInfo = []

    '''
    抓取酒店详情页
    '''
    def startCrawlDetail(self, city):
        self.service.set_city(city)
        listPageInfo = list(self.service.getListPageInfo())
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
                    result = self.service.crawlHotelInfo(target)
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
                self.service.saveHotelInfo()

    '''
    关闭爬取服务
    '''
    def set_service(self,service):
        self.service = service

    '''
    关闭爬取驱动
    '''
    def exit(self):
        self.service.closeDriver()


if __name__ == "__main__":
    hotel_service = TuniuService()
    # hotel_service = XiechengDriverService()
    hotelCatcher = HotelCatcher(hotel_service)
    hotelCatcher.startCrawlListPage("南京")
    # 设置爬取的内容
    #hotel_service.set_crawl_content(if_crawl_hotel_comment=False,if_crawl_hotel_info=False,if_crawl_hotel_price=True)
    # # 开始爬取
    #hotelCatcher.startCrawlDetail("南京")
    hotelCatcher.exit()

