#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'LiuYang,geosmart'
import math

class CollectionUtil(object):

    #arr是被分割的list，n是每个chunk中含n元素。
    def chunksBySize(self,arr, n):
        return [arr[i:i+n] for i in range(0, len(arr), n)]

    #或者让一共有m块，自动分（尽可能平均）
    #split the arr into N chunks
    def chunksByAverage(self,arr, m):
        n = int(math.ceil(len(arr) / float(m)))
        return [arr[i:i + n] for i in range(0, len(arr), n)]