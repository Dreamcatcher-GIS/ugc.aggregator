# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'


import uuid
import re
import traceback

from dao.hotel.HotelDAO import HotelDAO
from dao.hotel.xiechengdao.xiecheng import xiechengDAO
from dao.hotel.TuniuDao import TuniuDAO
from setting import local_hotel_setting

# 配置数据库
dao_setting = local_hotel_setting

hotel_dao = HotelDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])
tuniu_dao = TuniuDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])
xiecheng_dao = xiechengDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])

# tuniu_comm = tuniu_dao.get_remarks()
#
# hotel_comm = []
# i = 0
# for comm in tuniu_comm:
#     i+=1
#     print i
#     baseinfo = hotel_dao.get_baseinfo_by_hotelname(comm[10].encode('utf-8'), '南京')
#     for info in baseinfo:
#         if info[3].encode('utf-8') == '途牛':
#             hotel_comm.append({
#                 "guid":uuid.uuid1(),
#                 "username":comm[1],
#                 "remark":comm[2],
#                 "comm_time":comm[3],
#                 "comm_type":comm[6],
#                 "user_type":comm[4],
#                 "senti_value":comm[7],
#                 "viewpoint":comm[8],
#                 "word_freq":comm[9],
#                 "baseinfo_id":info[0],
#             })
# hotel_dao.save_remarks(hotel_comm)

print '=============Tuniu Done================='

xiecheng_comms = xiecheng_dao.get_comments()
print len(xiecheng_comms)
hotel_name = ""
baseinfo_id = ""
hotel_comm = []
# 遍历评论
i = 0
for comm in xiecheng_comms:
    i+=1
    print i
    # 当酒店名发生改变时，更新baseinfo的id
    if comm[0] != hotel_name:
        baseinfo_id = ""
        hotel_name = comm[0]
        baseinfo = hotel_dao.get_baseinfo_by_hotelname(hotel_name.encode('utf-8'), '南京')
        for info in baseinfo:
            if info[3] == u'携程':
                baseinfo_id = info[0]
    if baseinfo_id != "":
        try:
            hotel_comm.append({
                "guid":uuid.uuid1(),
                "username":comm[1],
                "remark":comm[6],
                "intime":re.sub(u"\(本次服务由代理商提供\)",u"",comm[3]),
                "comm_score":float(comm[2]) if comm[2]!=u'' else None,
                "user_type":comm[4],
                "baseinfo_id":baseinfo_id,
                "senti_value":comm[7],
                "viewpoint":comm[8]
            })
        except:
            traceback.print_exc()
            print comm
print len(hotel_comm)
hotel_dao.save_remarks(hotel_comm)

print '=============XieCheng Done================='