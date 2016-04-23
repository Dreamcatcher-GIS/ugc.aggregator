# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

from flask import Flask
from flask import abort
from flask import request
from flask.ext.cors import CORS
import json
import traceback

from service.weibo.WeiboService import WeiboService
from service.hotel.TuniuDataService import TuniuDataService
from service.hotel.xiecheng.DriveServices import XiechengDriverService
from service.hotel.xiecheng.XichengDataService import XichengDataService


app = Flask(__name__)
CORS(app)

weibo_service = WeiboService()
xiechengDriverService = XiechengDriverService()
tuniu_data_service = TuniuDataService()
xiecheng_data_service = XichengDataService()

@app.route('/hello', methods=['GET'])
def hello_world():
    if "name" in request.args:
        return "Hello" + request.args["name"]
    else:
        return 'Hello World!'

@app.route('/ugc.hotel/rest/v100/weibo/get/nearby_timeline', methods=['GET'])
def weibo_nearbytimeline():
    try:
        return json.dumps(weibo_service.get_all_weibo_nearby(request.args["lat"], request.args["lng"], request.args["starttime"], request.args["endtime"],request.args["range"]))
    except:
        abort(404)

@app.route('/ugc.hotel/rest/v100/weibo/get/nearby_timeline/statics', methods=['GET'])
def weibo_nearbytimeline_wrapper():
    try:
        data = weibo_service.get_all_weibo_nearby(request.args["lat"], request.args["lng"], request.args["starttime"], request.args["endtime"],request.args["range"])
        return json.dumps(weibo_service.nearby_weibo_statis_wrapper(data))
    except:
        abort(404)

@app.route('/ugc.hotel/rest/v100/hotel/get/CommTypeNum', methods=['GET'])
def get_comm_type_num():
    try:
        return json.dumps(tuniu_data_service.get_comm_type_num(request.args["hotel_name"]))
    except:
        abort(404)

@app.route('/ugc.hotel/rest/v100/hotel/get/viewpoint', methods=['GET'])
def get_viewpoint():
    try:
        if "hotel_name" in request.args:
            return json.dumps(tuniu_data_service.get_comm_viewpoints(request.args["hotel_name"]))
    except:
        abort(404)

@app.route('/ugc.hotel/rest/v100/hotel/get/adjective', methods=['GET'])
def get_adjective_statics():
    try:
        return json.dumps(tuniu_data_service.get_comm_adjective_statics(request.args["hotel_name"]))
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

if __name__ == '__main__':
    app.run(host='192.168.1.124',port=5000)