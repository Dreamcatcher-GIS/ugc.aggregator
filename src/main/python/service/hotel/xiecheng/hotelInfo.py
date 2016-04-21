# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from scrapy.http import HtmlResponse
from datetime import datetime
import re
import time
import json
import uuid
from dao.hotel.xiechengdao.xiecheng import xiechengDAO
import random
from service.hotel.SuperHotelService import HotelService
from service.nlp.HotelNLP import HotelNLP
from setting import lt_hotel_setting
class XiechenghotelService(object):

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.xiechengDao = xiechengDAO()
        # 自然语言处理
        self.hotelNLP = HotelNLP()
        # 存放酒店详情数据
        self.hotelItem = {}
        # 存放酒店评论数据
        self.commList = []

    # 关闭浏览器
    def depose(self):
        self.driver.close()


    # 从数据库读取数据（链接）
    def getdata(self):

        Lianjie_data = self.xiechengDao._return()
        for lianjie_data in Lianjie_data:
            self.intohotel(lianjie_data[1])
            # 存储数据
            # self.xiechengDao.savehotelCommentinfo(self.commList)
            # self.commList = []


    # 从数据库读取评论数据
    def getdata_comment(self):
        Commentinfo = self.xiechengDao._returncommentinfo()
        for commentinfo in Commentinfo:
            try:
                commentinfo_list = []
                senti_value = None
                viewpoint = None
                senti_value = self.hotelNLP.sentiment(commentinfo[7].encode("utf-8"))
                viewpoint = json.dumps(self.hotelNLP.viewpoint(commentinfo[7].encode("utf-8"),decoding="utf-8"))
                commentinfo_list.append({"hotelname":commentinfo[0],"username":commentinfo[1],"commentscore":commentinfo[2],"intime":commentinfo[3],"tourstyle":commentinfo[4],"praisenum":commentinfo[5],"comment":commentinfo[7],"senti_value":senti_value,"viewpoint":viewpoint})
                self.xiechengDao.savehotelCommentinfosenti(commentinfo_list)
            except:
                pass

     # 进入酒店
    def intohotel(self,Links):

        url = "http://hotels.ctrip.com/" + Links
        self.driver.get(url)
        self.driver.maximize_window()
        self.driver.implicitly_wait(80)
        time.sleep(3)
        response = HtmlResponse(url="my HTML string",body=self.driver.page_source,encoding="utf-8")
        # 爬取酒店评论信息
        # self.crawlcommentinfo(commentnum)
        # # 爬取酒店基本数据
        try:
            items = self.crawlhotelinfo(response,url)
        except:
            items = self.crawlhotelinfo2(response,url)
        # 存取酒店基本数据
        self.xiechengDao.savehotelComment(items)



    # 点击全部评论并获取页数
    def getpagenum(self,response):
        try:
            self.driver.find_element_by_tag_name("body").send_keys(Keys.END)
            self.driver.find_element_by_xpath("//li[@id='commentTab']/a").click()
            time.sleep(3)
            # 点评总数

            comments = response.xpath("//li[@id='commentTab']/a/text()").extract()[0]
            commentnum = re.sub('\D','',comments)
            commentpagenum = int(commentnum)/15+1
            self.crawlcommentinfo(commentpagenum)

        except:
            pass

    # 爬取酒店评论数据
    def crawlcommentinfo(self,commentnum):
        pageNum = commentnum/15+1
        pagenum = pageNum
        # 单页循环次数
        loopNum = 0
        # 标识当前页面是否已经爬取：False为未处理，反之为已处理
        ifHandle = False
        self.driver.find_element_by_tag_name("body").send_keys(Keys.END)
        if u"酒店点评" in self.driver.page_source:
            try:
                self.driver.find_element_by_xpath("//li[@id='commentTab']/a").click()
            except:
                self.driver.refresh()
                self.commList = []
                self.crawlcommentinfo(commentnum)
        else:
            while True:
                time.sleep(3)
                self.driver.refresh()
                self.commList = []
                self.crawlcommentinfo(commentnum)
        while(pageNum>=1):
            # 循环次数加1
            loopNum = loopNum + 1
            # 到达页面底部
            try:
                self.driver.find_element_by_tag_name("body").send_keys(Keys.END)
            except Exception, e:
                print e
            time.sleep(2)
            # 当页面中出现“返前价”字样时，爬取页面并跳转到下一页
            if u"搜索" in self.driver.page_source:
                pageNum = pageNum - 1
            # 对未解析过的页面进行解析
                if ifHandle==False:
                    self.getcommentinfo(self.driver.page_source)
                    ifHandle = True
                try:
                    if u"下一页" in self.driver.page_source:
                        self.driver.find_element_by_partial_link_text("下一页").click()
                        ifHandle = False
                        # 单页循环次数置为零
                        loopNum = 0
                        time.sleep(random.uniform(4,7))
                except:
                    pass
        # 如果单页循环次数不为零，说明没有跳转到下一页
            if loopNum != 0:
                # 循环次数较大的情况下（此处预定为15次）说明页面可能加载失败，跳出循环，否则继续循环获取
                if loopNum < 15:
                    time.sleep(3)
                    continue
                else:
                    break
        print len(self.commList)
        return False if pageNum>1 else True


    # 解析评论页面
    def getcommentinfo(self,page_sourse):
        response = HtmlResponse(url="my HTML string",body=self.driver.page_source,encoding="utf-8")
        commentData = response.xpath("//div[@class='comment_detail_list']/div[@class='comment_block J_asyncCmt']")
        title = response.xpath("//div[@class='main_detail_wrapper ']/div[@class='detail_main detail_main_no_tips']/div[@class='htl_info']/div[@class='name']/h2[@class='cn_n']/text()").extract()
        if len(title):
            Title = title
        else:
            Title = response.xpath("//div[@class='main_detail_wrapper ']/div[@class='detail_main detail_main_no_comment']/div[@class='htl_info']/div[@class='name']/h2[@class='cn_n']/text()").extract()
        for itemData in commentData:
            itemDict = dict()

            # 酒店名
            hotelname = Title
            if len(hotelname):
                hotelnames = hotelname[0]
            else:
                hotelnames = " "


            # 用户名
            username = itemData.xpath("div[1]/p[2]/span/text()").extract()
            if len(username):
                usernames = username[0]
            else:
                usernames = ""

            # 评论分
            commentscore = itemData.xpath("div[2]/p/span[2]/span/text()").extract()
            if len(commentscore):
                commentscores = commentscore[0]
            else:
                commentscores = ""

            # 入住时间
            intime = itemData.xpath("div[2]/p/span[3]/text()").extract()
            if len(intime):
                intimes = intime[0]
            else:
                intimes = ""

            # 出游类型
            tourstyle = itemData.xpath("div[2]/p/span[4]/text()").extract()
            if len(tourstyle):
                tourstyles = re.sub('\w','',tourstyle[0])
            else:
                tourstyles = ""

            # 点赞数量
            praisenum = itemData.xpath("div[2]/div[@class='comment_txt']/div[@class='comment_bar']/a/span/text()").extract()
            if len(praisenum):
                Praisenum = re.sub('\D','',praisenum[0])
                praisenums = Praisenum
            else:
                praisenums = ""

            # 评论发表时间
            commenttime = itemData.xpath("div[2]/div[@class='comment_txt']/div[@class='comment_bar']/p/span/text()").extract()
            if len(commenttime):
                commenttimes = commenttime[0].split(u"于")[1]
            else:
                commenttimes = ""

            # 评论内容
            comment = itemData.xpath("div[2]/div[@class='comment_txt']/div[1]/text()").extract()
            if len(comment):
                comments = comment[0]
            else:
                comments = ""
            self.commList.append({"title":hotelnames,"username":usernames,"commentscore":commentscores, "intime":intimes, "tourstyle":tourstyles, "praisenum":praisenums,"commenttime":commenttimes,"comment":comments})




    # 爬取酒店基本数据（另一种情况）
    def crawlhotelinfo2(self,response,url):

            time.sleep(2)
            items = []
            itemData = response.xpath("//div[@class='main_detail_wrapper ']")
            # 爬取的时间
            currentTime = datetime.now()
            strCurrentTime = currentTime.strftime('%Y-%m-%d %H:%M:%S').encode('utf-8')

            itemDict = dict()

            itemDict["guid"] = uuid.uuid1()

            itemDict["city"] = "南京"

            # 标题
            title = itemData.xpath("div[@class='detail_main detail_main_no_comment']/div[@class='htl_info']/div[@class='name']/h2[@class='cn_n']/text()").extract()[0]
            if len(title):
                itemDict["title"] = title
            else:
                itemDict["title"] = ""
            # print itemDict["title"]

            # 价格
            price = itemData.xpath("div[@class='detail_main detail_main_no_comment']/div[@class='htl_info']/div[@class='price_box']/div/p/span[@class='price']/text()").extract()
            if len(price):
                itemDict["price"] = price[0]
            else:
                itemDict["price"] = ""
            # print itemDict["price"]

            # 评分
            score = itemData.xpath("div[@class='detail_side']/div[@class='htl_com J_htl_com ']/div/a/p/span/text()").extract()
            if len(score):
                    itemDict["score"] = score[0]
            else:
                    itemDict["score"] = ""
            # print itemDict["score"]

            # 推荐
            recommend = itemData.xpath("div[@class='detail_side']/div[@class='htl_com J_htl_com ']/div/a/p[2]/text()").extract()
            if len(recommend):
                Recommend = re.sub('\D','',recommend[0])
                Recommend += "%"
                itemDict["recommend"] = Recommend
            else:
                itemDict["recommend"] = " "
            # print itemDict["recommend"]


            # 地址
            area = itemData.xpath("div[@class='detail_main detail_main_no_comment']/div[@class='htl_info']/div[@class='adress']/span/text()").extract()
            if (len(area)):
                areas = ""
                for i in range(0,3,1):
                    areas += area[i]
                itemDict["area"] = areas
            else:
                itemDict["area"] = ""
            # print itemDict["area"]

            # 有无wifi
            havewifi1 = itemData.xpath("div[@class='detail_main detail_main_no_comment']/div[@class='htl_info']/div[@class='icon_list']/i[@class='icons-facility32']")
            havewifi2 = itemData.xpath("div[@class='detail_main detail_main_no_comment']/div[@class='htl_info']/div[@class='icon_list']/i[@class='icons-facility32']")
            if (havewifi1 or havewifi2):
                itemDict["havawifi"] = "yes"
            else:
                itemDict["havawifi"] = "no"
            # print itemDict["havawifi"]

            # 评论数
            discuss = itemData.xpath("div[@class='detail_side']/div[@class='htl_com J_htl_com ']/div/a/span[@class='commnet_num']/span/text()").extract()
            if len(discuss):
                Discuss = re.sub('\D','',discuss[0])
            else:
                Discuss = ""

            itemDict["discussNum"] = Discuss
            # print itemDict["discussNum"]

            # 通用设施
            itemDict["common_facilities"] = ""
            itemDict["activity_facilities"] = ""
            itemDict["service_facilities"] = ""
            itemDict["room_facilities"] = ""
            hotel_facilities = itemData.xpath("div[@class='detail_main detail_main_no_comment']/div[@id='hotel_info_comment']/div[@class='hotel_info_comment']/div[@id='J_htl_facilities']/table/tbody/tr")
            if len(hotel_facilities):
                for a in range(0,len(hotel_facilities)-1):
                    sheshiname = hotel_facilities[a].xpath("th/text()").extract()[0]
                    Hotel_facilities = hotel_facilities[a].xpath("td/ul/li/@title").extract()
                    if sheshiname == u"通用设施":
                        common_facilities = ""
                        for j in range(len(Hotel_facilities)):
                            common_facilities += Hotel_facilities[j]
                            common_facilities += ","
                        itemDict["common_facilities"] = common_facilities
                        # print itemDict["common_facilities"]
                    elif sheshiname == u"活动设施":
                        activity_facilities = ""
                        for j in range(len(Hotel_facilities)):
                            activity_facilities += Hotel_facilities[j]
                            activity_facilities += ","
                        itemDict["activity_facilities"] = activity_facilities
                        # print itemDict["activity_facilities"]
                    elif sheshiname == u"服务项目":
                        service_facilities = ""
                        for j in range(len(Hotel_facilities)):
                            service_facilities += Hotel_facilities[j]
                            service_facilities += ","
                        itemDict["service_facilities"] = service_facilities
                        # print itemDict["service_facilities"]
                    elif sheshiname == u"客房设施":
                        room_facilities = ""
                        for j in range(len(Hotel_facilities)):
                            room_facilities += Hotel_facilities[j]
                            room_facilities += ","
                        itemDict["room_facilities"] = room_facilities
                        # print itemDict["room_facilities"]
                    else:
                        continue
            else:
                itemDict["common_facilities"] = " "
                itemDict["activity_facilities"] = " "
                itemDict["service_facilities"] = " "
                itemDict["room_facilities"] = " "
            items.append(itemDict)
            return items






    # 爬取酒店基本数据
    def crawlhotelinfo(self,response,url):

            time.sleep(2)
            items = []
            itemData = response.xpath("//div[@class='main_detail_wrapper ']")
            # 爬取的时间
            currentTime = datetime.now()
            strCurrentTime = currentTime.strftime('%Y-%m-%d %H:%M:%S').encode('utf-8')

            itemDict = dict()

            itemDict["guid"] = uuid.uuid1()

            itemDict["city"] = "南京"

            # 标题
            title = itemData.xpath("div[@class='detail_main detail_main_no_tips']/div[@class='htl_info']/div[@class='name']/h2[@class='cn_n']/text()").extract()[0]
            if len(title):
                itemDict["title"] = title
            else:
                itemDict["title"] = ""
            # print itemDict["title"]

            # 价格
            price = itemData.xpath("div[@class='detail_main detail_main_no_tips']/div[@class='htl_info']/div[@class='price_box']/div/p/span[@class='price']/text()").extract()
            if len(price):
                itemDict["price"] = price[0]
            else:
                itemDict["price"] = ""
            # print itemDict["price"]

            # 评分
            score = itemData.xpath("div[@class='detail_side']/div[@class='htl_com J_htl_com ']/div/a/p/span/text()").extract()
            if len(score):
                    itemDict["score"] = score[0]
            else:
                    itemDict["score"] = ""
            # print itemDict["score"]

            # 推荐
            recommend = itemData.xpath("div[@class='detail_side']/div[@class='htl_com J_htl_com ']/div/a/p[2]/text()").extract()
            if len(recommend):
                Recommend = re.sub('\D','',recommend[0])
                Recommend += "%"
                itemDict["recommend"] = Recommend
            else:
                itemDict["recommend"] = " "
            # print itemDict["recommend"]


            # 地址
            area = itemData.xpath("div[@class='detail_main detail_main_no_tips']/div[@class='htl_info']/div[@class='adress']/span/text()").extract()
            if (len(area)):
                areas = ""
                for i in range(0,3,1):
                    areas += area[i]
                itemDict["area"] = areas
            else:
                itemDict["area"] = ""
            # print itemDict["area"]

            # 有无wifi
            havewifi1 = itemData.xpath("div[@class='detail_main detail_main_no_tips']/div[@class='htl_info']/div[@class='icon_list']/i[@class='icons-facility32']")
            havewifi2 = itemData.xpath("div[@class='detail_main detail_main_no_tips']/div[@class='htl_info']/div[@class='icon_list']/i[@class='icons-facility32']")
            if (havewifi1 or havewifi2):
                itemDict["havawifi"] = "yes"
            else:
                itemDict["havawifi"] = "no"
            # print itemDict["havawifi"]

            # 评论数
            discuss = itemData.xpath("div[@class='detail_side']/div[@class='htl_com J_htl_com ']/div/a/span[@class='commnet_num']/span/text()").extract()
            if len(discuss):
                Discuss = re.sub('\D','',discuss[0])
            else:
                Discuss = ""

            itemDict["discussNum"] = Discuss

            # 通用设施
            itemDict["common_facilities"] = ""
            itemDict["activity_facilities"] = ""
            itemDict["service_facilities"] = ""
            itemDict["room_facilities"] = ""
            hotel_facilities = itemData.xpath("div[@class='detail_main detail_main_no_tips']/div[@id='hotel_info_comment']/div[@class='hotel_info_comment']/div[@id='J_htl_facilities']/table/tbody/tr")
            if len(hotel_facilities):
                for a in range(0,len(hotel_facilities)-1):
                    sheshiname = hotel_facilities[a].xpath("th/text()").extract()[0]
                    Hotel_facilities = hotel_facilities[a].xpath("td/ul/li/@title").extract()
                    if sheshiname == u"通用设施":
                        common_facilities = ""
                        for j in range(len(Hotel_facilities)):
                            common_facilities += Hotel_facilities[j]
                            common_facilities += ","
                        itemDict["common_facilities"] = common_facilities
                        # print itemDict["common_facilities"]
                    elif sheshiname == u"活动设施":
                        activity_facilities = ""
                        for j in range(len(Hotel_facilities)):
                            activity_facilities += Hotel_facilities[j]
                            activity_facilities += ","
                        itemDict["activity_facilities"] = activity_facilities
                        # print itemDict["activity_facilities"]
                    elif sheshiname == u"服务项目":
                        service_facilities = ""
                        for j in range(len(Hotel_facilities)):
                            service_facilities += Hotel_facilities[j]
                            service_facilities += ","
                        itemDict["service_facilities"] = service_facilities
                        # print itemDict["service_facilities"]
                    elif sheshiname == u"客房设施":
                        room_facilities = ""
                        for j in range(len(Hotel_facilities)):
                            room_facilities += Hotel_facilities[j]
                            room_facilities += ","
                        itemDict["room_facilities"] = room_facilities
                        # print itemDict["room_facilities"]
                    else:
                        continue
            else:
                itemDict["common_facilities"] = " "
                itemDict["activity_facilities"] = " "
                itemDict["service_facilities"] = " "
                itemDict["room_facilities"] = " "
            items.append(itemDict)
            return items


if __name__=="__main__":
    xiechenghotelService = XiechenghotelService()
    # 获取链接数据
    xiechenghotelService.getdata()

    # 获取评论数据
    # xiechenghotelService.getdata_comment()
    # 关闭浏览器
    xiechenghotelService.depose()