from firefly_widgets import *
from nx import *

import sys


try:
    app_state = json.loads(open(".app_state").read())
except:
    app_state = {}



def get_pix(name):
    return QPixmap(os.path.join("images","%s.png" % name))



class Firestarter(QApplication):
    def __init__(self):
        super(Firestarter, self).__init__(sys.argv)

        splash_pix = get_pix('splash')
        self.splash = QSplashScreen(splash_pix)
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
        print msg
        self.splash.showMessage(msg,alignment=Qt.AlignBottom|Qt.AlignLeft, color=Qt.white)

    def load_site_settings(self):
        self.splash_message("Loading site settings")
        ret_code, result = query("site_settings")
        if ret_code < 300:
            config.update(result)
        else:
            critical_error("Unable to load site settigs")

    def load_meta_types(self):
        self.splash_message("Loading metadata types")
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