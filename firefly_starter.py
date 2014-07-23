import sys

from firefly_common import *
from firefly_listener import SeismicListener
from dlg_sites import SiteSelect

class Firestarter(QApplication):
    def __init__(self, main_window):
        super(Firestarter, self).__init__(sys.argv)
        self.main_window = False
        self.splash = QSplashScreen(pixlib['splash'])
        self.splash.show()
        self.got_seismic = False
        self.listener = SeismicListener()

        try:
            local_settings = json.loads(open("local_settings.json").read())
        except:
            critical_error("Unable to open site_settings file.")
        
        i = 0
        if len(local_settings) > 1:
            dlg = SiteSelect(None, local_settings)
            i = dlg.exec_()
        
        config.update(local_settings[i])

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
        self.got_seismic = True
        self.main_window.handle_messaging(data)



    def splash_message(self, msg):
        self.splash.showMessage(msg,alignment=Qt.AlignBottom|Qt.AlignLeft, color=Qt.white)


    def load_site_settings(self):
        self.splash_message("Loading site settings")
        ret_code, result = query("site_settings")
        if ret_code < 300:
            config.update(result)
            
            if "JSON IS RETARDED AND CAN'T HANDLE INTEGER BASED KEYS IN DICTS":
                nfolders = {}
                for id_folder in config["folders"]:
                    nfolders[int(id_folder)] = config["folders"][id_folder]
                config["folders"] = nfolders

                nviews = {}
                i = 0
                for id_view, title, columns in config["views"]:
                        nviews[id_view] = i, title, columns
                        i += 1
                config["views"] = nviews

                nch = {}
                for id_channel in config["playout_channels"]:
                    nch[int(id_channel)] = config["playout_channels"][id_channel]
                config["playout_channels"] = nch

                nch = {}
                for id_channel in config["ingest_channels"]:
                    nch[int(id_channel)] = config["ingest_channels"][id_channel]
                config["ingest_channels"] = nch

        else:
            QMessageBox.critical(self.splash, "Critical error", "Unable to contact NX server.")
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