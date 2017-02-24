# -*- coding: utf-8 -*-
__author__ = 'lizhen'

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from weibo import APIClient
from scrapy.http import HtmlResponse
from dao.weibo.WeiboDAO import WeiboDAO
from datetime import datetime
from service.weibo.APIService import WeiboAPIService
import re
import time


class WeiboDriverService(object):

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.weiboDao = WeiboDAO()
        self.weiboAPIService = WeiboAPIService()

    # 设置目标用户的微博名称
    def setScreen_Name(self, screen_name):
        self.userInfo = self.weiboAPIService.getUserInfo(screen_name=screen_name)

    # 登录weibo
    def login(self,account, password, timeout=3):
        def send_key(elemName,key):
            self.driver.implicitly_wait(10)
            try:
                elem = self.driver.find_element_by_name(elemName)
                elem.send_keys(key)
                print "sendkey:"+key+" successful"
                return elem
            except:
                print "sendkey failed"
                raise Exception()
        # 打开微博首页
        self.driver.get("http://weibo.com/")
        # 将界面最大化
        self.driver.maximize_window()
        self.driver.implicitly_wait(30)

        # 输入账号密码并点击登录
        send_key("username", account)
        send_key("password", password)
        self.driver.find_element_by_xpath("//span[@node-type='submitStates']").click()
        time.sleep(timeout)

    # 爬取页面内容
    # 捕捉到下一页按钮时将页面内容作为参数回调pageHandler
    # 同时点击跳转到下一页
    def crawlUserWeibo(self,url=None,pageHandler = None,threshold=0.3):
        if url is None:
            url = "http://weibo.com/"+str(self.userInfo["id"])
        if pageHandler is None:
            pageHandler = self.pageHandler_weibo
        # 进入链接页
        self.driver.get(url)
        time.sleep(2)

        thresholdTime = time.time()+threshold
        loopNum = 0
        pageNum = 1
        ifHandle = False
        # 持续下翻页面直到页面出现下一页按钮
        while True:
            # 到达页面底部
            self.driver.find_element_by_tag_name("body").send_keys(Keys.END)

            # 每隔threshold秒检查一下页面是否有下一页按钮
            if time.time()>thresholdTime:
                if u"下一页" in self.driver.page_source:
                    if ifHandle==False:
                        pageHandler(self.driver.page_source, pageNum)
                        ifHandle = True
                    try:
                        self.driver.find_element_by_partial_link_text("下一页").click()
                        loopNum = 0
                        ifHandle = False
                        pageNum = pageNum+1
                        print "page:"+str(pageNum)
                    except:
                        thresholdTime = time.time()+threshold
                        continue
                else:
                    thresholdTime = time.time()+threshold
                    loopNum = loopNum + 1
                    continue

            # 如果循环次数过多,说明可能出现页面加载失败,刷新页面
            if loopNum>10:
                loopNum = 0
                self.driver.refresh()

    # 页面处理器：获取页面中发布的微博ID并存入数据库中
    def pageHandler_weibo(self, page_source, pageNum):
        retext = "href=\"/"+str(self.userInfo['id'])+"/(.+?)[?]from="
        weiboIDSet = set()
        p = re.compile(retext)
        matches = p.findall(page_source)
        for weiboId in matches:
            if(len(weiboId)>0):
                weiboIDSet.add(weiboId)
        self.weiboDao.saveWeiboID(weiboIDSet, self.userInfo['id'],pageNum)

    # 遍历微博的评论页，将页面传递给pageHanlder处理
    def crawlWeiboContent(self, userID, weiboID, pageHandler = None, threshold=0.2):
        if pageHandler is None:
            pageHandler = self.pageHandler_comment
        # 进入到微博内容页
        url = "http://weibo.com/"+userID +"/"+weiboID
        print url
        self.driver.get(url)
        time.sleep(1)
        # 评论的页数
        while True:
            try:
                totalPageNum = self.__getCommentNum(self.driver.page_source)/20+1
                break
            except:
                continue

        thresholdTime = time.time()+threshold
        currentPageNum = 1
        loopNum = 0
        ifHandle = False
        # 根据评论页数循环爬取页面
        while currentPageNum<=totalPageNum:
            # 到达页面底部
            self.driver.find_element_by_tag_name("body").send_keys(Keys.END)
            if time.time()>thresholdTime:
                # 页面加载完成时会出现下一页按钮
                if u"下一页" in self.driver.page_source:
                    # ifHandle负责标识页面是否已经进行了处理
                    if ifHandle==False:
                        pageHandler(self.driver.page_source,currentPageNum,userID,weiboID)
                        ifHandle = True

                    try:
                        self.driver.find_element_by_partial_link_text("下一页").click()
                        time.sleep(1)
                        loopNum = 0
                        ifHandle = False
                        currentPageNum = currentPageNum+1
                    except:
                        thresholdTime = time.time()+threshold
                        continue
                else:
                    thresholdTime = time.time()+threshold
                    loopNum = loopNum + 1
                    continue
                # 当前页面等于最后一页时需要爬取
                if currentPageNum==totalPageNum:
                    if ifHandle==False:
                        pageHandler(self.driver.page_source,currentPageNum,userID,weiboID)
                        break

            # 如果循环次数过多,说明可能出现页面加载失败,刷新页面
            if loopNum>20:
                loopNum = 0
                self.driver.refresh()
                currentPageNum = 1

    # 获得评论数
    def __getCommentNum(self,page_source):
        retext = "\"comment_btn_text\">(.+?)</span>"
        p = re.compile(retext)
        matches = p.findall(page_source)
        try:
            return int(matches[0].split(" ")[1])
        except:
            raise Exception()

    # 页面处理器：将微博内容和评论信息抽取出来
    def pageHandler_comment(self,page_source,pageNum,userID,weiboID):
        response = HtmlResponse(url="my HTML string",body=page_source,encoding="utf-8")
        if pageNum==1:
            pass
        items = self.__getCommentItems(response,pageNum,userID,weiboID)
        if len(items)>0:
            self.weiboDao.saveWeiboComment(items)

    # 获取页面中的评论数据
    def __getCommentItems(self,response,pageNum,userID,weiboID):
        items = []
        commentData = response.xpath("//div[@comment_id]")
        # 爬取的时间
        currentTime = datetime.now()
        strCurrentTime = currentTime.strftime('%Y-%m-%d %H:%M:%S').encode('utf-8')
        # 遍历每条评论，将评论数据放到items中
        for itemData in commentData:
            # commPeople:评论人
            # commentText:评论文本
            # commentTime:评论时间
            # crawlTime:抓取数据时间
            itemDict = dict()

            itemDict["userID"] = userID

            itemDict["weiboID"] = weiboID

            itemDict["pageNum"] = pageNum

            itemDict["crawlTime"] = strCurrentTime

            commentTime = itemData.xpath("div[2]/div[3]/div[2]/text()").extract()[0]
            itemDict["commentTime"] = commentTime

            likeNumData = itemData.xpath("div[2]/div[3]/div/ul/li/span/a/span/em/text()").extract()
            likeNum = 0 if len(likeNumData)==0 else int(likeNumData[0])
            itemDict["likeNum"] = likeNum
            # 文本数组：每条评论中的所有文本
            commentArray = itemData.xpath("div[2]/div[1]//text()").extract()

            valve = False
            commPeople = ""
            commentText = ""
            # 拼接文本数组，取评论人和评论内容
            for string in commentArray:
                if u"：" in string:
                    valve = True
                # 在冒号前的文本为评论人
                if valve==False:
                    commPeople = commPeople + re.sub("\s*","",string)
                # 在冒号之后的文本为评论内容
                if valve==True:
                    commentText = commentText + re.sub("\s*","",string)
                ## 获取评论的文本
                itemDict["commentText"] = commentText
                ## 获取评论的人名
                itemDict["commPeople"] = commPeople
            items.append(itemDict)
        return items

    # 关闭浏览器
    def depose(self):
        self.driver.close()

if __name__=="__main__":
    weiboService = WeiboDriverService()
    weiboService.setScreen_Name("芜湖方特旅游度假区")
    weiboService.login("18110782697","a3411610")
    # weiboService.crawlUserWeibo()
    weiboService.crawlWeiboContent("2549228714","D6SoQBSYt")
    weiboService.depose()

