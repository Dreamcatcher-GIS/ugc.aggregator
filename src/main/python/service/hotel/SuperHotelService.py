# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer，LiuYang'

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import traceback


class HotelService(object):

    def __init__(self):
        self.driver = webdriver.Chrome()

        self.if_crawl_hotel_info = True

        self.if_crawl_hotel_comment = True

        self.if_crawl_hotel_price = True

        self._city = None

    '''
    打开页面
    '''
    def openPage(self,url):
        self.driver.get(url)
        # 将界面最大化
        self.driver.maximize_window()

    '''
    等待加载
    '''
    def wait(self,timeout):
        self.driver.implicitly_wait(timeout)

    '''
    关闭驱动
    '''
    def closeDriver(self):
        self.driver.close()

    '''
    遍历酒店信息列表页，爬取酒店详情页链接
    抓取成功返回True  失败返回False
    '''
    def crawlListPage(self):
        pass

    '''
    保存爬取的酒店列表页数据
    '''
    def saveListPageInfo(self):
        pass

    def set_city(self, city):
        self._city = city

    '''
    抓取酒店信息
    '''
    def crawlHotelInfo(self,target):
        pass

    '''
    保存抓取的酒店信息
    '''
    def saveHotelInfo(self):
        pass

    '''
    获取酒店列表页数据
    '''
    def getListPageInfo(self):
        pass

    def scroll_and_click_by_partial_link_text(self, text, from_bottom=False):
        if from_bottom:
            # 跳到页尾
            self.driver.find_element_by_tag_name("body").send_keys(Keys.END)
            key = Keys.ARROW_UP
        else:
            # 跳到页头
            self.driver.find_element_by_tag_name("body").send_keys(Keys.HOME)
            key = Keys.ARROW_DOWN
        x = 0
        while 1:
            x += 1
            if x%500 == 0:
                self.driver.refresh()
                time.sleep(2)
                if from_bottom:
                    self.driver.find_element_by_tag_name("body").send_keys(Keys.END)
                else:
                    self.driver.find_element_by_tag_name("body").send_keys(Keys.HOME)
            if x == 1501:
                print u"点击评论类型出错" + self.driver.current_url
                break
            self.driver.find_element_by_tag_name("body").send_keys(key)
            try:
                self.driver.find_element_by_partial_link_text(text).click()
                break
            except:
                continue

    def scroll_and_click_by_xpath(self, text, from_bottom=False, refresh_if_failed=True, sleep_time=0):
        if from_bottom:
            # 跳到页尾
            self.driver.find_element_by_tag_name("body").send_keys(Keys.END)
            key = Keys.ARROW_UP
        else:
            # 跳到页头
            self.driver.find_element_by_tag_name("body").send_keys(Keys.HOME)
            key = Keys.ARROW_DOWN
        time.sleep(sleep_time)
        x = 0
        while 1:
            x += 1
            if x%500 == 0:
                # 刷新整个页面
                if refresh_if_failed:
                    self.driver.refresh()
                time.sleep(sleep_time)
                if from_bottom:
                    self.driver.find_element_by_tag_name("body").send_keys(Keys.END)

                else:
                    self.driver.find_element_by_tag_name("body").send_keys(Keys.HOME)
                time.sleep(sleep_time)
            if x == 1501:
                print u"点击评论类型出错" + self.driver.current_url
                break
            self.driver.find_element_by_tag_name("body").send_keys(key)
            try:
                self.driver.find_element_by_xpath(text).click()
                break
            except:
                # print text
                continue

    '''
    设置爬取内容
    '''
    def set_crawl_content(self,if_crawl_hotel_info, if_crawl_hotel_comment, if_crawl_hotel_price):
        self.if_crawl_hotel_info = if_crawl_hotel_info

        self.if_crawl_hotel_comment = if_crawl_hotel_comment

        self.if_crawl_hotel_price = if_crawl_hotel_price