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

DEFAULT_PORT = 443
DEFAULT_SSL = True


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

    host = config.get("hive_host", None)
    port = config.get("hive_port", DEFAULT_PORT)
    ssl = config.get("hive_ssl", DEFAULT_SSL)

    url = "{protocol}://{host}:{port}/{target}".format(
            protocol=["http", "https"][ssl],
            host=host,
            port=port,
            target=target
            )

    params = {
            "method"   : method,
            "auth_key" : AUTH_KEY,
            "params"   : json.dumps(kwargs)
            }

    try:
        request = requests.post(
                url,
                data=params,
                stream=True,
            )
    except:
        request = None
        log_traceback("Query failed")

    if not request:
        return (500, "Unable to create connection to {}".format(url))

    response = None
    
    for line in readlines(request):
        if config.get("debug", False):
            print (line)
        try:
            response, result = json.loads(line)
        except:
            print (line)
            continue
        if response == -1:
            if handler:
                handler(result)
        else:
            break

    if not response:
        response, result = 500, "No response"

    if success(response):
        logging.info("Query {} completed in {:0.2f} seconds".format(method, time.time() - start_time))
    else:
        logging.error("Query {} to {} failed: ({}) {}".format(url, method, response, result))
    return response, result
