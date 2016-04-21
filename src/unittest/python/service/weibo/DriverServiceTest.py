# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

from service.weibo.DriverService import WeiboDriverService


class DriverServiceTest(object):

    def __init__(self):
        self.weiboDriverService = WeiboDriverService()

    def crawlUserWeiboTest(self):
        self.weiboDriverService.login("18110782697","a3411610")
        self.weiboDriverService.setScreen_Name("芜湖方特旅游度假区")
        self.weiboDriverService.crawlUserWeibo()
        self.weiboDriverService.depose()

    def crawlWeiboContent(self):
        self.weiboDriverService.login("18110782697","a3411610")
        self.weiboDriverService.crawlWeiboContent("2549228714","D6SoQBSYt")
        self.weiboDriverService.depose()

if __name__ == "__main__":
    driverServiceTest = DriverServiceTest()

    driverServiceTest.crawlUserWeiboTest()

    #driverServiceTest.crawlWeiboContent()