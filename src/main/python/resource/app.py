# -*- coding:utf-8 -*-
__author__ = 'LiuYang,DreamCathcer，pengshaowei'

from flask import Flask
from flask import abort
from flask import request
from flask.ext.cors import CORS
import json
import traceback
import redis
r = redis.Redis(host='localhost',port=6379,db=0)

from service.weibo.WeiboService import WeiboService
from service.hotel.HotelDataService import HotelDataService
from service.hotel.TuniuDataService import TuniuDataService
from service.hotel.xiecheng.XichengDataService import XichengDataService
from service.pms.PmsService import PmsService

app = Flask(__name__)
CORS(app)

weibo_service = WeiboService()
tuniu_data_service = TuniuDataService()
xiecheng_data_service = XichengDataService()
hotel_data_service = HotelDataService()
pms_service = PmsService()

@app.route('/ugc.hotel/rest/v100/weibo/get/nearby_timeline', methods=['GET'])
def weibo_nearbytimeline():
    try:
        data = weibo_service.get_all_weibo_nearby(
            request.args["lat"],
            request.args["lng"],
            request.args["starttime"],
            request.args["endtime"],
            request.args["range"]
        )
        return json.dumps(data)
    except:
        abort(404)


@app.route('/ugc.hotel/rest/v100/weibo/get/nearby_timeline/statics', methods=['GET'])
def weibo_nearbytimeline_wrapper():
    try:
        data = r.get(request.url)
        if data is None:
            data = weibo_service.get_all_weibo_nearby_async(
                request.args["lat"],
                request.args["lng"],
                int(request.args["starttime"]),
                int(request.args["endtime"]),
                int(request.args["range"])
            )
            data = json.dumps(weibo_service.nearby_weibo_statis_wrapper(data))
            r.set(request.url, data)
        return data
    except:
        traceback.print_exc()
        abort(404)


@app.route('/ugc.hotel/rest/v100/weibo/get/user_trace', methods=['GET'])
def get_weibo_user_trace():
    try:
        data = r.get(request.url)
        if data is None:
            data = weibo_service.get_weibo_users_timeline_statics(request.args["id"])
            data = json.dumps(data)
            r.set(request.url, data)
        return data
    except:
        traceback.print_exc()
        abort(404)


@app.route('/ugc.hotel/rest/v100/hotel/get/baseinfo', methods=['GET'])
def get_baseinfo_by_location_id():
    try:
        return json.dumps(hotel_data_service.get_baseinfo_by_location_id(request.args["location_id"]))
    except:
        traceback.print_exc()
        abort(404)


@app.route('/ugc.hotel/rest/v100/hotel/get/CommTypeNum', methods=['GET'])
def get_comm_type_num():
    try:
        return json.dumps(tuniu_data_service.get_comm_type_num(request.args["hotel_name"]))
    except:
        abort(404)


@app.route('/ugc.hotel/rest/v100/hotel/get/type_score/statics', methods=['GET'])
def get_comm_type_score_statics():
    try:
        return json.dumps(hotel_data_service.get_comm_type_score_statics(request.args["baseinfo_id"], request.args["ota"]))
    except:
        abort(404)


@app.route('/ugc.hotel/rest/v100/hotel/get/viewpoint', methods=['GET'])
def get_viewpoint():
    try:
        data = json.dumps(hotel_data_service.get_comm_viewpoints(request.args["hotel_name"]))
        return data
    except:
        abort(404)


@app.route('/ugc.hotel/rest/v100/hotel/get/tuniu/viewpoint', methods=['GET'])
def get_viewpoint_tuniu():
    try:
        data = json.dumps(hotel_data_service.get_comm_viewpoints(request.args["hotel_name"]))
        return data
    except:
        abort(404)


@app.route('/ugc.hotel/rest/v100/hotel/get/adjective', methods=['GET'])
def get_adjective_statics():
    try:
        return json.dumps(hotel_data_service.get_comm_adjective_statics(request.args["baseinfo_id"]))
    except:
        traceback.print_exc()
        abort(404)


@app.route('/ugc.hotel/rest/v100/hotel/get/comments', methods=['GET'])
def get_comm_by_text():
    try:
        ota = request.args["ota"].encode("utf-8") if 'ota' in request.args else None
        text = request.args["text"].encode("utf-8") if 'text' in request.args else None
        data = hotel_data_service.get_comm_by_text(
            hotel_name=request.args["hotel_name"],
            page=int(request.args["page"]),
            text=text,
            ota=ota
        )
        return json.dumps(data)
    except:
        traceback.print_exc()
        abort(404)


'''
发布酒店设施坐标数据
'''
@app.route('/ugc.hotel/rest/v100/map/get/aroundfacilities', methods=['GET'])
def get_around_facilities():
    try:
        data = xiecheng_data_service.get_around_facilities()
        return json.dumps(data)
    except:
        abort(404)


'''
发布酒店最远距离数据
'''
@app.route('/ugc.hotel/rest/v100/map/get/maxdistance', methods=['GET'])
def get_max_distance():
    try:
        data = xiecheng_data_service.get_max_distance()
        return json.dumps(data)
    except:
        abort(404)


'''
发布房间数据
'''
@app.route('/ugc.hotel/rest/v100/map/get/hotelbedinfo', methods=['GET'])
def get_hotel_bedinfo():
    try:
        data = tuniu_data_service.getbed_info(request.args["hotel_name"])
        return json.dumps(data)
    except:
        abort(404)


'''
发布房间各房型剩余房间数
'''
@app.route('/ugc.hotel/rest/v100/map/get/hotelroomnum', methods=['GET'])
def get_hotel_roomnum():
    try:
        data = tuniu_data_service.getbed_roomnum(request.args["hotel_name"])
        return json.dumps(data)
    except:
        abort(404)


'''
发布用户轨迹数据
'''
@app.route('/ugc.hotel/rest/v100/hotel/get/user_trace', methods=['GET'])
def get_hotel_user_trace():
    try:
        data = r.get(request.url)
        if data is None:
            if "ring_str" in request.args:
                data = hotel_data_service.get_user_trace(request.args["baseinfo_id"].encode("utf-8"), ring_str=request.args["ring_str"])
            else:
                data = hotel_data_service.get_user_trace(request.args["baseinfo_id"].encode("utf-8"))
            data = json.dumps(data)
            r.set(request.url, data)
        return data
    except:
        traceback.print_exc()
        abort(404)


'''
客流流出数据
'''
@app.route('/ugc.hotel/rest/v100/hotel/get/html/customer_to', methods=['GET'])
def get_user_flow_to_html():
    try:
        # data = None
        data = r.get(request.url)
        if data is None:
            if "ring_str" in request.args:
                ring_str = request.args["ring_str"]
            else:
                ring_str = None
            data = hotel_data_service.get_user_flow_to_html(
                    request.args["hotel_name"],
                    request.args["baseinfo_id"].encode("utf-8"),
                    int(request.args["page"]),
                    ring_str=ring_str
                )
            data = json.dumps(data)
            r.set(request.url, data)
        return data
    except:
        traceback.print_exc()
        abort(404)


'''
检查用户登录合法性
'''
@app.route('/ugc.hotel/rest/v100/hotel/get/check_user', methods=['GET'])
def check_user():
    try:
        data = hotel_data_service.check_user(request.args["user_name"], request.args["password"])
        if data is None:
            return json.dumps({'status': 0, 'errorMsg': '用户账户错误'})
        else:
            return json.dumps({'status': 200, 'data': [data]})
    except:
        traceback.print_exc()
        abort(404)

'''
以下是（质检）以及（推荐）
'''
'''
（质检）依据楼层号获取酒店楼层各房间的评论状态
'''
@app.route('/ugc.hotel/rest/v100/quality/floorstate',methods=['GET'])
def query_floorstate():
    try:
        result = r.get(request.url)
        #result = None
        if result is None:
            result = pms_service.query_floorstate(
                request.args['floornum'].encode('utf-8'),
                request.args['time'].encode('utf-8')
            )
            result = json.dumps(result,ensure_ascii=False)
            #print result
            r.set(request.url,result)
        return result
    except Exception,e:
        print e
        traceback.print_exc()
        abort(404)

'''
(质检)依据roomid 来获取到酒店的房间的 评论
'''
@app.route('/ugc.hotel/rest/v100/quality/getroomremark',methods=['GET'])
def get_room_remark():
    try:
        result =r.get(request.url)
        #result = None
        if result is None:
            result = pms_service.get_room_remark(request.args['roomid'].encode('utf-8'))
            result = json.dumps(result,ensure_ascii=False)
            r.set(request.url,result)
        return result
    except:
        traceback.print_exc()
        abort(404)

'''
(质检)依据实体选择 获取remark
'''
@app.route('/ugc.hotel/rest/v100/quality/getRemarkByPoints',methods=['GET'])
def get_remark_by_points():
    try:
        result =r.get(request.url)
        #result = None
        if result is None:
            result = pms_service.get_remark_by_points(
                request.args['points'].encode('utf-8'),
                request.args['floornum'].encode('utf-8')
            )
            result = json.dumps(result,ensure_ascii=False)
            r.set(request.url,result)
        return result
    except:
        traceback.print_exc()
        abort(404)

'''
(推荐)pms用户登录
'''
@app.route('/ugc.hotel/rest/v100/user/login',methods=['GET'])
def user_login():
    try:
        result =r.get(request.url)
        if result is None:
            result = pms_service.user_login(
                request.args['username'].encode('utf-8'),
                request.args['password'].encode('utf-8'),
                request.args['usertype'].encode('utf-8'))
            r.set(request.url,result)
        return result
    except:
        traceback.print_exc()
        abort(404)

'''
(推荐)pms加载酒店房间
'''
@app.route('/ugc.hotel/rest/v100/room/get/room_info',methods=['GET'])
def get_hotel_rooms():
    try:
        data = pms_service.get_hotel_roominfos()
        data = json.dumps(data)
        return data
    except:
        traceback.print_exc()
        abort(404)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port = 5000)