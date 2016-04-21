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


    # 从数据库获取酒店名称所对应房间信息
    def getbed_info(self,hotelname):
        hotel_list = hotelname.split(',')
        for hotel in hotel_list:
            bedinfo = self.get_bedcommpent(hotel)
            self.bed[hotel] = bedinfo
        return self.bed

    def get_bedcommpent(self,hotel):
        bedInfo = {}
        bedtype = [] # 所有床型
        bedtypeinfo = {}
        bedlist = self.dao._returnbed(hotel)
        for bedList in bedlist:
                if bedList[1] in bedtype:
                    pass
                else:bedtype.append(bedList[1])
        for bedList in bedlist:
            if bedList[1] in bedtype:
                bedpraise = re.sub('\D','',str(bedList[7]))
                bedtypeinfo[bedList[8]] = bedpraise
            Bedtypeinfo = sorted(bedtypeinfo.iteritems(),key=lambda d:d[0].split('-'))
            bedInfo[bedList[1]] = Bedtypeinfo
        return bedInfo


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