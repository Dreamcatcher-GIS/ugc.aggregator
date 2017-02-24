# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

from selenium.webdriver.common.keys import Keys
from scrapy.http import HtmlResponse
import time
import re
import random
import uuid
import json
import traceback
import datetime

from dao.hotel.HotelDAO import HotelDAO
from dao.hotel.TuniuDao import TuniuDAO
from service.hotel.SuperHotelService import HotelService
from service.nlp.HotelNLP import HotelNLP
from service.map.baidu.APIService import BaiduMapAPIService
from util.geo import CoordTransor
from setting import local_hotel_setting

# 配置数据库
dao_setting = local_hotel_setting


class TuniuService(HotelService):

    def __init__(self):
        HotelService.__init__(self)
        # 酒店dao
        self.hotel_dao = HotelDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])
        # 途牛dao
        self.dao = TuniuDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])
        # 自然语言处理
        self.hotelNLP = HotelNLP()
        # 存放列表页数据
        self.listPageInfo = []
        # 存放酒店详情数据
        self.hotelItem = {}
        # 存放酒店评论数据
        self.commList = []
        # 存放酒店价格数据
        self.priceList = []

        self.ifCrawlHotelInfo = True

        self.__ota_info = "途牛"

    '''
    遍历酒店信息列表页，爬取酒店详情页链接
    '''
    def crawlListPage(self):
        # 打开酒店详情页
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        after_tomorrow = tomorrow + datetime.timedelta(days=1)
        self.openPage(
            "http://hotel.tuniu.com/list/"
            + self._city
            + "p0s0b0"
            + "?checkindate="
            + tomorrow.strftime('%Y-%m-%d')
            + "&checkoutdate="
            + after_tomorrow.strftime('%Y-%m-%d')
        )
        # 记录每页的循环次数(初始值为0)
        loop_num = 0
        # 标识页面是否已经爬取：False为未处理，反之为已处理
        if_handle = False
        # 获取总页面数
        page_num = int(self.driver.find_element_by_xpath("//span[@class='page-num'][last()]/a").text)
        # 遍历所有页
        while page_num >= 1:
            # 循环次数加1
            loop_num += 1
            # 滚动在页面最底下，然后再向上翻一页(为了让"下一页"按钮可以点击)
            self.driver.find_element_by_tag_name("body").send_keys(Keys.END)
            self.driver.find_element_by_tag_name("body").send_keys(Keys.PAGE_UP)
            # 当页面中出现“返前价”字样时，爬取页面并跳转到下一页
            if u"返前价" in self.driver.page_source:
                # 对未解析过的页面进行解析
                if if_handle is False:
                    pageData =  self.driver.execute_script('return pageData')
                    print pageData['list'][0]['pos']
                    self.__parseUrls(self.driver.page_source)
                    print u"获取酒店数为：%d" % len(self.listPageInfo)
                    if_handle = True
                # 跳转到下一页
                try:
                    if u"下一页" in self.driver.page_source:
                        self.driver.find_element_by_xpath("//div[@class='fr page-jump']/span[@class='next']").click()
                        page_num -= 1
                        # 处理标识重新置为未处理
                        if_handle = False
                        # 单页循环次数置为零
                        loop_num = 0
                        time.sleep(random.uniform(3, 6))
                        print page_num
                except Exception, e:
                    print "error happen at clicking next-page"
                    print e
                    # 将当前的错误页保存下来
                    # self.driver.save_screenshot('%s.png'%page_num)
            # 如果单页循环次数不为零，说明没有跳转到下一页
            if loop_num != 0:
                # 循环次数较大的情况下（此处预定为15次）说明页面可能加载失败，跳出循环，否则继续循环获取
                if loop_num < 15:
                    time.sleep(3)
                    continue
                else:
                    break
        return False if page_num > 1 else True

    '''
    抓取酒店信息
    '''
    def crawlHotelInfo(self, target):
        # 打开酒店详情页
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        after_tomorrow = tomorrow + datetime.timedelta(days=1)
        url = target[2].split('?')[0] + "?checkindate=" + tomorrow.strftime('%Y-%m-%d') + "&checkoutdate=" + after_tomorrow.strftime('%Y-%m-%d')
        self.openPage("http://hotel.tuniu.com" + url)
        self.wait(5)
        time.sleep(2)
        response = HtmlResponse(url="My HTML String", body=self.driver.page_source, encoding="utf-8")

        if self.driver.current_url == "http://hotel.tuniu.com/":
            print u"酒店地址失效"
            return False
        # 解析酒店页面信息
        if self.if_crawl_hotel_info is True:
            self.__parseHotelInfo(response, target)

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
            if target[4] > 0:
                comm_type_num = self.__parse_comm_type_num(response)
                is_successful = True
                if comm_type_num["满意"] > 0:
                    # 滚动至"满意"按钮处并进行点击操作
                    # self.scroll_and_click_by_partial_link_text(u"满意", from_bottom=True)
                    self.scroll_and_click_by_xpath("//div[@class='tradeoffConclude']/a[@data='1']", from_bottom=True, sleep_time=0.5)
                    time.sleep(2)
                    is_successful = self.__crawlHotelComment(self.driver, target[0], comm_type_num["满意"], "满意")
                    if is_successful is False:
                        print u"爬取'满意'评论出错"
                        return False
                if comm_type_num["一般"] > 0:
                    # 滚动至"一般"按钮处并进行点击操作
                    self.scroll_and_click_by_xpath("//div[@class='tradeoffConclude']/a[@data='2']", from_bottom=True, sleep_time=0.5)
                    time.sleep(2)
                    is_successful = self.__crawlHotelComment(self.driver, target[0], comm_type_num["一般"], "一般")
                    if is_successful is False:
                        print u"爬取'一般'评论出错"
                        return False
                if comm_type_num["不满意"] > 0:
                    # 滚动至"不满意"按钮处并进行点击操作
                    # self.scroll_and_click_by_partial_link_text(u"不满意", from_bottom=True)
                    self.scroll_and_click_by_xpath("//div[@class='tradeoffConclude']/a[@data='3']", from_bottom=True, sleep_time=0.5)
                    time.sleep(2)
                    is_successful = self.__crawlHotelComment(self.driver, target[0], comm_type_num["不满意"], "不满意")
                    if is_successful is False:
                        print u"爬取'不满意'评论出错"
                        return False
                if is_successful and target[4] - len(self.commList) < 30:
                    return True
                print u"爬取评论长度与事实差距大"
                return False
        return True

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
            if location_id is None:
                location_id = uuid.uuid1()
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
                    "guid": location_id,
                    "x": trans_location[1],
                    "y": trans_location[0],
                    "hotel_name": item["hotel_name"],
                    "city": self._city,
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
                    baseinfo[6] = item["comm_num"] - baseinfo[4] if item["comm_num"] - baseinfo[4] > 0 else 0
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

    '''
    保存抓取的酒店信息
    '''
    def saveHotelInfo(self):
        if self.if_crawl_hotel_comment is True:
            self.dao.saveComments(self.commList)
        if self.if_crawl_hotel_info is True:
            self.dao.saveHotelInfo(self.hotelItem)
        if self.if_crawl_hotel_price is True:
            self.dao.save_room_info(self.priceList)

    '''
    获取酒店列表页数据
    '''
    def getListPageInfo(self):
        return self.dao.getAllUrl(self._city)

    '''
    解析网页，取出酒店详细链接，存储到urlList中
    '''
    def __parseUrls(self, page_source):
        response = HtmlResponse(url="my HTML string",body=page_source,encoding="utf-8")
        # 抽取出每页中的酒店url存储到urlList中
        url_list = response.xpath("//a[@class='name']/@href").extract()
        comment_number_list = response.xpath("//div[@class='comment']/a/span/text()").extract()
        name_list = response.xpath("//a[@class='name']/text()").extract()
        address_list = response.xpath("//span[@class='address']/text()").extract()
        if len(url_list) == len(comment_number_list) == len(name_list) == len(address_list):
            for i in range(0, len(url_list)):
                self.listPageInfo.append({
                    "guid": uuid.uuid1(),
                    "url": url_list[i],
                    "hotel_name": name_list[i],
                    "OTA": "途牛",
                    "comm_num": int(comment_number_list[i]),
                    "address": address_list[i]
                })

    '''
    解析酒店信息
    '''
    def __parseHotelInfo(self, response, target):
        self.hotelItem  = {}
        # 酒店名
        self.hotelItem ['name'] = response.xpath("//span[@id='hotelName']/text()").extract()[0]
        # 酒店类型
        type = response.xpath("//span[@class='types']/text()").extract()
        if len(type) > 0:
            self.hotelItem ['type'] = type[0]
        # 酒店位置
        self.hotelItem ['address'] = re.sub('\s+', '', response.xpath("//span[@class='address']/text()").extract()[0])
        # 设施
        faciText = ""
        faciDom = response.xpath("//div[@class='facilities']")
        faciDomLen = len(response.xpath("//div[@class='facilities']/i"))
        for i in range(1, faciDomLen + 1):
            faciText = faciText + faciDom.xpath("i[%d]/@title"%i).extract()[0]+","
        self.hotelItem ['facility'] = faciText
        ## 获取酒店介绍 ##
        introDom = response.xpath("//div[@class='hotel_introduction_body']")
        introDomLen = len(introDom.xpath("div"))
        # 获取分界线的下标
        def getSplitList(domLen):
            tempList = []
            # 以d为class的div为标题，视作分界线
            for i in range(1, introDomLen+1):
                if "d" in introDom.xpath("div[%d]/@class"%i).extract()[0]:
                    tempList.append(i)
            # 在有分界线的情况下，将dom的长度作为最后的分界
            if len(tempList)>0:
                tempList.append(domLen)
            return tempList
        splitList = getSplitList(introDomLen)
        for i in range(0,len(splitList)-1):
            titleText = introDom.xpath("div[%d]/span/text()"%splitList[i]).extract()[0]
            # 酒店政策
            if u"酒店政策" in titleText:
                policyText = ""
                # 遍历introDom下的div,将每一行按照;;分隔
                for j in range(splitList[i]+1,splitList[i+1]):
                    lineText = introDom.xpath("div[%d]/span/text()"%j).extract()
                    if len(lineText)>1:
                        policyText = policyText + lineText[0] + re.sub("\s+", "", lineText[1]) +";;"
                self.hotelItem ['policy'] = policyText
            # 设施服务
            if u"设施服务" in titleText:
                facilitiesServerText = ""
                for j in range(splitList[i]+1,splitList[i+1]):
                    # 取出div下的所有文本
                    facilitiesText = introDom.xpath("div[%d]//text()"%j).extract()
                    # '酒店设施'这一栏需特殊对待
                    if u"酒店设施" in facilitiesText[1]:
                        for line in facilitiesText:
                            facilitiesServerText = facilitiesServerText + re.sub("\s+", "", line)+ ","
                        facilitiesServerText = facilitiesServerText + ";;"
                    else:
                        lineText = introDom.xpath("div[%d]/span/text()"%j).extract()
                        if len(lineText)>1:
                            facilitiesServerText = facilitiesServerText + lineText[0] + re.sub("\s+", "", lineText[1]) +";;"
                self.hotelItem ['service'] = facilitiesServerText
            # 酒店周边
            if u"酒店周边" in titleText:
                hotelRimText = ""
                for j in range(splitList[i]+1,splitList[i+1]):
                    labelText = introDom.xpath("div[%d]/span[2]/label/text()"%j).extract()
                    hotelRimText = hotelRimText + introDom.xpath("div[%d]/span[1]/text()"%j).extract()[0]
                    for line in labelText:
                        hotelRimText = hotelRimText + re.sub("\s+", "", line) + ","
                    hotelRimText = hotelRimText + ";;"
                self.hotelItem ['hotel_rim'] = hotelRimText
        summary = response.xpath("//div[@class='hotel_introduction_body']//p/text()").extract()
        if len(summary)>0:
            self.hotelItem ['summary'] = summary[0]
        self.hotelItem ['guid'] = uuid.uuid1()
        self.hotelItem ['hotel_id'] = target[0]

    '''
    解析酒店评论类型的数量
    返回字段,如:{"满意":50,"一般":3,"不满意":5}
    '''
    def __parse_comm_type_num(self, response):
        type_num = {}
        satisfaction = response.xpath("//div[@class='tradeoffConclude']/a[@data='1']/@data-count").extract()
        common = response.xpath("//div[@class='tradeoffConclude']/a[@data='2']/@data-count").extract()
        dissatisfaction = response.xpath("//div[@class='tradeoffConclude']/a[@data='3']/@data-count").extract()
        type_num["满意"] = int(satisfaction[0]) if len(satisfaction) > 0 else 0
        type_num["一般"] = int(common[0]) if len(common) > 0 else 0
        type_num["不满意"] = int(dissatisfaction[0]) if len(dissatisfaction) > 0 else 0
        return type_num

    '''
    抓取酒店评论
    '''
    def __crawlHotelComment(self, driver, hotel_id, comm_num, comm_type):
        page_num = comm_num/20 + 1
        # 单页循环次数
        loop_num = 0
        # 标识当前页面是否已经爬取：False为未处理，反之为已处理
        if_handle = False
        # 遍历所有页
        while(page_num>=1):
            # 循环次数加1
            loop_num +=  1
            # 当页面中出现“返前价”字样时，爬取页面并跳转到下一页
            if u"u5 clearfix" in self.driver.page_source:
                # 对未解析过的页面进行解析
                if if_handle==False:
                    # 解析评论
                    if self.__parseHotelComment(self.driver.page_source, hotel_id, comm_type) == False:
                        print u"重复爬取页面"
                        return False
                    if_handle = True
                    # 如果当前是最后一页，抓取完成后直接跳出循环
                    if page_num == 1:
                        break
                # 跳转到下一页
                try:
                    # 当page_num等于0时,即到达评论的最后一页,此时不用点击下一页
                    if u"下一页" in self.driver.page_source:
                        self.scroll_and_click_by_xpath("//div[@id='remarksPage']/a[@class='page-next']", from_bottom=True, refresh_if_failed=False, sleep_time=0.5)
                        page_num -= 1
                        # 处理标识重新置为未处理
                        if_handle = False
                        # 单页循环次数置为零
                        loop_num = 0
                        time.sleep(random.uniform(3,4))
                except Exception, e:
                    print "error happen at clicking of nextpage"
                    print e
                    # 将当前的错误页保存下来
                    # self.driver.save_screenshot('%s.png'%page_num)
            else:
                break

            # 如果单页循环次数不为零，说明没有跳转到下一页
            if loop_num != 0 :
                # 循环次数较大的情况下（此处预定为15次）说明页面可能加载失败，跳出循环，否则继续循环获取
                if loop_num < 15:
                    time.sleep(2)
                    continue
                else:
                    break
        return False if page_num>1 else True

    '''
    解析酒店评论
    如果当前页的数据已经爬取过,则返回False
    '''
    def __parseHotelComment(self, page_source, hotel_id, comm_type):
        response = HtmlResponse(url="My HTML String", body=page_source, encoding="utf-8")
        remarkDom = response.xpath("//div[@class='user_remark_datail']")
        remarkDomLen = len(response.xpath("//div[@class='user_remark_datail']/div"))
        # 记录抓取页的评论内容跟已保存评论的相同数目
        same_num = 0
        for i in range(1, remarkDomLen+1):
            id = uuid.uuid1()
            # 用户名
            username = remarkDom.xpath("div[%d]/div[@class='a1']/div[@class='b2']/text()"%i).extract()
            username = username[0] if len(username) > 0 else ""
            # 评论文本
            remarkText = remarkDom.xpath("div[%d]/div[@class='a2']/div[@class='b2']/p/text()"%i).extract()
            remark = ""
            for str in remarkText:
                remark = remark + re.sub("\s+", "", str)
            # 评论时间
            comm_time = remarkDom.xpath("div[%d]/div[@class='a2']/div[@class='b4']/div[@style='float: right;']/text()"%i).extract()[0]
            # 用户类型
            user_type = ""
            senti_value = None
            viewpoint = None
            try:
                user_type = remarkDom.xpath("div[%d]/div[@class='a1']/div[@class='b3']/text()"%i).extract()[0]
                senti_value = self.hotelNLP.sentiment(remark.encode("utf-8"))
                viewpoint = json.dumps(self.hotelNLP.viewpoint(remark.encode("utf-8"),decoding="utf-8"))
            except:
                traceback.print_exc()
            comm = {"guid":id, "username":username, "remark":remark, "comm_time":comm_time, "user_type":user_type, "hotel_id":hotel_id, "comm_type":comm_type, "senti_value":senti_value, "viewpoint":viewpoint}
            if self.__is_exist_in_comment_list(comm):
                same_num += 1
            else:
                self.commList.append(comm)
        if same_num == remarkDomLen:
            return False
        else:
            return True

    '''
    判断一条评论是否已经保存过
    已保存则返回True
    否则返回False
    '''
    def __is_exist_in_comment_list(self, comm):
        for temp in self.commList:
            if temp["remark"] == comm["remark"]:
                return True
        return False

    '''
    抓取酒店房间数据
    '''
    def __parseHotelRoomInfo(self, page_source, hotel_id):
        response = HtmlResponse(url="My HTML String", body=page_source, encoding="utf-8")
        hotel_price_list_len = len(response.xpath("//div[@class='hotel_price_body']/div"))
        hotel_price_body_dom = response.xpath("//div[@class='hotel_price_body']")
        crawl_time = datetime.datetime.now().strftime('%Y-%m-%d')
        if hotel_price_list_len < 2:
            return False
        else:
            for i in range(2, hotel_price_list_len+1):
                room_item_list_len = len(hotel_price_body_dom.xpath("div[%d]/div[@class='fleft s2']/div[@class='item']"%i))
                room_item_list = hotel_price_body_dom.xpath("div[%d]/div[@class='fleft s2']"%i)
                room_name = hotel_price_body_dom.xpath("div[%d]/div[@class='fleft s1']/div/p[@class='name']/text()"%i).extract()[0]
                if room_item_list_len > 0:
                    for j in range(1, room_item_list_len+1):
                        description = room_item_list.xpath("div[%d]/div[@class='m1 fleft']/span/text()"%(j+1)).extract()[0]
                        bed_type = room_item_list.xpath("div[%d]/div[@class='m2 fleft']/span/text()"%(j+1)).extract()[0]
                        breakfast = room_item_list.xpath("div[%d]/div[@class='m3 fleft']/span/text()"%(j+1)).extract()[0]
                        wifi = room_item_list.xpath("div[%d]/div[@class='m4 fleft']/span/a/text()"%(j+1)).extract()[0]
                        cancel_policy = room_item_list.xpath("div[%d]/div[@class='m5 fleft']/span/a/text()"%(j+1)).extract()[0]
                        price = room_item_list.xpath("div[%d]/div[@class='m6 fleft']//span[@class='digit']/text()"%(j+1)).extract()[0]
                        self.priceList.append({"guid":uuid.uuid1(),"room_name":room_name, "description":description, "bed_type":bed_type, "breakfast":breakfast, "wifi":wifi, "cancel_policy":cancel_policy, "price": int(price),"crawl_time":crawl_time, "hotel_id":hotel_id})

if __name__=="__main__":
    tuniuService = TuniuService()
    # tuniuService.startCrawlUrl("南京")
    # tuniuService.crawlHotelInfo(["2c2a0980-e5b2-11e5-a88b-c47f6d40e3b9", "/detail/232856409?checkindate=2016-03-23&checkoutdate=2016-03-24", "南京", 0])
    tuniuService.crawlHotelInfo(["2c2a0980-e5b2-11e5-a88b-c47f6d40e3b9", "/detail/39867?checkindate=2016-03-23&checkoutdate=2016-03-24##", "南京", 2])
    # tuniuService.saveHotelInfo()
    tuniuService.closeDriver()