# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

from util.http.UniversalSDK import APIClient


class TianMapAPIService(object):

    def __init__(self):
        self.tiandituClient = APIClient("http://map.tianditu.com")

    # 天地图地理编码
    # 地址：http://map.tianditu.com/query.shtml
    # 类型：post
    def tdtGeocoding(self,address):
        postStr = "{\"keyWord\":\"address\",\"level\":\"18\",\"mapBound\":\"117.15973,39.10137,117.16825,39.10371\",\"queryType\":\"1\",\"count\" :\"20\",\"start\":\"0\",\"queryTerminal\":\"10000\"}"
        postStr = postStr.replace("address",address)
        data=self.tiandituClient.query.addtrail(".shtml").post(postStr=postStr,type="query")
        return data