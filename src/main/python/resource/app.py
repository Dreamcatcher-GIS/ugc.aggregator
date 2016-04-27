# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

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


app = Flask(__name__)
CORS(app)

weibo_service = WeiboService()
#xiechengDriverService = XiechengDriverService()
tuniu_data_service = TuniuDataService()
xiecheng_data_service = XichengDataService()
hotel_data_service = HotelDataService()


@app.route('/ugc.hotel/rest/v100/weibo/get/nearby_timeline', methods=['GET'])
def weibo_nearbytimeline():
    try:
        return json.dumps(weibo_service.get_all_weibo_nearby(request.args["lat"], request.args["lng"], request.args["starttime"], request.args["endtime"],request.args["range"]))
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
            r.set(request.url,data)
        return data
    except:
        traceback.print_exc()
        abort(404)

'''
微博用户轨迹
'''
@app.route('/ugc.hotel/rest/v100/weibo/get/user_trace',methods=['GET'])
def get_weibo_user_trace():
    try:
        data = r.get(request.url)
        if data is None:
            data = weibo_service.get_weibo_users_timeline_statics(request.args["id"])
            data = json.dumps(data)
            r.set(request.url,data)
        return data
    except:
        traceback.print_exc()
        abort(404)

@app.route('/ugc.hotel/rest/v100/hotel/get/baseinfo', methods=['GET'])
def get_baseinfo_by_location_id():
    try:
        return json.dumps(hotel_data_service.get_baseinfo_by_location_id(request.args["location_id"]))
    except:
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
        data = json.dumps(hotel_data_service.get_comm_viewpoints(request.args["baseinfo_id"],request.args["location_id"]))
        return data
    except:
        abort(404)

@app.route('/ugc.hotel/rest/v100/hotel/get/tuniu/viewpoint', methods=['GET'])
def get_viewpoint_tuniu():
    try:
        data = json.dumps(tuniu_data_service.get_comm_viewpoints(request.args["hotel_name"]))
        return data
    except:
        abort(404)

@app.route('/ugc.hotel/rest/v100/hotel/get/adjective', methods=['GET'])
def get_adjective_statics():
    try:
        return json.dumps(hotel_data_service.get_comm_adjective_statics(request.args["baseinfo_id"]))
    except:
        abort(404)

@app.route('/ugc.hotel/rest/v100/hotel/get/comments', methods=['GET'])
def get_comm_by_text():
    try:
        return json.dumps(tuniu_data_service.get_comm_by_text(request.args["hotel_name"],request.args["text"],int(request.args["page"])))
    except:
        traceback.print_exc()
        abort(404)

'''
发布酒店设施坐标数据
'''
@app.route('/ugc.hotel/rest/v100/map/get/aroundfacilities',methods=['GET'])
def get_around_facilities():
    try:
        data = xiecheng_data_service.get_around_facilities()
        return json.dumps(data)
    except:
        abort(404)

'''
发布酒店最远距离数据
'''
@app.route('/ugc.hotel/rest/v100/map/get/maxdistance',methods=['GET'])
def get_max_distance():
    try:
        data = xiecheng_data_service.get_max_distance()
        return json.dumps(data)
    except:
        abort(404)

'''
发布房间数据
'''
@app.route('/ugc.hotel/rest/v100/map/get/hotelbedinfo',methods=['GET'])
def get_hotel_bedinfo():
    try:
        data = tuniu_data_service.getbed_info(request.args["hotel_name"])
        return json.dumps(data)
    except:
        abort(404)

'''
发布房间各房型剩余房间数
'''
@app.route('/ugc.hotel/rest/v100/map/get/hotelroomnum',methods=['GET'])
def get_hotel_roomnum():
    try:
        data = tuniu_data_service.getbed_roomnum(request.args["hotel_name"])
        return json.dumps(data)
    except:
        abort(404)

'''
发布用户轨迹数据
'''
@app.route('/ugc.hotel/rest/v100/hotel/get/user_trace',methods=['GET'])
def get_hotel_user_trace():
    try:
        if "ring_str" in request.args:
            data = hotel_data_service.get_user_trace(request.args["baseinfo_id"].encode("utf-8"), ring_str=request.args["ring_str"])
        else:
            data = hotel_data_service.get_user_trace(request.args["baseinfo_id"].encode("utf-8"))
        return json.dumps(data)
    except:
        traceback.print_exc()
        abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)