from nx.common import *

import sys 
import json

connection_type = "client"

__all__ = ["connection_type", "query", "success"]

AUTH_KEY = "dev"



PYTHON_GEN = sys.version_info[0]


def success(retcode):
    return retcode < 300


if PYTHON_GEN == 3:

    from urllib.parse import urlencode
    from urllib.request import urlopen

    def query(method, params={}, target="hive"):
        params = json.dumps(params)
        url = "{protocol}://{host}:{port}/{target}".format(protocol = ["http", "https"][config.get("use_ssl", False)],
                                                           host     = config["hive_host"], 
                                                           port     = config["hive_port"], 
                                                           target   = target
                                                          )

        post_data = urlencode({ "method" : method,
                                "auth_key" : AUTH_KEY, 
                                "params" : params
                                })

        result = urlopen(url, post_data.encode("ascii"), timeout=10).read()
        result = json.loads(result.decode('ascii'))
        return 200, result


elif PYTHON_GEN == 2:

    import urllib
    import urllib2

    def query(method, params={}, target="hive"):
        params = json.dumps(params)
        url = "http://%s:%s/%s" % (config["hive_host"], config["hive_port"], target)
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

