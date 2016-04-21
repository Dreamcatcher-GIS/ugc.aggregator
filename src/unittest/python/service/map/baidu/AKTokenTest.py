# -*- coding:utf-8 -*-

__author__ = 'geosmart'

from util.http.UniversalSDK import APIClient


# "dRtL7RRo4YTdtujclWx85DtG","G4UkrVktXE71zQsGY8Vza3Ih",
class AKTokenTest(object):
    def TokenTest(self):
        akList =   ["lWpbR5OCQYybppqci2kGYgFd", "WBw4kIepZzGp4kH5Gn3r0ACy", "ou5X9BBEMZtwvuSO4Ypfx2HB",
              "Qdgt7mclCrkFdPBizd3uUWsE","lWhyznAxPPYdanHLKZpjR272","e5UujacxFn50xo2RadnTEtly",
              "WEC1LKpjIWfCehFqGVPm6Dn6", "DW2CwL3B3271CiVyw7GdBsfR", "LPtK0OiWUItxFK6qd3m1FsRD",
              "oD8Okbi8FdRm5keKBvfHuR7H","K1bHzgxG2osaIiKyAAel57jQ",
              "MviPFAcx5I6f1FkRQlq6iTxc", "MviPFAcx5I6f1FkRQlq6iTxc","MviPFAcx5I6f1FkRQlq6iTxc"
             ]
        baiduClient = APIClient("http://api.map.baidu.com")
        for aktoken in akList:
            data = baiduClient.geocoder.v2.addtrail("/").get(ak=aktoken, output="json",
                                                             location='32.2785671,118.324748')
            print aktoken, "...", data


if __name__ == "__main__":
    tokenTest = AKTokenTest()
    tokenTest.TokenTest()
