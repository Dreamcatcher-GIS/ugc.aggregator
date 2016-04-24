# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import logging

from util.http.UniversalSDK import APIClient

logger = logging.getLogger('ugc')


class BaiduMapAPIService(object):
    def __init__(self, ak):
        self.baiduClient = APIClient("http://api.map.baidu.com")
        self.__ak = ak

    '''
    正向地理编码geocoding
    文档：http://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-geocoding
    Rest地址：http://api.map.baidu.com/geocoder/v2/
    类型：get
    '''
    def doGeocoding(self, addressText,city=None):
        if city==None:
            data = self.baiduClient.geocoder.v2.addtrail("/").get(ak=self.__ak, output="json", address=addressText)
        else:
            data = self.baiduClient.geocoder.v2.addtrail("/").get(ak=self.__ak, output="json", address=addressText, city=city)
        return data

    def reverseGeocodingBatch(self, locationList):
        '''
        逆向地理编码批量处理入口
        地址：http://api.map.baidu.com/geocoder/v2/
        类型：get
        '''
        respList = self.reverseGeocodingBatchHandler(locationList=locationList, respList=[], errorList=[])
        return respList

    def reverseGeocodingBatchHandler(self, locationList, respList, errorList):
        '''
        逆向地理编码批量处理，处理timeout
        地址：http://api.map.baidu.com/geocoder/v2/
        类型：get
        '''
        for i in range(0, len(locationList), 1):
            location = locationList[i]
            resp = self.reverseGeocoding(location=location)
            if resp is not None and resp["status"] == 0:
                respList.append(resp)
            else:
                logging.debug("current token: %s " % self.__ak)
                logging.debug( resp)
                logging.debug("at point:%s",str(location))
        if len(errorList) > 0:
            # http请求异常重新处理
            logging.debug("http exception ,rehandle size : " + str(len(errorList)))
            self.reverseGeocodingBatchHandler(locationList=errorList, respList=respList, errorList=[])
        return respList

    def reverseGeocoding(self, location, coordtype='bd09ll', output="json", pois='0'):
        '''
        逆向地理编码request
        地址：http://api.map.baidu.com/geocoder/v2/
        类型：get
        coordtype，默认bd09ll，坐标的类型，目前支持的坐标类型包括：bd09ll（百度经纬度坐标）、bd09mc（百度米制坐标）、gcj02ll（国测局经纬度坐标）、wgs84ll（ GPS经纬度）
        '''
        resp = self.baiduClient.geocoder.v2.addtrail("/").get(ak=self.__ak, output="json",pois=2, location=location)
        return resp

    def placeSearchBatch(self, query, bounds, pageNumber="0"):
        '''
        Place地名批量查询，处理timeout
        地址：http://api.map.baidu.com/geocoder/v2/
        类型：get
        '''
        resp = self.placeSearch(query=query, bounds=bounds, pageNumber=pageNumber)
        if resp is None:
            logging.debug("http exception ,rehandle...")
            reHandleResp = self.placeSearch(query=query, bounds=bounds, pageNumber=pageNumber)
            while reHandleResp is None:
                reHandleResp = self.placeSearch(query=query, bounds=bounds, pageNumber=pageNumber)
            return reHandleResp
        else:
            # TODO 为什么返回None
            return resp

    # coord_type(坐标类型)，1（wgs84ll），2（gcj02ll），3（bd09ll），4（bd09mc）
    def placeSearch(self, query, bounds, output="json", pageSize="20", pageNumber="0", coord_type="1", scope=2):
        '''
        Place地名
        地址：http://api.map.baidu.com/place/v2/search
        类型：get
        '''
        data = self.baiduClient.place.v2.search.get(ak=self.__ak, query=query, bounds=bounds, output=output,
                                                    coord_type=coord_type, page_size=pageSize, page_num=pageNumber,
                                                    scope=scope)
        return data
