# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import traceback

from dao.hotel.TuniuDao import TuniuDAO
from setting import local_hotel_setting
from service.map.baidu.APIService import BaiduMapAPIService

# 配置数据库
dao_setting = local_hotel_setting

dao = TuniuDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])

map_service = BaiduMapAPIService("MviPFAcx5I6f1FkRQlq6iTxc")

hotellist = dao.get_hotelinfo()

# 酒店地理编码容器
hotel_location = []

# 遍历酒店信息，取出酒店名称进行地理编码
for i in range(0, len(hotellist)):
    geocoding_info = map_service.doGeocoding(hotellist[i][1])
    try:
        geocoding_info = {"hotel_name":hotellist[i][1], "x":geocoding_info["result"]["location"]["lng"], "y":geocoding_info["result"]["location"]["lat"]}
    except:
        traceback.print_exc()
        continue
    hotel_location.append(geocoding_info)
    print "%d done"%i

print len(hotel_location)
# 保存到数据库中
dao.save_hotels_location(hotel_location)