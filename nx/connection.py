from nx.common import *

import json
import zlib

from urllib.parse import urlencode
from urllib.request import urlopen

__all__ = ["connection_type", "query", "success"]

connection_type = "client"

AUTH_KEY = "dev"

def success(retcode):
    return retcode < 300

def query(method, params={}, target="hive"):
    if config.get("use_zlib",False):
      params["use_zlib"] = True
    params = json.dumps(params)
    url = "{protocol}://{host}:{port}/{target}".format(protocol = ["http", "https"][config.get("hive_ssl", False)],
                                                       host     = config["hive_host"], 
                                                       port     = config["hive_port"], 
                                                       target   = target
                                                      )

    post_data = urlencode({ "method" : method,
                            "auth_key" : AUTH_KEY, 
                            "params" : params
                            })

    result = urlopen(url, post_data.encode("ascii"), timeout=10).read()
    if config.get("use_zlib",False):
      result = zlib.decompress(result)
    result = json.loads(result.decode('ascii'))

    return 200, result
