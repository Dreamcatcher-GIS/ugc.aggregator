# -*- coding:utf-8 -*-
__author__ = 'LiuYang'


import time
import uuid

from service.hotel.XieChengAPIClient import XieChengAPIClient
from dao.hotel.HotelDAO import HotelDAO
from setting import local_hotel_setting
from util.geo import CoordTransor

# 配置数据库
dao_setting = local_hotel_setting


class XiechengCatcher(object):

    def __init__(self):
        self._city = None
        self.__ota_info = "携程"
        self.xiecheng_api_client = XieChengAPIClient()
        self.hotel_dao = HotelDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])

    def setCity(self, city):
        self._city = city

    def getHotelList(self, cityId):
        if self._city == None:
            print "未设置城市,请先使用setCity方法"
        hotel_list = []
        page_index = 1
        page_amount =10000
        while page_index <= page_amount - 1:
            try:
                page_data = self.xiecheng_api_client.get_hotel_list(page_index, cityId, self._city)
                # 接口返回的酒店数不稳定，所以爬取页数以最小数为准
                if page_amount > page_data["hotelAmount"] / 25:
                    page_amount = page_data["hotelAmount"] / 25
                    print "page_amount=%d"%page_amount
                hotel_list.extend(page_data["hotelPositionJSON"])
                print "Page_%d Success"%page_index
                page_index += 1
            except:
                print "Page_%d Fail"%page_index
                continue
        return hotel_list

    def saveHolteList(self, hotel_list):
        old_location_info = self.hotel_dao.get_locations(self._city)
        old_baseinfo = list(self.hotel_dao.get_baseinfo(self._city, self.__ota_info))
        # 将基础数据中的if_overtime先假设为都已过时
        for i in range(0, len(old_baseinfo)):
            old_baseinfo[i] = list(old_baseinfo[i])
            old_baseinfo[i][5] = 1
        new_locations = []
        new_baseinfo = []
        update_baseinfo = []
        # 遍历将要保存的数据
        for item in hotel_list:
            location_id = None
            # 首先检查该酒店是否已经保存在location表中
            for location in old_location_info:
                if item["name"] == location[3]:
                    location_id = location[0]
                    break
            # 如果没有则插入一条新的记录到location表中
            if location_id is None:
                location_id = uuid.uuid1()
                trans_location = CoordTransor.bd09togcj02(bd_lon=float(item["lon"]), bd_lat=float(item["lat"]))
                trans_location = CoordTransor.gcj02towgs84(trans_location[1], trans_location[0])
                new_locations.append({
                    "guid": location_id,
                    "x": trans_location[1],
                    "y": trans_location[0],
                    "hotel_name": item["name"],
                    "city": self._city,
                    "address": item["address"]
                })
            # 根据location的id号到baseinfo表中查询
            # 如果已经存于表中，则更新该条数据
            # 如果没有，则插入一条新的数据
            if_exist = False
            for baseinfo in old_baseinfo:
                if location_id == baseinfo[2]:
                    if_exist = True
                    baseinfo[1] = item["url"]
                    baseinfo[4] = item["dpcount"]
                    baseinfo[5] = 0
                    baseinfo[6] = int(item["dpcount"]) - int(baseinfo[4]) if int(item["dpcount"]) - int(baseinfo[4]) > 0 else 0
                    baseinfo[7] = item["img"]
                    baseinfo[8] = item["id"]
                    break
            if not if_exist:
                new_baseinfo.append({
                    "guid": uuid.uuid1(),
                    "url": item["url"],
                    "location_id": location_id,
                    "OTA": self.__ota_info,
                    "comm_num": item["dpcount"],
                    "if_overtime": 0,
                    "incre_num": item["dpcount"],
                    "img": item["img"],
                    "id_in_ota": item["id"]
                })
        for baseinfo in old_baseinfo:
            update_baseinfo.append({
                "guid": baseinfo[0],
                "url": baseinfo[1],
                "location_id": baseinfo[2],
                "OTA": baseinfo[3],
                "comm_num": baseinfo[4],
                "if_overtime": baseinfo[5],
                "incre_num": baseinfo[6],
                "img": baseinfo[7],
                "id_in_ota": baseinfo[8]
            })
        print len(new_locations), len(new_baseinfo), len(update_baseinfo)
        self.hotel_dao.save_locations(new_locations)
        self.hotel_dao.save_baseinfo(new_baseinfo)
        self.hotel_dao.update_baseinfo(update_baseinfo)



if __name__ == "__main__":
    starttime = time.time()
    xiecheng_catcher = XiechengCatcher()
    xiecheng_catcher.setCity("南京")
    hotel_list = xiecheng_catcher.getHotelList(12)
    xiecheng_catcher.saveHolteList(hotel_list)
    endtime = time.time()
    print endtime-starttime