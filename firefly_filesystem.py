import os
import time
import subprocess

from firefly_common import *

def load_filesystem(handler=False):
    if PLATFORM == "windows":
        for letter in "abcdefghijklmnopqrstuvwxyz":
            if handler:
                handler(letter)
            base_path = "{}:\\".format(letter)
            if not os.path.exists(base_path):
                continue

            storage_ident = os.path.join(base_path, ".nebula_root")
            if not os.path.exists(storage_ident):
                continue

            for line in open(storage_ident).read().split("\n"):
                try:
                    site, id_storage = line.split(":")
                    id_storage = int(id_storage)
                except:
                    continue
                
                if site != config["site_name"]:
                    continue
                
                storage = Storage()
                storage.id_storage = id_storage
                storage.local_path = base_path
                
                storages[id_storage] = storage
