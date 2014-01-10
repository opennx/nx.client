#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common import *
from connection import *

class MetaType(object):
    def __init__(self, title):
        self.title      = title
        self.namespace  = "site"
        self.editable   = False
        self.searchable = False
        self.class_     = TEXT
        self.default    = False
        self.settings   = False
        self.aliases    = {}

    def alias(self, lang='en-US'):
        return self.aliases.get(lang, self.title)

    def pack(self):
        return {
                "title"      : self.title,
                "namespace"  : self.namespace,
                "editable"   : self.editable,
                "searchable" : self.searchable,
                "class"      : self.class_,
                "default"    : self.default,
                "settings"   : self.settings,
                "aliases"    : self.aliases
                }


class MetaTypes(dict):
    def __init__(self):
        super(MetaTypes, self).__init__()
        self.nstagdict = {}

    def __getitem__(self, key):
        return self.get(key, self._default())

    def load(self):
        if connection_type == "server":
            db = DB()
            db.query("SELECT namespace, tag, editable, searchable, class, default_value,  settings FROM nx_meta_types")
            for ns, tag, editable, searchable, class_, default, settings in db.fetchall():
                meta_type = MetaType(tag)
                meta_type.namespace  = ns
                meta_type.editable   = bool(editable)
                meta_type.searchable = bool(searchable)
                meta_type.class_     = class_
                meta_type.default    = default
                meta_type.settings   = settings
                db.query("SELECT lang, alias FROM nx_meta_aliases WHERE tag='%s'" % tag)
                for lang, alias in db.fetchall():
                    meta_type.aliases[lang] = alias
                self[tag] = meta_type
            return True

        elif connection_type == "client":
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
                    self[t["title"]] = m
                return True
            else:
                return False
        return False

    def _default(self):
        meta_type = MetaType("Unknown")
        meta_type.namespace  = "site"
        meta_type.editable   = 0
        meta_type.searchable = 0
        meta_type.class_     = TEXT
        meta_type.default    = ""
        meta_type.settings   = False
        return meta_type

    def ns_tags(self, ns):
        if not ns in self.nstagdict:
            result = []
            for tag in self:
                if self[tag].namespace in ["o", ns]:
                    result.append(self[tag].title)
            self.nstagdict[ns] = result
        return self.nstagdict[ns]

    def format_default(self, key):
        if not key in self:
            return False
        else:
            return self.format(key, self[key].default)

    def col_alias(self, key, lang):
        if key in self: 
            return self[key].aliases.get(lang,key)
        return key

    def format(self, key, value):
        if not key in self:
            return value
        mtype = self[key]

        if  key == "path":                return value.replace("\\","/")

        elif mtype.class_ == TEXT:        return value.strip()
        elif mtype.class_ == INTEGER:     return int(value)
        elif mtype.class_ == NUMERIC:     return float(value)
        elif mtype.class_ == BLOB:        return value.strip()
        elif mtype.class_ == DATE:        return float(value)
        elif mtype.class_ == TIME:        return float(value)
        elif mtype.class_ == DATETIME:    return float(value)
        elif mtype.class_ == TIMECODE:    return float(value)
        elif mtype.class_ == DURATION:    return float(value)
        elif mtype.class_ == REGION:      return json.loads(value)
        elif mtype.class_ == REGIONS:     return json.loads(value)
        elif mtype.class_ == SELECT:      return value.strip()
        elif mtype.class_ == ISELECT:     return int(value)
        elif mtype.class_ == LIST:        return value.strip()
        elif mtype.class_ == COMBO:       return value.strip()
        elif mtype.class_ == FOLDER:      return int(value)
        elif mtype.class_ == STATUS:      return int(value)
        elif mtype.class_ == STATE:       return int(value)
        elif mtype.class_ == FILESIZE:    return int(value)
        elif mtype.class_ == MULTISELECT: return json.loads(value)
        elif mtype.class_ == PART:        return json.loads(value)
        elif mtype.class_ == BOOLEAN:     return int(value)
        elif mtype.class_ == STAR:        return int(value)

meta_types = MetaTypes()

if connection_type == "server":
    meta_types.load()
