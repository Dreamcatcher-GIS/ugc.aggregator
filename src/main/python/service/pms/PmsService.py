# -*- coding:utf-8 -*-

import re
import json
import random
import datetime
from shapely.geometry import Polygon
from shapely.geometry import Point

from dao.hotel.HotelDAO import HotelDAO
from dao.pms.pmsdao import PmsDAO
from setting import local_hotel_setting

# 配置数据库
dao_setting = local_hotel_setting

class PmsService(object):
    def __init__(self):
        self.hotel_dao = HotelDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])
        self.pms_dao = PmsDAO(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])
        self.hotelname = '南京天丰大酒店'
        # 房间推荐时 的 阈值 ；房间推荐是 先综合所有历史评论，更新到 房间表后（每一项的评分）再 按此分数 推荐
        self.keyvalue = 0.1
        # 质检 的 阈值 ； 实时爬取 remark表里的
        self.redvalue = 0.03
        self.yellowvalue = 0.1
    '''
    0 旨在更新和配置数据库
    1 pms前台调用的服务
    '''

    '''
    1用户登录
    '''
    def user_login(self,username,password,usertype):
        result = self.pms_dao.user_login(username)
        print type(result)
        for re in result:
            if re[2] ==password or re[3]==usertype:
                return True
        return False

    '''
    1获取房间信息表
    '''
    def get_hotel_roominfos(self):
        result_data = self.hotel_dao.get_records('roominfo')
        return result_data

    '''
    1获取顾客信息表
    '''
    def get_hotel_guestinfos(self):
        result_data = self.hotel_dao.get_records('guestinfo')
        return result_data

    '''
    1基于用户评论 协同过滤 推荐房间
    '''
    def room_recommend(self,guestname,roomtype):
        #顾客的所有关注点
        view_points = {}
        #顾客的差评关注点 小于value值的
        review_points = []
        #评分排序
        toppoint = {}
        #取用户所有点评过的实体及其情感值
        guest_remarks = self.pms_dao.get_guest_remark(guestname)
        for remark in guest_remarks:
            points = json.loads(remark[9])
            for point,value in points.iteritems():
                if point in view_points:
                    if view_points[point] > value:
                        view_points[point] = value
                else:
                    view_points[point] = value
        #将情感值小于keyvalue的实体保存起来
        for point,value in view_points.iteritems():
            if value < self.keyvalue:
                review_points.append({
                    'point':point,
                    'value':[]
                })
        #
        rooms =self.pms_dao.get_records('roominfo')
        for point in review_points:
            for room in rooms:
                if point['point'] in room[5]:
                    dictroompoint = json.loads(room[5])
                    point['value'].append((
                        room[0],dictroompoint[point['point']]
                    ))
                else:
                    continue
            #排序
            point['value'].sort(key=lambda x:x[1],reverse=True)
        #统计房间排名
        #print review_points
        for point in review_points:
            i = 0
            for r in point['value']:
                room = str(r[0])
                if room in toppoint:
                    toppoint[room] = i + toppoint[room]
                else:
                    toppoint[room] = i
                i += 1
                if i > len(point['value']):
                    break
        toppoint = sorted(toppoint.iteritems(),key=lambda x:x[1])
        print toppoint
        # TODO 推荐列表已经计算完成，只要再结合 房间类型即可推荐

    '''
    1添加用户入住记录，修改房间信息表
    '''
    def add_record(self,roomid,guestid,intime,outtime,charge):
        #判断用户是否在住，即存在于房间信息表中，如果不存在就执行下一步
        if self.check_user_roominfo(guestid):
            return False
        else:
            #添加记录
            #intime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.pms_dao.add_record(roomid,guestid,intime,outtime,charge)
            #修改房间 guestid
            self.pms_dao.alter_roominfo(roomid,guestid)
            return True

    '''
    1(质检)依据 楼层号 查询 各房间 的 状态 例如标红
    '''
    def query_floorstate(self,floornum,time):
        if len(floornum)==1:
            floornum = "0"+floornum
        remarklist = []
        hotelid = self.pms_dao.query_hotelid_from_hotelname(self.hotelname)
        condition = "(roomid='%s')AND(" + " OR ".join(["baseinfo_id= '"+id[0]+"'" for id in hotelid])+ ")"
        # 依据楼层号，确定 rooms
        rooms = self.pms_dao.get_hotel_rooms(floornum)
        for room in rooms:
            redpoint = []
            yellowpoint = []
            greenpoint = []
            viewpointlist = self.pms_dao.get_condition_column('viewpoint','remark',condition%(room[0]))
            for item in viewpointlist:
                for i in item:
                    if i == None:
                        continue
                    dicti = json.loads(i)
                    for k,v in dicti.iteritems():
                        #print k,v
                        if v < self.redvalue:
                            if k not in redpoint:
                                redpoint.append(k)
                        elif v < self.yellowvalue:
                            if k not in yellowpoint:
                                yellowpoint.append(k)
                        else:
                            if k not in greenpoint:
                                greenpoint.append(k)
            remarklist.append([room[0], [redpoint,yellowpoint,greenpoint],[room[1],room[3],room[4]]])
        return remarklist

    '''
    1(质检) 通过前台点击房间 传入 roomid 返回与房间相关的评论
    '''
    def get_room_remark(self,roomid):
        commentlist = []
        hotelid = self.pms_dao.query_hotelid_from_hotelname(self.hotelname)
        condition = "(roomid='%s')AND(" + " OR ".join(["baseinfo_id= '"+id[0]+"'" for id in hotelid])+ ")"
        roomremark = self.pms_dao.get_condition_column('*','remark',condition%(roomid))

        for remark in roomremark:
            comment =  remark[2]
            viewpoint = json.loads(remark[9])
            for point in viewpoint:
                #print point
                if point in comment:
                    if viewpoint[point] < self.redvalue:
                        comment = re.sub(point,'<a title="'+'%.2f'%viewpoint[point]+'" data-toggle="tooltip" href="#"><b> <span style="color:red">'+point+'</span></b></a>',comment)
                    elif viewpoint[point] < self.yellowvalue:
                        comment = re.sub(point,'<a title="'+'%.2f'%viewpoint[point]+'" data-toggle="tooltip" href="#"><b> <span style="color:yellow">'+point+'</span></b></a>',comment)
                    else:
                        comment = re.sub(point,'<a title="'+'%.2f'%viewpoint[point]+'" data-toggle="tooltip" href="#"><b>'+point+'</b></a>',comment)
            commentlist.append(comment)
        return commentlist

    '''
    1(质检)依据实体选择 获取remark
    '''
    def get_remark_by_points(self,points,floornum):
        points = points.split(',')
        if len(floornum)==1:
            floornum = "0"+floornum
        remarklist = []
        hotelid = self.pms_dao.query_hotelid_from_hotelname(self.hotelname)
        condition = "(roomid='%s')AND(" + " OR ".join(["baseinfo_id= '"+id[0]+"'" for id in hotelid])+ ")"
        # 依据楼层号，确定 rooms
        rooms = self.pms_dao.get_hotel_rooms(floornum)
        #循环房间
        for room in rooms:
            #依据房间id 抽取评论
            viewpointlist = self.pms_dao.get_condition_column('viewpoint,remark,roomid','remark',condition%(room[0]))
            #循环 获取到 的房间评论
            for viewpoint in viewpointlist:
                #房间实体词
                sqlpoint = json.loads(viewpoint[0])
                #评论
                comment = viewpoint[1]
                #循环 前端传过来的 实体
                for point in points:
                    point = unicode(point,"utf-8")
                    #判断 前端实体 是否在 当前这个房间的 这条评论中，如果在就添加到 remarklist
                    if point in sqlpoint:
                        roomnum = self.pms_dao.get_condition_column('roomnum','roominfo',"roomid='%s'"%(viewpoint[2]))
                        #处理 comment 中实体 添加title属性

                        if sqlpoint[point] < self.redvalue:
                            comment = re.sub(point,'<a title="'+'%.2f'%sqlpoint[point]+'" data-toggle="tooltip" href="#"><b> <span style="color:red">'+point+'</span></b></a>',comment)
                        elif sqlpoint[point] < self.yellowvalue:
                            comment = re.sub(point,'<a title="'+'%.2f'%sqlpoint[point]+'" data-toggle="tooltip" href="#"><b> <span style="color:yellow">'+point+'</span></b></a>',comment)
                        else:
                            comment = re.sub(point,'<a title="'+'%.2f'%sqlpoint[point]+'" data-toggle="tooltip" href="#"><b>'+point+'</b></a>',comment)

                        remarklist.append([roomnum[0][0],comment])

        return remarklist

    '''
    1判断用户是否在住
    '''
    def check_user_roominfo(self,guestid):
        result = self.hotel_dao.get_records('roominfo')
        for re in result:
            if re[4]==guestid:
                return True
        return False
        pass
    '''
    0随机更新remark表的roomid
    '''
    def insert_roomid(self):
        guidlist = self.pms_dao.get_column_table('guid','remark')
        roomids = list(range(1,217))
        records = []
        for i in guidlist:
            records.append({
                'guid':i[0],
                'roomid':random.sample(roomids,1)[0]
            })
        self.pms_dao.update_roomid(records)
        pass
    '''
    0更新guest表
    '''
    def update_guest(self):
        records = []
        usernamelist = self.pms_dao.get_column_table('username','remark')
        for name in usernamelist:
            records.append({
                'guestname':name[0]
            })
        self.pms_dao.save_records('guestinfo',records)

    '''
    0更新roominfo表的viewpoint 南京苏宁威尼斯酒店
    '''
    def update_roominfo(self):
        hotelid = self.pms_dao.query_hotelid_from_hotelname(self.hotelname)
        condition = "(roomid='%s')AND(" + " OR ".join(["baseinfo_id= '"+id[0]+"'" for id in hotelid])+ ")"
        #获取到房间列表，并逐一循环
        roomlist = self.pms_dao.get_column_table('roomid','roominfo')
        for room in roomlist:
            print room
            #对每一个房间 取 remark 后，更新remark
            commlist = {}
            viewpointlist = self.pms_dao.get_condition_column('viewpoint','remark',condition%(room))
            for item in viewpointlist:
                for i in item:
                    if i == None:
                        continue
                    dicti = json.loads(i)
                    for k in dicti:
                        if k in commlist:
                            commlist[k] = (commlist[k] + dicti[k]) / 2
                        else:
                            commlist[k] = dicti[k]
            remarklist = json.dumps(commlist,ensure_ascii=False)
            self.pms_dao.updata_roominfo_viewpoint(remarklist,room[0])


if __name__ == "__main__":
    p = PmsService()
    #先要添加 remark表中的roomid字段，zai
    p.insert_roomid()
    #p.update_guest()
    #p.update_roominfo()
    #房间推荐，
    #p.room_recommend('永恒不变','')
    #房间质检，
    #p.query_floorstate('04','')
    #p.get_room_remark('5')
    #p.get_remark_by_points("房间","4")
