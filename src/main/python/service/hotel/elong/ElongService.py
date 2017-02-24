# -*- coding:utf-8 -*-
__author__ = 'pengshaowei'

import re
import json
import uuid
import time
import random
import datetime
from dao.hotel.HotelDAO import HotelDAO
from dao.hotel.elong.ElongDao import ElongDAO
from service.nlp.HotelNLP import HotelNLP
from service.hotel.SuperHotelService import HotelService
from service.map.baidu.APIService import BaiduMapAPIService
from selenium.webdriver.common.keys import Keys
from util.geo import CoordTransor
from scrapy.http import HtmlResponse

from setting import local_hotel_setting

# 配置数据库
dao_setting = local_hotel_setting

class ElongService(HotelService):
    def __init__(self):
        print '开始爬取艺龙'
        HotelService.__init__(self)
        self.hotel_dao = HotelDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])
        self.dao = ElongDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])
        self.hotelNLP = HotelNLP()
        self.listPageInfo = []
        self.hotelItem = {}
        self.commList = []
        self.priceList = []
        self.ifCrawlHotelInfo = True
        self.__ota_info = "艺龙"

    '''
    1 遍历酒店信息列表页，爬取酒店链接
    '''
    def crawlListPage(self):
        print '开始抓取列表页'
        self.openPage(
            "http://hotel.elong.com/nanjing/"
        )
        # 记录每页的循环次数(初始值为0)
        loop_num = 0
        # 标识页面是否已经爬取：False为未处理，反之为已处理
        if_handle = False

        # 总页面数
        page_num = 0
        hotel_num = int(self.driver.find_element_by_xpath("//span[@class='t24 mr5']").text)
        if hotel_num % 20==0:
            page_num = hotel_num/20
        else:
            page_num = hotel_num/20 + 1

        # 测试 抓取5页
        #page_num = 5

        while page_num>=1:
            loop_num += 1
            self.driver.find_element_by_tag_name("body").send_keys(Keys.END)
            #self.driver.find_element_by_tag_name("body").send_keys(Keys.PAGE_UP)
            if u"返后价" in self.driver.page_source:
                if if_handle == False:
                    self.__parseUrls(self.driver.page_source)
                    print u"获取酒店数为：%d" % len(self.listPageInfo)
                    if_handle = True
                try:
                    #判断是否在加载，若在加载，就等0.1s
                    response = HtmlResponse(url="My HTML String",body=self.driver.page_source,encoding="utf-8")
                    _loading = response.xpath("//div[@id='_loading_']/@style").extract()
                    while 1:
                        if _loading == []:
                            break
                        if u'none' in _loading[0]:
                            break
                        else:
                            #print '正在加载中......'
                            time.sleep(0.1)
                            response = HtmlResponse(url="My HTML String",body=self.driver.page_source,encoding="utf-8")
                            _loading = response.xpath("//div[@id='_loading_']/@style").extract()
                    if u"下一页" in self.driver.page_source:
                        self.driver.find_element_by_xpath("//div[@class='paging1']/a[@class='page_next']").click()
                        page_num -= 1
                        if_handle = False
                        loop_num = 0
                        time.sleep(random.uniform(1, 3))
                except Exception, e:
                    print "error happen at clicking next-page"
                    print e

            if loop_num != 0:
                if loop_num < 15:
                    time.sleep(1)
                    continue
                else:
                    break
        return False if page_num > 1 else True

    '''
    1 解析网页，取出酒店详细链接，存储到urlList中
    '''
    def __parseUrls(self,page_source):
        response = HtmlResponse(url="My HTML String",body=page_source,encoding="utf-8")
        hotel_list = response.xpath("//div[@class='h_list']/div[@class='h_item']")
        for hotel in hotel_list:
            url = hotel.xpath(".//p[@class='h_info_b1']/a/@href").extract()[0]
            name = hotel.xpath(".//p[@class='h_info_b1']/a/@title").extract()[0]
            address = hotel.xpath(".//p[@class='h_info_b2']/text()").extract()[1]
            commnum = hotel.xpath(".//div[@class='h_info_comt']/a/span[@class='c555 block mt5']/b/text()").extract()
            if len(commnum)==0:
                commnum = 0
            else:commnum = commnum[0]
            self.listPageInfo.append({
                "guid": uuid.uuid1(),
                "url": url,
                "hotel_name": name,
                "OTA": self.__ota_info,
                "comm_num": commnum,
                "address": address
            })
            pass

    '''
    1 保存爬取的酒店列表页数据
    '''
    def saveListPageInfo(self):
        print "开始保存"
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
            if location_id is None:
                location_id = uuid.uuid1()
                while 1:
                    try:
                        geocoding_info = baidu_api_service.doGeocoding(item["address"], city=self._city)
                        if "result" not in geocoding_info:
                            geocoding_info = baidu_api_service.doGeocoding(item["hotel_name"], city=self._city)
                        break
                    except:
                        time.sleep(0.5)
                        continue
                if "result" not in geocoding_info:
                    print item["hotel_name"] + "error"
                    continue
                trans_location = CoordTransor.bd09togcj02(bd_lon=geocoding_info["result"]["location"]["lng"], bd_lat=geocoding_info["result"]["location"]["lat"])
                #trans_location = [geocoding_info["result"]["location"]["lng"], geocoding_info["result"]["location"]["lat"]]
                #print trans_location
                new_locations.append({
                    "guid": location_id,
                    "x": trans_location[1],
                    "y": trans_location[0],
                    "hotel_name": item["hotel_name"],
                    "city": self._city
                })
            if_exist = False
            for baseinfo in old_baseinfo:
                if location_id == baseinfo[2]:
                    if_exist = True
                    baseinfo[1] = item["url"]
                    baseinfo[6] = int(item["comm_num"]) - int(baseinfo[4])
                    baseinfo[4] = item["comm_num"]
                    baseinfo[5] = 0
                    #baseinfo[6] = item["comm_num"] - baseinfo[4] if item["comm_num"] - baseinfo[4] > 0 else 0
                    break
            if not if_exist:
                new_baseinfo.append({
                    "guid": item["guid"],
                    "url": item["url"],
                    "location_id": location_id,
                    "OTA": self.__ota_info,
                    "comm_num": item["comm_num"],
                    "if_overtime": 0,
                    "incre_num": item["comm_num"],
                })
        for baseinfo in old_baseinfo:
            update_baseinfo.append({
                "guid": baseinfo[0],
                "url": baseinfo[1],
                "location_id": baseinfo[2],
                "OTA": baseinfo[3],
                "comm_num": baseinfo[4],
                "if_overtime": baseinfo[5],
                "incre_num": baseinfo[6]
            })
        print len(new_locations), len(new_baseinfo), len(update_baseinfo)
        self.hotel_dao.save_locations(new_locations)
        self.hotel_dao.save_baseinfo(new_baseinfo)
        self.hotel_dao.update_baseinfo(update_baseinfo)
        pass
    '''
    2判断网址是否正确，有无alert
    '''
    def isAlertPresent(self):
        try:
            alert = self.driver.switch_to_alert()
            alert.accept()
            return True
        except :
            return False
    '''
    2 抓取酒店信息
    '''
    def crawlHotelInfo(self,target):
        #target来自于baseinfo表
        url = target[1]
        self.openPage("http://hotel.elong.com"+url)

        self.wait(3)
        time.sleep(random.uniform(1,3))
        # 如果网址失效 return

        if self.isAlertPresent():
            return False

        response = HtmlResponse(url="My HTML String", body=self.driver.page_source, encoding="utf-8")
        # 解析酒店页面信息
        if self.if_crawl_hotel_info is True:
            self.__parseHotelInfo(response, target)
            pass

        # 解析酒店房间信息
        if self.if_crawl_hotel_price is True:
            record_time = 0
            while 1:
                try:
                    self.priceList = []
                    self.__parseHotelRoomInfo(self.driver.page_source, target[0])
                    break
                except:
                    time.sleep(2)
                    record_time += 1
                if record_time > 3:
                    break
        # 抓取酒店点评
        if self.if_crawl_hotel_comment is True:
            self.commList = []
            # TODO 若评论数大于0   冗余可改
            if target[4]>0:
                self.driver.find_element_by_xpath("//body").send_keys(Keys.END)
                self.wait(2)
                read_time = 0
                comm_page_num = ''
                while 1:
                    try:
                        response = HtmlResponse(url="My HTML String", body=self.driver.page_source, encoding="utf-8")
                        hotelname = ""
                        page_a = response.xpath("//div[@id='comment_paging']/a")

                        if len(page_a)==1 :
                            comm_page_num = page_a.xpath(".//text()").extract()[0]
                        if len(page_a)>1:
                            comm_page_num = page_a.xpath(".//text()").extract()[-2]
                    except Exception , e:
                        print e
                    time.sleep(1)
                    read_time+=1
                    if read_time>10:#10次等待
                        break
                    if comm_page_num != '':
                        break

                print "评论共有:",comm_page_num,"页"
                if self.__crawlHotelComment(self.driver, target[0], comm_page_num):
                    print ""
                    print "共抓取了",len(self.commList),"条评论，存储到commList中"

        return True

    '''
    2 解析酒店信息
    '''
    def __parseHotelInfo(self, response, target):
        self.hotelItem  = {}
        #酒店名
        self.hotelItem ['guid'] = uuid.uuid1()
        self.hotelItem ['city'] = self._city
        self.hotelItem ['name'] = response.xpath("//div[@class='t24 yahei']/@title").extract()[0]
        #酒店类型
        type = response.xpath("//div[@class='t24 yahei']/b/@title").extract()
        if len(type)!=0:
            self.hotelItem ['type'] = type[0]
        #酒店位置
        self.hotelItem ['address'] =  response.xpath("//span[@class='mr5 left']/text()").extract()[1]
        #酒店价格
        price = response.xpath("//div[@class='hrela_price']/p/span[@class='cf55']/text()").extract()
        if len(price)!=0:
            self.hotelItem ['price'] = price[0]
        #酒店好评率
        recommend = response.xpath("//div[@class='pertxt_num']/text()").extract()
        if len(recommend)!=0:
            self.hotelItem ['recommend'] = recommend[0]
        #酒店服务分数
        score = response.xpath("//span[@class='cf55 t18']/text()").extract()
        if len(score)!=0:
            self.hotelItem ['score'] = score[0]
        #酒店评论数量
        discuss = response.xpath("//div[@class='hrela_comt_total']/a/text()").extract()
        if len(discuss)!=0:
            self.hotelItem ['discussNum'] = discuss[0]
        #酒店 九大基础信息
        dviewli = response.xpath("//ul[@class='dview_icon_list']/li")
        dataview = ''
        for li in dviewli:
            if li.xpath(".//@class").extract()[0] != "no":
                dataview += li.xpath(".//p/text()").extract()[0]
        self.hotelItem ['dataview'] = dataview
        #酒店详细信息
        dllist = response.xpath("//div[@class='dview_info']/dl")
        for dl in dllist:
            dltitle = dl.xpath(".//dt/text()").extract()
            #其他信息也可写在此for中，如 酒店电话 等
            #酒店简介
            if u'酒店简介' in dltitle:
                self.hotelItem ['summary'] = dl.xpath(".//dd/p/text()").extract()[0].strip()
            #酒店设施
            if u'酒店设施' in dltitle:
                self.hotelItem ['facility'] = dl.xpath(".//dd/p/text()").extract()[0].strip()
        self.hotelItem ['hotel_id'] = target[0]
        #打印
        #for i in self.hotelItem:
            #print i +":"+ self.hotelItem[i]

    '''
    2 抓取酒店房间数据
    '''
    def __parseHotelRoomInfo(self, page_source, hotel_id):
        response = HtmlResponse(url="My HTML String", body=page_source, encoding="utf-8")
        rooms_list = response.xpath("//div[@class='htype_list']/div")
        rooms_list_len = len(rooms_list)
        if rooms_list_len<0:
            return False
        crawl_time = datetime.datetime.now().strftime('%Y-%m-%d')
        for rooms in rooms_list:
            #房间名称
            roomname = rooms.xpath(".//p[@class='htype_info_name']/span/text()").extract()[0]
            #房间大小
            roomarea = rooms.xpath(".//p[@class='htype_info_ty']/span[1]/text()").extract()
            if len(roomarea)!=0:
                roomarea = roomarea[0]
            else:
                roomarea = ''
            #床型
            bedtype = rooms.xpath(".//p[@class='htype_info_ty']/span[3]/text()").extract()
            if len(bedtype)!=0:
                bedtype = bedtype[0]
            else:
                bedtype = ''
            #人数
            havenum = rooms.xpath(".//p[@class='htype_info_ty']/span[3]/span/text()")
            if havenum:
                peoplecount = str(havenum.extract()[0])
            else:
                peoplecount = str(len(rooms.xpath(".//p[@class='htype_info_ty']/span[5]/i")))
            if peoplecount == '0':
                peoplecount = '未说明'
            #楼层
            roomsfloor = rooms.xpath(".//p[@class='htype_info_ty']/span[7]/text()").extract()
            if len(roomsfloor)!=0:
                roomsfloor = roomsfloor[0]
            else:
                roomsfloor = ''
            havewifi = rooms.xpath(".//p[@class='htype_info_ty']/span[9]/text()").extract()
            if len(havewifi)!=0:
                havewifi = havewifi[0]
            else:
                havewifi = ''
            list = rooms.xpath(".//table[@class='htype-table']/tbody/tr[@data-handle='rp']")
            descriptions = rooms.xpath(".//td[@class='ht_other']//p/text()").extract()
            description = ''
            for d in descriptions:
                dstrip = d.strip()
                if u'查看更多产品报价' != dstrip:
                    description +=dstrip
            for room in list:
                roomtype = room.xpath(".//td[@class='ht_name']/span/text()").extract()[0]
                supply = room.xpath(".//td[@class='ht_supply']/text()").extract()[0].strip()
                breakfast =  room.xpath(".//td[@class='ht_brak']/text()").extract()[0]
                rule = room.xpath(".//td[@class='ht_rule']/span/text()").extract()[0]
                price = room.xpath(".//td[@class='ht_pri']/span[@class='ht_pri_h cur']/span/text()").extract()[0]
                self.priceList.append({
                    'guid':uuid.uuid1(),
                    'room_name':roomname,
                    'room_area':roomarea,
                    'bed_type':bedtype,
                    'people_count':peoplecount,
                    'rooms_floor':roomsfloor,
                    'wifi':havewifi,
                    'description':description,
                    'room_type':roomtype,
                    'supply':supply,
                    'breakfast':breakfast,
                    'cancel_policy':rule,
                    'price':price,
                    'crawl_time':crawl_time,
                    'hotel_id':hotel_id
                })
                pass

        #for i in self.priceList:
            #for j in i :
                #print j ,':',i[j]
            #print '------------------------------------------------'

    '''
    2 保存抓取的酒店信息
    '''
    def saveHotelInfo(self):
        if self.if_crawl_hotel_comment is True:
            self.dao.saveComments(self.commList)
        if self.if_crawl_hotel_info is True:
            self.dao.saveHotelInfo(self.hotelItem)
        if self.if_crawl_hotel_price is True:
            self.dao.save_room_info(self.priceList)

    '''
    2 获取酒店列表页数据
    '''
    def getListPageInfo(self):
        return self.dao.getAllUrl()
        pass

    '''
    2 抓取酒店评论
    '''
    def __crawlHotelComment(self,driver,hotel_id ,pagenum):
        pagenum = int(pagenum)
        # 遍历所有页
        while pagenum>=1:
            response = HtmlResponse(url="My HTML String", body=self.driver.page_source, encoding="utf-8")
            loading = response.xpath("//div[@id='commentLoading']/@style").extract()[0]
            #当加载不显示时，才爬取
            while loading!=u'display: none;':
                print '正在加载......'
                time.sleep(0.1)
                response = HtmlResponse(url="My HTML String", body=self.driver.page_source, encoding="utf-8")
                loading = response.xpath("//div[@id='commentLoading']/@style").extract()[0]
            itemlist =  response.xpath("//ul[@class='dcomt_list']/li")
            for item in itemlist:
                username = item.xpath(".//div[@class='dcomt_head left']/div[2]/span/text()").extract()[0]
                remarkText = item.xpath(".//p[@class='dcomt_con_txt']/text()").extract()[0]
                #TODO 过滤 非中文字符 待修改
                remarkText = remarkText.encode("gbk",'ignore')
                remarkText = remarkText.decode("gbk")
                remark = ''
                for string in remarkText:
                    remark = remark + re.sub("\s+", "", string)
                user_type = item.xpath(".//div[@class='dcomt_head_pic']/p/text()").extract()[0]
                comm_time = item.xpath(".//span[@class='dcomt_con_time']/text()").extract()[0]
                goodorbad = item.xpath(".//p[@class='mb5']/i/@class").extract()[0]
                comm_type = ''
                if u'good' in  goodorbad:
                    comm_type = "值得推荐"
                if u'bad' in goodorbad:
                    comm_type = "有待改善"
                senti_value = self.hotelNLP.sentiment(remark.encode("utf-8"))
                viewpoint = json.dumps(self.hotelNLP.viewpoint(remark.encode("utf-8"),decoding="utf-8"))
                comm ={
                    "guid":uuid.uuid1(),
                    "username":username,
                    "remark":remark,
                    "comm_time":comm_time,
                    "user_type":user_type,
                    "comm_type":comm_type,
                    "senti_value":senti_value,
                    "viewpoint":viewpoint,
                    "baseinfo_id":hotel_id
                }
                if self.__is_exist_in_comment_list(comm) is False:
                    self.commList.append(comm)
                else:
                    #print comm['remark']
                    pass
            if pagenum == 1:
                break
            #点下一页
            self.scroll_and_click_by_xpath("//div[@id='comment_paging']/a[@class='page_next']")
            pagenum  -= 1
            time.sleep(random.uniform(1,4))
            print pagenum
        return True

    '''
    2 判断一条评论是否已经保存过
        已保存则返回True，否则返回False
    '''
    def __is_exist_in_comment_list(self, comm):
        for temp in self.commList:
            if temp["remark"] == comm["remark"]:
                return True
        return False

if __name__ == "__main__":
    elongservice = ElongService()
    # 爬取列表页
    #elongservice.crawlListPage()
    #elongservice.saveListPageInfo()
    # 爬取详情页
    elongservice.crawlHotelInfo(["83fe65cf-5352-11e6-b8a1-70188b049ec0","/nanjing/51101001/","","",23])
    #elongservice.crawlHotelInfo(["83fe8cde-5352-11e6-b554-70188b049ec0","/nanjing/31101011/","","",6621])
    # 关闭驱动
    #elongservice.closeDriver()
    pass

