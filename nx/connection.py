import sys
import json
import zlib

from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

from nx.common import *

import hashlib
import socket
import getpass
import ssl

AUTH_KEY = hashlib.sha256("{}:{}".format(
    socket.gethostname(),
    getpass.getuser()).encode("ascii")
    ).hexdigest()

__all__ = ["connection_type", "query", "success"]

connection_type = "client"

# 3.4.3 workaround
try:
    context = ssl._create_unverified_context()
except:
    context = None


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
        "method"   : method,
        "auth_key" : AUTH_KEY,
        "params"   : json.dumps(kwargs)
        })

    response = False
    result   = False

    try:

        urlargs = {"timeout" : config.get("hive_timeout", 3)}
        if context:
            urlargs["context"] = context

        with urlopen(url, post_data.encode("ascii"), **urlargs) as feed:
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
        response = 503
        result   = str(e.reason)
    except HTTPError as e:
        response = e.code
        result   = "HTTP Errror {}".format(e.code)
    except socket.timeout:
        response = 400
        result   = "Operation timeout"
    except:
        response = 400
        result   = "Unknown error: {}".format(str(sys.exc_info()))

    if success(response):
        print ("Query {} completed in {:0.2f} seconds".format(method, time.time() - start_time))
    else:
        try:
            print ("Query {} failed: ({}) {}".format(method, response, result))
        except:
            print ("Query {} failed".format(method))
    return response, result
