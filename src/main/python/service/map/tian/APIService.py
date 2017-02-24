# -*- coding:utf-8 -*-

from util.http.UniversalSDK import APIClient


class TianMapAPIService(object):

    def __init__(self):
        self.tiandituClient = APIClient("http://map.tianditu.com")

    # 天地图地理编码
    # 地址：http://map.tianditu.com/query.shtml
    # 类型：post
    def tdtGeocoding(self,address):
        # json格式
        postStr = "{\"keyWord\":\"address\",\"level\":\"12\",\"mapBound\":\"118.61107,31.90788,118.93449,32.18735\",\"queryType\":\"1\",\"count\" :\"20\",\"start\":\"0\",\"queryTerminal\":\"10000\"}"
        postStr = postStr.replace("address",address)
        data=self.tiandituClient.query.addtrail(".shtml").post(postStr=postStr,type="query")
        return data