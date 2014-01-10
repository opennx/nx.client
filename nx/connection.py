from common import *
import urllib, urllib2, json

connection_type = "client"

__all__ = ["connection_type", "query"]

AUTH_KEY = "dev"

def query(method, params={}):
    params = json.dumps(params)
    url = "http://%s:%s" % (config["hive_host"], config["hive_port"])
    post_data = urllib.urlencode({ "method" : method,
                                   "auth_key" : AUTH_KEY, 
                                   "params" : params
                                   })
    
    result = urllib2.urlopen(url, post_data, timeout=10).read()
    #try:
    #    result = urllib2.urlopen(url, post_data, timeout=3).read()
    #except urllib2.URLError as e:
    #    return 500, None

    #try:
    result = json.loads(result)
    #except:
    #    return 500, None

    return 200, result




