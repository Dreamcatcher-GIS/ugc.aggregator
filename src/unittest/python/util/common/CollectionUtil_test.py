# -*- coding:utf-8 -*-
import unittest

from util.common.CollectionUtil import CollectionUtil

class CollectionUtilTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print "setUpClass..."

    @classmethod
    def tearDownClass(cls):
        print "tearDownClass..."

    def test_chunksBySize(self):
        array=range(10)
        chunks=CollectionUtil().chunksBySize(array,5)
        self.assertEqual(chunks,[[0, 1, 2, 3, 4], [5, 6, 7, 8,9]])

if __name__=="__main__":
    unittest.main()