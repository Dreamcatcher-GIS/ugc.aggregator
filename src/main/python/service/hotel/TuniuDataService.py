# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import json
import re

from dao.hotel.TuniuDao import TuniuDAO
from setting import local_hotel_setting

# 配置数据库
dao_setting = local_hotel_setting

class TuniuDataService(object):

    def __init__(self):
        self.dao = TuniuDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])
         # 存储床价信息
        self.bed = {}


    '''
    返回各房型剩余房间数信息
    '''
    def getbed_roomnum(self,hotelname):
        roomshengyv = []
        hotel_List = hotelname.split(',')
        hotel1 = [["3-21","4-14","4-17","4-19","4-21"],["大床房","豪华套间","双人标间","商务大床房","精选大床房"],[28,39,55,16,71],[33,65,21,56,85],[13,16,59,41,26],[56,90,12,52,32],[42,16,59,36,21]]
        hotel2 = [["3-21","4-14","4-17","4-19","4-21"],["标准双人房","大床房","精选大床房","商务大床房","豪华家庭房"],[55,13,62,42,190],[63,26,75,41,64],[20,62,61,42,71],[13,65,26,58,49],[74,52,68,23,62]]
        hotel3 = [["3-21","4-14","4-17","4-19","4-21"],["精选大床房","特价房","豪华套间","豪华大床房","大床房"],[28,56,23,91,42],[62,52,12,36,55],[100,56,23,81,20],[63,59,74,52,12],[63,69,65,21,35]]
        hotel4 = [["3-21","4-14","4-17","4-19","4-21"],["豪华家庭房","大床房","商务大床房","豪华套间","精选大床房"],[55,21,25,69,54],[74,51,23,65,85],[51,20,52,36,57],[85,42,16,32,54],[63,56,85,41,21]]
        if len(hotel_List) == 1:
            roomshengyv.append(hotel_List[0])
            roomshengyv.append(hotel1)
            return roomshengyv
        elif len(hotel_List) == 2:
            roomshengyv.append(hotel_List[0])
            roomshengyv.append(hotel1)
            roomshengyv.append(hotel_List[1])
            roomshengyv.append(hotel2)
            return roomshengyv
        elif len(hotel_List) == 3:
            roomshengyv.append(hotel_List[0])
            roomshengyv.append(hotel1)
            roomshengyv.append(hotel_List[1])
            roomshengyv.append(hotel2)
            roomshengyv.append(hotel_List[2])
            roomshengyv.append(hotel3)
            return roomshengyv
        else:
            roomshengyv.append(hotel_List[0])
            roomshengyv.append(hotel1)
            roomshengyv.append(hotel_List[1])
            roomshengyv.append(hotel2)
            roomshengyv.append(hotel_List[2])
            roomshengyv.append(hotel3)
            roomshengyv.append(hotel_List[3])
            roomshengyv.append(hotel4)
            return roomshengyv





    '''
    从数据库获取酒店名称所对应房间信息
    '''
    # 从数据库获取酒店名称所对应房间信息
    def getbed_info(self,hotelname):
        bed = []
        hotel_list = hotelname.split(',')
        for hotel in hotel_list:
            bedinfo = self.get_bedcommpent(hotel)
            bed.append(hotel)
            bed.append(bedinfo)
        return bed

    def get_bedcommpent(self,hotel):
        dataNum = self.getdatanum(hotel)
        bedInfo = []
        bedtype = [] # 所有床型
        bedtypeinfo = [] #去掉了重复的床型
        # 添加日期对应，价格信息
        bedprais = {}
        bedlist = self.dao._returnbed(hotel)
        for bedList in bedlist:
            if bedList[1] in bedtype:
                pass
            else:bedtypeinfo.append(bedList[1])

        for bedtyp in bedtypeinfo:
            for bedList in bedlist:
                if bedList[1] == bedtyp:
                    bedpraise = re.sub('\D','',str(bedList[7]))
                    bedprais[bedList[8]] = bedpraise
                    if bedList[1] not in bedInfo:
                        if len(bedprais) == dataNum:
                            Bedtypeinfo = sorted(bedprais.iteritems(),key=lambda d:d[0].split('-'))
                            bedInfo.append(bedList[1])
                            bedInfo.append(Bedtypeinfo)
        return bedInfo

    # 获得日期总数
    def getdatanum(self,hotel):
        datanum = []
        bedlist = self.dao._returnbed(hotel)
        for bedList in bedlist:
            if bedList[8] not in datanum:
                datanum.append(bedList[8])
        return len(datanum)


    '''
    获取到酒店评论类型的评论数
    '''
    def get_comm_type_num(self, hotel_name):
        return self.dao.get_comm_type_num(hotel_name)

    '''
    酒店评论观点统计
    '''
    def get_comm_viewpoints(self,hotel_name):
        hotel_list = hotel_name.split(',')
        viewpoints = []
        for hotel in hotel_list:
            viewpoint = self.get_comm_viewpoint(hotel)
            viewpoints.append({"hotel_name":hotel,"viewpoint":viewpoint})
        return viewpoints

    def get_comm_viewpoint(self, hotel_name):
        viewpoint_statics = {}
        comments = self.dao.get_hotel_comments_by_name(hotel_name)
        for comment in comments:
            # 反序列化字符串
            viewpoint = json.loads(comment[8])
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
    def get_comm_adjective_statics(self, hotel_name):
        adjective_statics = {}
        comments = self.dao.get_hotel_comments_by_name(hotel_name)
        for comment in comments:
            # 反序列化字符串
            viewpoint = json.loads(comment[9])
            # 遍历key值
            for key in viewpoint:
                if key in adjective_statics:
                    adjective_statics[key] = adjective_statics[key] + viewpoint[key]
                else:
                    adjective_statics[key] = viewpoint[key]
        adjective_statics = sorted(adjective_statics.iteritems(),key=lambda asd:asd[1],reverse=True)
        return adjective_statics

    '''
    根据文本获取相关评论
    '''
    def get_comm_by_text(self, hotel_name, text, page, count=20):
        comments = self.dao.get_hotel_comments_by_text(hotel_name, text)
        comments_changed = []
        # 遍历评论，加粗其中关于酒店实体的文字
        for comm in comments[count*(page-1):count*page]:
            comm = list(comm)
            viewpoint = json.loads(comm[8])
            for feature in viewpoint:
                if feature != text:
                    comm[2] = re.sub(feature,'<a title="'+ '%.2f'%viewpoint[feature] + '" data-toggle="tooltip" href="#"><b>' + feature + '</b></a>',comm[2])
                else:
                    comm[2] = re.sub(feature,'<a title="'+ '%.2f'%viewpoint[feature] + '" data-toggle="tooltip" href="#"><b> <span style="color:red">' + feature + '</span></b></a>',comm[2])
            for adjective in json.loads(comm[9]):
                comm[2] = re.sub(adjective,'<b>' + adjective + '</b>',comm[2])
            comments_changed.append(comm)
        return {"pageNum":len(comments)/20 + 1,"comments_info":comments_changed}