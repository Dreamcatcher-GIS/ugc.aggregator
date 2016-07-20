# -*- coding: utf-8 -*-
import traceback

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from scrapy.http import HtmlResponse
from datetime import datetime
import re
import time
import uuid
import random

from dao.hotel.xiechengdao.xiecheng import xiechengDAO
from dao.hotel.HotelDAO import HotelDAO
from service.hotel.SuperHotelService import HotelService
from setting import local_hotel_setting
from service.map.baidu.APIService import BaiduMapAPIService
from util.geo import CoordTransor

dao_setting = local_hotel_setting

class XiechengDriverService(HotelService):

    def __init__(self):
        HotelService.__init__(self)
        # 携程dao
        self.xiechengDao = xiechengDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])
        # 酒店dao
        self.hotel_dao = HotelDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])
        # 存放列表页数据
        self.listPageInfo = []
        # 存放酒店详情数据
        self.hotelItem = {}
        # 存放酒店评论数据
        self.commList = []
        # 存储床价信息
        self.bed = {}
        # 当前ota名称
        self.__ota_info = "携程"


    def crawlListPage(self):
        self.openPage("http://hotels.ctrip.com/hotel/nanjing12#ctm_ref=hod_hp_sb_lst")
        self.driver.implicitly_wait(10)
        # 单页循环次数
        loopNum = 0
        # 标识当前页面是否已经爬取：False为未处理，反之为已处理
        ifHandle = False
        # 获取总页面数
        pageNum = 140
        while(pageNum>=1):
            # 循环次数加1
            loopNum = loopNum + 1
            # 到达页面90%处
            # js="var q=document.documentElement.scrollTop=9600"
            # self.driver.execute_script(js)
            self.driver.find_element_by_tag_name("body").send_keys(Keys.END)
            self.driver.find_element_by_tag_name("body").send_keys(Keys.PAGE_UP)
            # 当页面中出现“返前价”字样时，爬取页面并跳转到下一页
            if u"收藏" in self.driver.page_source:
                # 对未解析过的页面进行解析
                if ifHandle==False:
                    self.__crawllianjie(self.driver.page_source)
                    print u"获取酒店数为：%d"%len(self.listPageInfo)
                    ifHandle = True
                # 跳转到下一页
                try:
                    if u"下一页" in self.driver.page_source:
                        self.driver.find_element_by_partial_link_text(u"下一页").click()
                        #self.driver.find_element_by_xpath("//a[@class='c_down']").click()
                        pageNum = pageNum - 1
                        # 处理标识重新置为未处理
                        ifHandle = False
                        # 单页循环次数置为零
                        loopNum = 0
                        time.sleep(random.uniform(3, 6))
                        print u"页数：" +  str(pageNum)
                except:
                    print "error happen at clicking of nextpage"
            # 如果单页循环次数不为零，说明没有跳转到下一页
            if loopNum != 0:
                # 循环次数较大的情况下（此处预定为15次）说明页面可能加载失败，跳出循环，否则继续循环获取
                if loopNum < 15:
                    time.sleep(3)
                    continue
                else:
                    break
        return False if pageNum > 1 else True

    # 爬取页面链接
    def __crawllianjie(self,page_sourse):
        response = HtmlResponse(url="my HTML string",body=page_sourse,encoding="utf-8")
        hotel_list = response.xpath("//div[@class='searchresult_list ']/ul")
        for hotel in hotel_list:
            url = hotel.xpath("li[@class='searchresult_info_name']/h2/a/@href").extract()[0]
            address = hotel.xpath("li[@class='searchresult_info_name']/p[@class='searchresult_htladdress']/text()").extract()[0]
            commnum = hotel.xpath("li[@class='searchresult_info_judge ']/div/a/span[@class='hotel_judgement']/text()").extract()
            if len(commnum):
                commnum = re.sub('\D','',commnum[0])
                commnum = commnum if len(commnum)>0 else 0
            else:
                commnum = 0
            name = hotel.xpath("li[@class='searchresult_info_name']/h2/a/text()").extract()[0]
            self.listPageInfo.append({
                "guid": uuid.uuid1(),
                "url": url,
                "hotel_name": name,
                "OTA": self.__ota_info,
                "comm_num": int(commnum),
                "address": address
            })


    '''
    保存爬取的酒店列表页数据
    '''
    def saveListPageInfo(self):
        baidu_api_service = BaiduMapAPIService("MviPFAcx5I6f1FkRQlq6iTxc")
        old_location_info = self.hotel_dao.get_locations(self._city)
        old_baseinfo = list(self.hotel_dao.get_baseinfo(self._city, self.__ota_info))
        # 将基础数据中的if_overtime先假设为都已过时
        for i in range(0, len(old_baseinfo)):
            old_baseinfo[i] = list(old_baseinfo[i])
            old_baseinfo[i][5] = 1
        new_locations = []
        new_baseinfo = []
        update_baseinfo = []
        # 遍历将要保存的数据
        for item in self.listPageInfo:
            location_id = None
            # 首先检查该酒店是否已经保存在location表中
            for location in old_location_info:
                if item["hotel_name"] == location[3]:
                    location_id = location[0]
                    break
            # 如果没有则插入一条新的记录到location表中
            if location_id == None:
                location_id = uuid.uuid1()
                geocoding_info = None
                while 1:
                    try:
                        geocoding_info = baidu_api_service.doGeocoding(item["address"], city=self._city)
                        break
                    except:
                        time.sleep(0.5)
                        continue
                if "result" not in geocoding_info:
                    print item["hotel_name"] + "error"
                    continue
                trans_location = CoordTransor.bd09togcj02(bd_lon=geocoding_info["result"]["location"]["lng"], bd_lat=geocoding_info["result"]["location"]["lat"])
                print trans_location
                new_locations.append({
                    "guid":location_id,
                    "x": trans_location[1],
                    "y": trans_location[0],
                    "hotel_name":item["hotel_name"],
                    "city":self._city,
                    "address": item["address"]
                })

            # 根据location的id号到baseinfo表中查询
            # 如果已经存于表中，则更新该条数据
            # 如果没有，则插入一条新的数据
            if_exist = False
            for baseinfo in old_baseinfo:
                if location_id == baseinfo[2]:
                    if_exist = True
                    baseinfo[1] = item["url"]
                    baseinfo[4] = item["comm_num"]
                    baseinfo[5] = 0
                    baseinfo[6] =  item["comm_num"] - baseinfo[4] if item["comm_num"]-baseinfo[4]>0 else 0
                    break
            if not if_exist:
                new_baseinfo.append({
                    "guid":item["guid"],
                    "url":item["url"],
                    "location_id":location_id,
                    "OTA":self.__ota_info,
                    "comm_num":item["comm_num"],
                    "if_overtime":0,
                    "incre_num":item["comm_num"],
                })
        for baseinfo in old_baseinfo:
            update_baseinfo.append({
                "guid":baseinfo[0],
                "url":baseinfo[1],
                "location_id":baseinfo[2],
                "OTA":baseinfo[3],
                "comm_num":baseinfo[4],
                "if_overtime":baseinfo[5],
                "incre_num":baseinfo[6]
            })
        print len(new_locations)
        print len(new_baseinfo)
        print len(update_baseinfo)
        self.hotel_dao.save_locations(new_locations)
        self.hotel_dao.save_baseinfo(new_baseinfo)
        self.hotel_dao.update_baseinfo(update_baseinfo)
        #self.dao.saveListPageInfo(self.listPageInfo)


    def depose(self):
        self.driver.close()

