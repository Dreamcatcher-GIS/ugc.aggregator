# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


class SeleniumTest(unittest.TestCase):

    driver = webdriver.Chrome()

    def setUp(self):
        print "setUp"

    def test_click_comment(self):
        self.driver.get("http://hotel.tuniu.com/detail/234656703?checkindate=2016-03-27&checkoutdate=2016-03-28##")
        # 将界面最大化
        self.driver.maximize_window()
        time.sleep(2)
        self.driver.find_element_by_tag_name("body").send_keys(Keys.END)
        while 1:
            self.driver.find_element_by_tag_name("body").send_keys(Keys.ARROW_UP)
            try:
                self.driver.find_element_by_xpath("//div[@class='tradeoffConclude']/a[@data='1']").click()
                break
            except Exception,e:
                continue
        time.sleep(10)

    def test_scroll_by_js(self):
        self.driver.get("http://hotel.tuniu.com/detail/234656703?checkindate=2016-03-27&checkoutdate=2016-03-28##")
        self.driver.maximize_window()
        time.sleep(2)
        js = "var q=document.documentElement.scrollTop=9000"
        self.driver.execute_script(js)
        print "scroll done"
        time.sleep(10)

    def test_window_size(self):
        self.driver.get("http://hotel.tuniu.com/detail/234656703?checkindate=2016-03-27&checkoutdate=2016-03-28##")
        self.driver.set_window_size(2000,30000)
        self.driver.find_element_by_partial_link_text(u"满意").click()
        time.sleep(10)

    def tearDown(self):
        self.driver.close()
        print "tearDown"

if __name__ == "__main__":
    unittest.main()