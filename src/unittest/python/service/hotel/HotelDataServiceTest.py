# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import unittest
import json

from service.hotel.HotelDataService import HotelDataService


class HotelDataServiceTest(unittest.TestCase):

    hotel_data_service = HotelDataService()

    def setUp(self):
        print 'setUp...'

    def test_get_comm_by_text(self):
        print json.dumps(self.hotel_data_service.get_user_trace("a147089e-0a4f-11e6-a508-84fe22347625"))

    def test_get_comm_viewpoints(self):
        print json.dumps(self.hotel_data_service.get_comm_viewpoints("a147089e-0a4f-11e6-a508-84fe22347625","6671c6a1-0a51-11e6-8871-84fe22347625"))

    def test_get_comm_type_score_statics(self):
        print json.dumps(self.hotel_data_service.get_comm_type_score_statics("979f6a41-0a4f-11e6-95f8-84fe22347625","携程"))

    def test_get_baseinfo_by_location_id(self):
        print json.dumps(self.hotel_data_service.get_baseinfo_by_location_id("00bbea11-0a52-11e6-8ea7-84fe22347625"))

    def test_get_comm_adjective_statics(self):
        print json.dumps(self.hotel_data_service.get_comm_adjective_statics("979f6a41-0a4f-11e6-95f8-84fe22347625"))

    def test_get_user_trace(self):
        rings = "[[118.7195888671875,32.049486328125],[118.73469506835937,32.09411828613281],[118.74842797851562,32.114031005859374],[118.81915246582031,32.092058349609374],[118.91253625488281,32.05978601074219],[118.91322290039062,32.027513671875],[118.83357202148437,32.01034753417969],[118.7635341796875,32.00348107910156],[118.7195888671875,32.049486328125]]"
        result_data = self.hotel_data_service.get_user_trace("a147089e-0a4f-11e6-a508-84fe22347625",ring_str=rings)
        print len(result_data["line"])
        print json.dumps(result_data)

    def tearDown(self):
        print 'tearDown...'