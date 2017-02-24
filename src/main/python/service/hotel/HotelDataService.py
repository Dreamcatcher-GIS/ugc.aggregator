# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer，LiuYang'


import json
import re
import random
import datetime
import traceback
from shapely.geometry import Polygon
from shapely.geometry import Point

from dao.hotel.HotelDAO import HotelDAO
from setting import local_hotel_setting

# 配置数据库
dao_setting = local_hotel_setting


class HotelDataService(object):

    def __init__(self):
        self.hotel_dao = HotelDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])

    '''
    检查登录用户账号密码的合法性
    '''
    def check_user(self, user_name, password):
        userdata = self.hotel_dao.get_user(user_name)
        result_data = {"baseinfo": [], 'location':{}, 'user':{} }
        if len(userdata) < 1:
            return None
        for line in userdata:
            result_data['location']['location_id'] = line[0]
            result_data['location']['x'] = line[1]
            result_data['location']['y'] = line[2]
            result_data['location']['hotel_name'] = line[3]
            result_data['location']['city'] = line[4]
            result_data['location']['address'] = line[5]
            result_data['baseinfo'].append(
                {"id": line[6], "url": line[7], "OTA": line[9], "comm_num": line[10], "img":line[13]}
            )
            result_data['user']['id'] = line[15]
            result_data['user']['user_name'] = line[16]
            result_data['user']['password'] = line[17]
            result_data['user']['corporation'] = line[19]
            result_data['user']['img'] = line[20]

        if password != result_data['user']['password']:
            return None
        else:
            return result_data

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
    通过酒店名获取酒店的实体观点
    '''
    def get_comm_viewpoints(self, hotel_name_str):
        hotel_name_list = hotel_name_str.split(',')
        viewpoints = []
        for i in range(0, len(hotel_name_list)):
            viewpoint = self.get_comm_viewpoint(hotel_name_list[i])
            viewpoints.append({"hotel_name":hotel_name_list[i], "viewpoint":viewpoint})
        return viewpoints

    '''
    对酒店的评论进行统计，得到酒店实体观点
    '''
    def get_comm_viewpoint(self, hotel_name):
        viewpoint_statics = {}
        comments = self.hotel_dao.get_remarks_by_hotel_name(hotel_name.encode('utf-8'))
        for comment in comments:
            try:
                # 反序列化字符串
                viewpoint = json.loads(comment[9])
                # 遍历key值
                for key in viewpoint:
                    if key in viewpoint_statics:
                        viewpoint_statics[key] = (viewpoint_statics[key] + viewpoint[key])/2
                    else:
                        viewpoint_statics[key] = viewpoint[key]
            except:
                traceback.print_exc()
                continue
        return viewpoint_statics

    '''
    酒店评论形容词统计
    '''
    def get_comm_adjective_statics(self, baseinfo_id):
        adjective_statics = {}
        comments = self.hotel_dao.get_remarks_by_baseinfo_id(baseinfo_id)
        for comment in comments:
            # 反序列化字符串
            try:
                adjectives = json.loads(comment[10])
                # 遍历key值
                for key in adjectives:
                    if key in adjective_statics:
                        adjective_statics[key] = adjective_statics[key] + adjectives[key]
                    else:
                        adjective_statics[key] = adjectives[key]
            except:
                continue
        adjective_statics = sorted(adjective_statics.iteritems(),key=lambda asd:asd[1],reverse=True)
        return adjective_statics


    def get_user_flow_to_html(self, hotel_name, base_info_id_str, page, count=10, start_time=None, end_time=None, ring_str=None):
        baseinfo_id_list = base_info_id_str.split(',')
        result_data = {}
        html = ""
        for baseinfo_id in baseinfo_id_list:
            if baseinfo_id != "":
                data = self.get_trace(baseinfo_id, start_time, end_time, ring_str)
                for key in data["point"]:
                    if data["point"][key]["name"] in hotel_name:
                        continue
                    if key not in result_data:
                        result_data[key] = data["point"][key]
                    else:
                        result_data[key]["value"] += data["point"][key]["value"]
        result_data = sorted(result_data.iteritems(),key=lambda asd:asd[1]["value"],reverse=True)
        for hotel in result_data[count*(page-1):count*page]:
            html += "<tr><td name='name'>%s</td><td name='count'>%s</td><td name='price'>%s</td></tr>" % (hotel[1]["name"], hotel[1]["value"], random.randint(340,500))
        return {"pageNum": len(result_data)/count + 1,"html": html}


    def get_user_trace(self, baseinfo_id_str, start_time=None, end_time=None, ring_str=None):
        baseinfo_id_list = baseinfo_id_str.split(',')
        result_data = []
        for baseinfo_id in baseinfo_id_list:
            if baseinfo_id != "":
                data = self.get_trace(baseinfo_id, start_time, end_time, ring_str)
                result_data.append(data)
        return result_data


    def get_trace(self, baseinfo_id, start_time=None, end_time=None, ring_str=None):
        result_data = {}
        result_data["line"] = []
        result_data["point"] = {}

        polygon = None

        user_list = self.hotel_dao.get_hotel_trace_users(baseinfo_id)
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
                    p1 = Point(remarks[i][14],remarks[i][15])
                    p2 = Point(remarks[i+1][14],remarks[i+1][15])
                    # 如果轨迹点不在这个区域内，则不存储
                    if not polygon.intersects(p1) or not polygon.intersects(p2):
                        continue


                if remarks[i][15] != remarks[i+1][15]:
                    start_point = {"name":remarks[i][13],"geoCoord":[remarks[i][14],remarks[i][15]]}
                    end_point = {"name":remarks[i+1][13],"geoCoord":[remarks[i+1][14],remarks[i+1][15]]}
                    result_data["line"].append([start_point,end_point])

            # 生成轨迹点
            for remark in remarks:
                if ring_str is not None:
                    if polygon is None:
                        ring = json.loads(ring_str)
                        polygon = Polygon(ring)
                    p = Point(remark[14],remark[15])
                    # 如果该点不在这个区域内，则不存储
                    if not polygon.intersects(p):
                        continue
                coord_str = str(remark[15])+","+str(remark[14])
                if coord_str not in result_data["point"]:
                    result_data["point"][coord_str] = {
                        "name":remark[13],
                        "geoCoord":[
                            remark[14],
                            remark[15]
                        ],
                        "value":1
                    }
                else:
                    result_data["point"][coord_str]["value"]+=1
        return result_data

    '''
    根据文本获取相关评论
    '''
    def get_comm_by_text(self, hotel_name, page, text = None, count = 20, ota = None):
        comments = self.hotel_dao.get_remarks_by_text(hotel_name.encode("utf-8"), text, ota)
        comments_changed = []
        # 遍历评论，加粗其中关于酒店实体的文字
        text = text.decode("utf-8") if text != None else None
        for comm in comments[count*(page-1):count*page]:
            comm = list(comm)
            viewpoint = json.loads(comm[9])
            for feature in viewpoint:
                if feature != text:
                    comm[2] = re.sub(feature,'<a title="'+ '%.2f'%viewpoint[feature] + '" data-toggle="tooltip" href="#"><b>' + feature + '</b></a>',comm[2])
                else:
                    comm[2] = re.sub(feature,'<a title="'+ '%.2f'%viewpoint[feature] + '" data-toggle="tooltip" href="#"><b> <span style="color:red">' + feature + '</span></b></a>',comm[2])
            for adjective in json.loads(comm[9]):
                comm[2] = re.sub(adjective,'<b>' + adjective + '</b>',comm[2])
            comments_changed.append(comm)
        return {"pageNum": len(comments)/20 + 1,"comments_info": comments_changed}

    def get_location(self, location_id):
        data = self.hotel_dao.get_hotel_name_by_location_id(location_id)
        if len(data) ==1:
            location = data[0]
            return {
                'data':{
                'location_id': location[0],
                'x': location[1],
                'y': location[2],
                'hotel_name': location[3],
                'address': location[5]
                },
                'status': 200
            }
        return {'status': 0}