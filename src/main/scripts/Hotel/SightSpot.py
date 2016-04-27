# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

from service.map.baidu.APIService import BaiduMapAPIService
from util.geo import CoordTransor


baidu_api_service = BaiduMapAPIService("MviPFAcx5I6f1FkRQlq6iTxc")

f = open('sightspot.txt', 'r')
for line in f.readlines():
    data = baidu_api_service.doGeocoding(addressText=line.strip(),city='南京')
    if "result" in data:
        print line+str(CoordTransor.bd09togcj02(data["result"]["location"]["lng"],data["result"]["location"]["lat"]))
        # print line+str(data["result"]["location"]["lat"])+","+str(data["result"]["location"]["lng"])