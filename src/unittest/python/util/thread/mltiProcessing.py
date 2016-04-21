from multiprocessing import Process, Pool
import time
import urllib2

def millis():
  return int(round(time.time() * 1000))

def http_get(url):
  start_time = millis()
  result = {"url": url, "data": urllib2.urlopen(url, timeout=5).read()[:100]}
  print url + " took " + str(millis() - start_time) + " ms"
  return result

if __name__ == '__main__':

    urls = ['http://api.map.baidu.com/lbsapi/getpoint/','https://github.com/','https://github.com/neo1218/pythonCookbook/tree/89a05a2a4d723fb49548e0e87d2542bd5d07fbee',"http://map.baidu.com/","http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000"]

    pool = Pool(processes=5)

    start_time = millis()
    results = pool.map(http_get, urls)

    print "\nTotal took " + str(millis() - start_time) + " ms\n"

    for result in results:
      print result