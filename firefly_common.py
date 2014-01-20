#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nx.common import *
from nx.common.metadata import meta_types
from nx.connection import *

from firefly_widgets import *


try:
    app_state = json.loads(open(".app_state").read())
except:
    app_state = {}




def get_pix(name):
    return QPixmap(os.path.join("images","%s.png" % name))

class Pixlib(dict):
    def __getitem__(self, key):
        if not key in self:
            self[key] = get_pix(key)
        return self.get(key, None)

pixlib = Pixlib()






class Firestarter(QApplication):
    def __init__(self):
        super(Firestarter, self).__init__(sys.argv)

        self.splash = QSplashScreen(pixlib['splash'])
        self.splash.show()

        self.tasks = [
                      self.load_site_settings,
                      self.load_meta_types,
                      self.load_storages
                     ]

        for task in self.tasks:
            task()

        self.splash_message("Loading user workspace...")

    def splash_message(self, msg):
        self.splash.showMessage(msg,alignment=Qt.AlignBottom|Qt.AlignLeft, color=Qt.white)

    def load_site_settings(self):
        self.splash_message("Loading site settings")
        ret_code, result = query("site_settings")
        if ret_code < 300:
            config.update(result)
        else:
            critical_error("Unable to load site settings")

    def load_meta_types(self):
        self.splash_message("Loading metadata types")
        if not meta_types.load():
            critical_error("Unable to load meta types")            

    def load_storages(self):
        pass

    def save_app_state(self):
        f = open(".app_state","w")
        f.write(json.dumps(app_state))
        f.close()

    def start(self):
        self.splash.hide()
        self.exec_()
        self.save_app_state()