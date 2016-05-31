#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .core import *
from .connection import *

from .core.base_objects import BaseAsset, BaseItem, BaseBin, BaseEvent

from .cellformat import NXCellFormat
from .colors import *

__all__ = ["Asset", "Item", "Bin", "Event", "Dummy"]


class Asset(BaseAsset, NXCellFormat):
    def format_sort(self, key):
        if not key in self.meta:
            return ""
        if not key in meta_types:
            return self[key]
        if key == "content_type":
            return self[key]
        mtype = meta_types[key]
        value = self[key]

        return value

        if mtype.class_   in [INTEGER, NUMERIC, DATE, TIME, DATETIME, DURATION, STATUS, STATE, FILESIZE, PART, BOOLEAN, STAR]: return value #FIXME
        elif mtype.class_ in [TEXT, BLOB]: return value
        elif mtype.class_ in [SELECT, ISELECT, LIST, COMBO, FOLDER]: return unaccent(self.format_display(key))

        return ""


class Dummy(NXCellFormat):
    object_type = "dummy"
    id = False
    def __init__(self, title=""):
        self.meta = {"title":title}
    def __getitem__(self, key):
        return self.meta.get(key,"")
    def __setitem__(self, key, value):
        self.meta[key] = value


class EmptyAsset():
    def __init__(self):
        self.meta = {}
    def __getitem__(self, key):
        return ""


class Item(BaseItem, NXCellFormat):
    @property
    def asset(self):
        return self._asset


class Bin(BaseBin, NXCellFormat):
    pass

class Event(BaseEvent, NXCellFormat):
    pass
