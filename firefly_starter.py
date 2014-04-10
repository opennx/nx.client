import sys

from firefly_common import *
from firefly_listener import SeismicListener


class Firestarter(QApplication):
    def __init__(self, main_window):
        super(Firestarter, self).__init__(sys.argv)
        self.main_window = False
        self.splash = QSplashScreen(pixlib['splash'])
        self.splash.show()
        self.listener = SeismicListener()


        self.tasks = [
                      self.load_site_settings,
                      self.load_meta_types,
                      self.load_storages,
                      self.init_listener
                     ]

        for task in self.tasks:
            task()

        self.splash_message("Loading user workspace...")
        self.main_window = main_window(self)
        


    def handle_messaging(self, data):
        if not self.main_window:
            return
        self.main_window.handle_messaging(data)


    def splash_message(self, msg):
        self.splash.showMessage(msg,alignment=Qt.AlignBottom|Qt.AlignLeft, color=Qt.white)


    def load_site_settings(self):
        self.splash_message("Loading site settings")
        ret_code, result = query("site_settings")
        if ret_code < 300:
            config.update(result)
            # folder ids back to integers. fuck json
            nfolders = {}
            for id_folder in config["folders"]:
                nfolders[int(id_folder)] = config["folders"][id_folder]
            config["folders"] = nfolders

        else:
            critical_error("Unable to load site settings")

    def load_meta_types(self):
        self.splash_message("Loading metadata types")
        if not meta_types.load():
            critical_error("Unable to load meta types")            

    def load_storages(self):
        pass

    def init_listener(self):
        self.splash_message("Initializing seismic listener")
        self.listener.listen(config["site_name"], config["seismic_addr"], int(config["seismic_port"]))
        self.listener.add_handler(self.handle_messaging)


    def start(self):
        self.splash.hide()
        self.exec_()
        self.on_exit()


    def on_exit(self):
        self.listener.halt()
        i = 0
        while not self.listener.halted and i < 30:
            time.sleep(.1)