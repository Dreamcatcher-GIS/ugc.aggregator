# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'


import json
import datetime
from shapely.geometry import Polygon
from shapely.geometry import Point

from dao.hotel.HotelDAO import HotelDAO
from setting import local_hotel_setting

# 配置数据库
dao_setting = local_hotel_setting


class HotelDataService(object):

    def __init__(self):
        self.hotel_dao = HotelDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])

    def get_baseinfo_by_location_id(self, location_id_str):
        location_id_list = location_id_str.split(',')
        result_data = []
        for location_id in location_id_list:
            baseinfo = self.hotel_dao.get_baseinfo_by_location_id(location_id)
            ota_list = []
            for info in baseinfo:
                ota_list.append({"id":info[0],"location_id":info[2], "ota":info[3]})
            result_data.append(ota_list)
        return result_data

    def get_comm_type_score_statics(self, baseinfo_id, ota):
        result_data = None
        if ota==u'携程':
            result_data = self.hotel_dao.get_comm_score_statics(baseinfo_id)
        elif ota==u'途牛':
            result_data = self.hotel_dao.get_comm_type_statics(baseinfo_id)
        return result_data

    '''
    酒店评论观点统计
    '''
    def get_comm_viewpoints(self, baseinfo_id_str):
        baseinfo_id_list = baseinfo_id_str.split(',')
        viewpoints = []
        for i in range(0, len(baseinfo_id_list)):
            viewpoint = self.get_comm_viewpoint(baseinfo_id_list[i])
            location_info = self.hotel_dao.get_location_info_by_baseinfo_id(baseinfo_id_list[i])
            hotel_name = location_info[0][3] if len(location_info)>0 else ""
            viewpoints.append({"hotel_name":hotel_name, "viewpoint":viewpoint})
        return viewpoints

    def get_comm_viewpoint(self, baseinfo_id):
        viewpoint_statics = {}
        comments = self.hotel_dao.get_remarks_by_baseinfo_id(baseinfo_id)
        for comment in comments:
            # 反序列化字符串
            viewpoint = json.loads(comment[9])
            # 遍历key值
            for key in viewpoint:
                if key in viewpoint_statics:
                    viewpoint_statics[key] = (viewpoint_statics[key] + viewpoint[key])/2
                else:
                    viewpoint_statics[key] = viewpoint[key]
        return viewpoint_statics

    '''
    酒店评论形容词统计
    '''
    def get_comm_adjective_statics(self, baseinfo_id):
        adjective_statics = {}
        comments = self.hotel_dao.get_remarks_by_baseinfo_id(baseinfo_id)
        for comment in comments:
            # 反序列化字符串
            adjectives = json.loads(comment[10])
            # 遍历key值
            for key in adjectives:
                if key in adjective_statics:
                    adjective_statics[key] = adjective_statics[key] + adjectives[key]
                else:
                    adjective_statics[key] = adjectives[key]
        adjective_statics = sorted(adjective_statics.iteritems(),key=lambda asd:asd[1],reverse=True)
        return adjective_statics

    def get_user_trace(self, baseinfo_id, start_time=None, end_time=None, ring_str=None):
        result_data = {}
        result_data["line"] = []
        result_data["point"] = {}

        polygon = None

        user_list = self.hotel_dao.get_hotel_trace_users(baseinfo_id)
        print len(user_list)
        # 遍历用户名
        for user in user_list:
            # 获取该用户的评论数据（评论对应的酒店名和地点）
            remarks = self.hotel_dao.get_remarks_by_username(user[0])
            # 生成轨迹线
            for i in range(0,len(remarks)-1):
                if ring_str is not None:
                    if polygon is None:
                        ring = json.loads(ring_str)
                        polygon = Polygon(ring)
                    p1 = Point(remarks[i][14],remarks[i][13])
                    p2 = Point(remarks[i+1][14],remarks[i+1][13])
                    # 如果轨迹点不在这个区域内，则不存储
                    if not polygon.intersects(p1) or not polygon.intersects(p2):
                        continue
                if remarks[i][13] != remarks[i+1][13]:
                    start_point = {"name":remarks[i][12],"geoCoord":[remarks[i][14],remarks[i][13]]}
                    end_point = {"name":remarks[i+1][12],"geoCoord":[remarks[i+1][14],remarks[i+1][13]]}
                    result_data["line"].append([start_point,end_point])
            # 生成轨迹点
            for remark in remarks:
                if ring_str is not None:
                    if polygon is None:
                        ring = json.loads(ring_str)
                        polygon = Polygon(ring)
                    p = Point(remark[14],remark[13])
                    # 如果该点不在这个区域内，则不存储
                    if not polygon.intersects(p):
                        continue
                coord_str = str(remark[13])+","+str(remark[14])
                if coord_str not in result_data["point"]:
                    result_data["point"][coord_str] = {
                        "name":remark[12],
                        "geoCoord":[
                            remark[14],
                            remark[13]
                        ],
                        "value":1
                    }
                else:
                    result_data["point"][coord_str]["value"]+=1
        return result_data