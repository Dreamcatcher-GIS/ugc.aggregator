# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

from util.http.UniversalSDK import APIClient
import datetime


class TuniuAPIClient(object):

    def __init__(self):
        self.client = APIClient("http://hotel.tuniu.com")

    def get_hotel_list(self, page, cityCode, checkIn=None, checkOut=None):
        if checkIn is None:
            tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
            after_tomorrow = tomorrow + datetime.timedelta(days=1)
            checkIn = tomorrow.strftime('%Y-%m-%d')
            checkOut = after_tomorrow.strftime('%Y-%m-%d')
        query_param = {
            "r":"/hotel/ajax/list",
            "search[cityCode]":cityCode,
            "search[checkInDate]":checkIn,
            "search[checkOutDate]":checkOut,
            "sort[first][id]":"recommend",
            "sort[third]":"cash-back-after",
            "page":page,
            "returnFilter":0
        }
        hotel_list = self.client.yii.addtrail(".php").get_by_dict(query_param)
        return hotel_list