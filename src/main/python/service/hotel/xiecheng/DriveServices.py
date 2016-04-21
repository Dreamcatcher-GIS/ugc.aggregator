# -*- coding: utf-8 -*-
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
from setting import local_hotel_setting

dao_setting = local_hotel_setting

class XiechengDriverService(object):

    def __init__(self):
        # self.driver = webdriver.Chrome()
        self.xiechengDao = xiechengDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])
        # 存放列表页数据
        self.listPageInfo = []
        # 存放酒店详情数据
        self.hotelItem = {}
        # 存放酒店评论数据
        self.commList = []
        # 存储床价信息
        self.bed = {}





    # 打开携程首页
    def start(self):
        self.driver.get("http://hotels.ctrip.com/hotel/nanjing12#ctm_ref=hod_hp_sb_lst")
        # 将界面最大化
        self.driver.maximize_window()
        self.driver.implicitly_wait(30)
        self.crawlxiecheng()


    def crawlxiecheng(self):
        # 单页循环次数
        loopNum = 0
        # 标识当前页面是否已经爬取：False为未处理，反之为已处理
        ifHandle = False
        # 获取总页面数
        pageNum = 280
        while(pageNum>=1):
            # 循环次数加1
            loopNum = loopNum + 1
            # 到达页面90%处
            js="var q=document.documentElement.scrollTop=9000"
            self.driver.execute_script(js)
            # 当页面中出现“返前价”字样时，爬取页面并跳转到下一页
            if u"收藏" in self.driver.page_source:
                # 对未解析过的页面进行解析
                if ifHandle==False:
                    self.crawllianjie(self.driver.page_source)
                    ifHandle = True
                # 跳转到下一页
                try:
                    if u"下一页" in self.driver.page_source:
                        # self.driver.find_element_by_partial_link_text(u"下一页").click()
                        pageNum = pageNum - 1
                        self.driver.find_element_by_xpath("//a[@class='c_down']").click()
                        # 处理标识重新置为未处理
                        ifHandle = False
                        # 单页循环次数置为零
                        loopNum = 0
                        time.sleep(random.uniform(3, 6))
                        print "页数：" +  str(pageNum)
                except :
                    pageNum = pageNum + 1
                    # 将当前的错误页保存下来
                    # self.driver.save_screenshot('%s.png'%pageNum)
            # 如果单页循环次数不为零，说明没有跳转到下一页
            if loopNum != 0:
                # 循环次数较大的情况下（此处预定为15次）说明页面可能加载失败，跳出循环，否则继续循环获取
                if loopNum < 15:
                    time.sleep(3)
                    continue
                else:
                    break
        return False if pageNum > 1 else True
    # 爬取酒店基本信息
    def pagecollect(self,response):
        items = []
        commentData = response.xpath("//div[@id='hotel_list']/div[@class='searchresult_list ']/ul[@class='searchresult_info']")

        for itemData in commentData:
            itemDict = dict()

            # 唯一标识
            itemDict['guid'] = uuid.uuid1()

            # 城市名
            itemDict["city"] = "南京"

            # 名称
            itemDict["title"] = itemData.xpath("li/h2/a[@title]/text()").extract()[0]

            # 价格
            price = itemData.xpath("li[@class='hotel_price_icon']/div/span/text()").extract()[0]
            if price:
                itemDict["price"] = price
            else:
                itemDict["price"] = ""

            # 评分
            score = itemData.xpath("li[@class='searchresult_info_judge ']/div/a/span[@class='hotel_value']/text()").extract()[0]
            if score:
                itemDict["score"] = score
            else:
                itemDict["score"] = " "

            # 位置
            location = itemData.xpath("li[@class='searchresult_info_name']/p[@class='searchresult_htladdress']/text()").extract()[0]
            Location = location.split(" ")
            if(Location):
                itemDict["location"] = Location[0]
            else:
                itemDict["location"] = " "

            # 评论
            discussnum = itemData.xpath("li[@class='searchresult_info_judge ']/div/a/span[@class='hotel_judgement']/text()").extract()[0]
            Discuss = re.sub('\D','',discussnum)
            if Discuss:
                itemDict["discussnum"] = Discuss
            else:
                itemDict["discussnum"] = ""

            # 有无wifi
            havewifi1 = itemData.xpath("li[@class='searchresult_info_name']/div[@class='icon_list']/i[@class='icons-facility32']")
            havawifi2 = itemData.xpath("li[@class='searchresult_info_name']/div[@class='icon_list']/i[@class='icons-facility01']")
            if (havewifi1 or havawifi2):
                itemDict["havawifi"] = "yes"
            else:
                itemDict["havawifi"] = "no"

            # 用户推荐百分比
            recommend = itemData.xpath("li[@class='searchresult_info_judge ']/div[@class='searchresult_judge_box']/a/span[@class='total_judgement_score']/text()").extract()[1]
            Recommend = re.sub('\D','',recommend)
            Recommend += "%"
            if Recommend:
                itemDict["recommend"] = Recommend
            else:
                itemDict["recommend"] = " "

            items.append(itemDict)
        return items


    # 爬取页面链接
    def crawllianjie(self,page_sourse):
        response = HtmlResponse(url="my HTML string",body=page_sourse,encoding="utf-8")

        A = response.xpath("//div[@class='searchresult_list ']/ul")
        # 获取每个酒店的链接
        for B in A:
            url = B.xpath("li[@class='searchresult_info_name']/h2/a/@href").extract()
        # 评论
            commnum = B.xpath("li[@class='searchresult_info_judge ']/div/a/span[@class='hotel_judgement']/text()").extract()
            if len(commnum):
                Discuss = re.sub('\D','',commnum[0])
                if len(Discuss):
                    pass
                else:
                    Discuss = 0
            else:
                Discuss = 0
            self.listPageInfo.append({"url":url[0], "comm_num":Discuss, "city":"南京"})
        xiechengService.saveListPageInfo()
        if len(self.listPageInfo) == 25:
            pass
        else:
            print len(self.listPageInfo)
        self.listPageInfo = []


    def saveListPageInfo(self):
        self.xiechengDao.savehotellink(self.listPageInfo)

    def depose(self):
        self.driver.close()

if __name__=="__main__":
    xiechengService = XiechengDriverService()
    xiechengService.start()
    xiechengService.depose()
