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

def query(method, target="hive", **kwargs):
    if config.get("hive_zlib",False):
        kwargs["hive_zlib"] = True

    url = "{protocol}://{host}:{port}/{target}".format(
            protocol = ["http", "https"][config.get("hive_ssl", False)],
            host     = config["hive_host"], 
            port     = config["hive_port"], 
            target   = target
        )

    post_data = urlencode({ 
        "method" : method,
        "auth_key" : AUTH_KEY, 
        "params" : json.dumps(kwargs)
        })

    #try:
    result = urlopen(url, post_data.encode("ascii"), timeout=10).read()
    #except:
    #    return 400, "TODO: Return specific error message"

    if kwargs.get("hive_zlib",False):
        result = zlib.decompress(result)
    result = json.loads(result.decode('ascii'))
    return 200, result
