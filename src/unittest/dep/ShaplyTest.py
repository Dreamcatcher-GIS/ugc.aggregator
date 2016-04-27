# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import unittest
from shapely.geometry import Polygon
from shapely.geometry import Point
import json


class ShapelyTest(unittest.TestCase):


    def setUp(self):
        print "setUp"

    def test_generate_polygon(self):
        ring_str = "[[118.72714196777343,32.01652734375],[118.72782861328125,32.05978601074219],[118.76971398925781,32.0659658203125],[118.86035119628906,32.00210778808594],[118.81228601074218,31.993868041992187],[118.72714196777343,32.01652734375]]"
        ring = json.loads(ring_str)
        pg = Polygon(ring)
        p = Point(118.69418298339843,32.10510461425781)
        print pg.intersects(p)

    def tearDown(self):
        print "tearDown"