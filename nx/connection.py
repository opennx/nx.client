from nx.common import *

import json

connection_type = "client"

__all__ = ["connection_type", "query", "success"]

AUTH_KEY = "dev"

import sys 

PYTHON_GEN = sys.version_info[0]


def success(retcode):
    return retcode < 300


if PYTHON_GEN == 3:

    from urllib.parse import urlencode
    from urllib.request import urlopen

    def query(method, params={}):
        params = json.dumps(params)
        url = "http://%s:%s" % (config["hive_host"], config["hive_port"])
        post_data = urlencode({ "method" : method,
                                "auth_key" : AUTH_KEY, 
                                "params" : params
                                })
        result = urlopen(url, post_data.encode("ascii"), timeout=10).read().decode('ascii')
        result = json.loads(result)
        return 200, result


elif PYTHON_GEN == 2:

    import urllib
    import urllib2

    def query(method, params={}):
        params = json.dumps(params)
        url = "http://%s:%s" % (config["hive_host"], config["hive_port"])
        post_data = urllib.urlencode({ "method" : method,
                                       "auth_key" : AUTH_KEY, 
                                       "params" : params
                                       })
        
        result = urllib2.urlopen(url, post_data, timeout=10).read()
        try:
            result = json.loads(result)
        except:
            return 500, None
        return 200, result


else:
    critical_error("Unsupported python version")

