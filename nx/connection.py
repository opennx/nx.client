import json
import zlib

from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

from nx.common import *

__all__ = ["connection_type", "query", "success"]

connection_type = "client"

AUTH_KEY = "dev"

def success(retcode):
    return retcode < 300

def query(method, target="hive", handler=False, **kwargs):
    start_time = time.time()
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

    response = False

    try:
        with urlopen(url, post_data.encode("ascii"), timeout=config.get("hive_timeout", 3)) as feed:
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

    except URLError as e:
        print ("Query failed")
        return 503, e.reason

    except HTTPError as e:
        print ("Query failed")
        return e.code, "HTTP Errror {}".format(e.code)

    except socket.timeout:
        return 400, "Operation timeout"

    if response:
        print ("Query {} completed in {:0.2f} seconds".format(method, time.time() - start_time))
        return response, result
    else:
        return 418, "I'm a teapot"