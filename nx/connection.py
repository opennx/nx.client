import json
import hashlib
import socket
import getpass
import requests

from .core import *

__all__ = ["connection_type", "query", "success"]

connection_type = "client"

AUTH_KEY = hashlib.sha256("{}:{}".format(
    socket.gethostname(),
    getpass.getuser()).encode("ascii")
    ).hexdigest()




def success(retcode):
    return retcode < 300


def readlines(f):
    buff = b""
    for ch in f.iter_content(1):
        ch = ch
        if ch == b"\n":
            yield buff.decode("ascii")
            buff = b""
        else:
            buff+=ch
    yield buff.decode("ascii")


def query(method, target="hive", handler=False, **kwargs):
    start_time = time.time()

    url = "{protocol}://{host}:{port}/{target}".format(
            protocol = ["http", "https"][config.get("hive_ssl", False)],
            host     = config.get("hive_host", None),
            port     = config.get("hive_port", 80),
            target   = target
            )

    params = {
            "method"   : method,
            "auth_key" : AUTH_KEY,
            "params"   : json.dumps(kwargs)
            }

    #TODO: Error handling here
    request = requests.post(url, data=params, stream=True)
    for line in readlines(request):
        print (line)
        response, result = json.loads(line)
        if response == -1:
            if handler:
                handler(result)
        else:
            break

    if success(response):
        logging.info("Query {} completed in {:0.2f} seconds".format(method, time.time() - start_time))
    else:
        logging.error("Query {} to {} failed: ({}) {}".format(url, method, response, result))
    return response, result
