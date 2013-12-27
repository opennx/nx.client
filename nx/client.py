from common import *
from assets import *


import urllib, urllib2, json

AUTH_KEY = "dev"


def query(method, params={}):
    params = json.dumps(params)
    url = "http://%s:%s" % (config["hive_host"], config["hive_port"])
    post_data = urllib.urlencode({ "method" : method,
                                   "auth_key" : AUTH_KEY, 
                                   "params" : params
                                   })
    
    result = urllib2.urlopen(url, post_data, timeout=3).read()
    #try:
    #    result = urllib2.urlopen(url, post_data, timeout=3).read()
    #except urllib2.URLError as e:
    #    return 500, None

    #try:
    result = json.loads(result)
    #except:
    #    return 500, None

    return 200, result


## Queries
#######################################################################################################
## Site settings

def load_site_settings():
    return
    ret_code, result = query("site_settings")
    if ret_code < 300:
        config.update(result)
    else:
        critical_error("Unable to load site settigs")


def load_meta_types():
    ret_code, result = query("meta_types")
    if ret_code < 300:  
        for t in result:
            m = MetaType(t["title"])
            m.namespace   = t["namespace"]
            m.editable    = t["editable"]
            m.searchable  = t["searchable"]
            m.class_      = t["class"]
            m.default     = t["default"]
            m.settings    = t["settings"]
            m.aliases     = t["aliases"]
            meta_types[t["title"]] = m
    else:
        critical_error("Unable to load meta types")

## Site settings
########################################################################
## Storages

class Storage():
    def __init__(self): 
        pass

    def get_path(self,rel=False):
        if self.protocol == LOCAL:
            return self.path

def load_storages():
    pass





class Firestarter():
    def __init__(self):
        self.tasks = [
                        (load_site_settings,"Loading site settings"),
                        (load_meta_types,"Loading meta types"),
                        (messaging.init,"Initialising Seismic messaging"),
                        (load_storages,"Loading storages")
                     ]

    def start(self, messageHandler=None):
        for task, msg in self.tasks:
            print msg
            task()


