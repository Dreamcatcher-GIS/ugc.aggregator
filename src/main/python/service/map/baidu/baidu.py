# -*- coding:utf-8 -*-

from util.http.UniversalSDK import APIClient


class BaiduCrawler(object):

    def __init__(self):
        self.client = APIClient("http://api.map.baidu.com")

    def place(self,query,bounds,ak):
        return self.client.place.v2.search.get(query=query,bounds=bounds,ak=ak,output="json")

if __name__ == "__main__":
    baiduCrawler = BaiduCrawler()
    #print baiduCrawler.place("银行","39.915,116.404,39.975,116.414","WBw4kIepZzGp4kH5Gn3r0ACy")