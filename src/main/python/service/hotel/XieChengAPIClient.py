# -*- coding:utf-8 -*-
__author__ = 'LiuYang'

from util.http.UniversalSDK import APIClient
import datetime


class XieChengAPIClient(object):

    def __init__(self):
        self.client = APIClient("http://hotels.ctrip.com")

    '''
    获取携程酒店列表数据
    '''
    def get_hotel_list(self, page, cityId, cityName, checkIn=None, checkOut=None):
        if checkIn is None:
            tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
            after_tomorrow = tomorrow + datetime.timedelta(days=1)
            checkIn = tomorrow.strftime('%Y-%m-%d')
            checkOut = after_tomorrow.strftime('%Y-%m-%d')
        header = {"Content-Type":"application/x-www-form-urlencoded"}
        hotel_list =  self.client.Domestic.Tool.AjaxHotelList.addtrail(".aspx").addheader(header)\
            .post(checkIn=checkIn, checkOut=checkOut, page=page, cityId=cityId, cityName=cityName)
        return hotel_list