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

def query(method, target="hive", handler=False, **kwargs):
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

    with urlopen(url, post_data.encode("ascii"), timeout=5) as feed:
        while True:
            line = feed.readline()
            if not line:
                break

            if kwargs.get("hive_zlib",False):
                result = zlib.decompress(result)

            response, result = json.loads(line.decode('ascii'))
            if response == -1:
                if handler:
                    handler(result)
            else:
                break



    return response, result
