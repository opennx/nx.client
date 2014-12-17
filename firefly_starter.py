import sys

from firefly_common import *
from firefly_listener import SeismicListener
from firefly_filesystem import load_filesystem
from dlg_sites import SiteSelect

from version_info import PROTOCOL

class Login(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle("Please log in")
        self.setStyleSheet(base_css)
        self.login = QLineEdit(self)
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.btn_login = QPushButton('Login', self)
        self.btn_login.clicked.connect(self.handleLogin)

        layout = QFormLayout(self)
        layout.addRow("Login", self.login)
        layout.addRow("Password", self.password)
        layout.addRow("", self.btn_login)

        self.result = False

    def handleLogin(self):
        stat, res = query("auth", login=self.login.text(), password=self.password.text(), host=socket.gethostname(), protocol=PROTOCOL)
        if success(stat):
            self.result = True
            self.close()
        else:
            QMessageBox.critical(self, "Error", res)


def check_login():
    stat, res = query("auth", protocol=PROTOCOL)
    if success(stat):
        return True
    elif stat == 403:
        dlg = Login()
        dlg.exec_()
        return dlg.result
    else:
        QMessageBox.critical(None, "Error", res)
        return False
    return True


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

        if not check_login():
            sys.exit(0)

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
        stat, res = query("site_settings")
        config["rights"] = {}
        if success(stat):
            config.update(res)

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
            QMessageBox.critical(self.splash, "Error", res)
            critical_error("Unable to load site settings")


    def load_meta_types(self):
        self.splash_message("Loading metadata types")
        if not meta_types.load():
            critical_error("Unable to load meta types")

    def load_storages(self):
        self.splash_message("Loading storages")
        f = lambda m: self.splash_message("Loading storages (testing mount point {})".format(m))
        load_filesystem(handler=f)

    def init_listener(self):
        self.splash_message("Initializing seismic listener")
        self.listener.listen(config["site_name"], config["seismic_addr"], int(config["seismic_port"]))

    def start(self):
        self.splash.hide()
        self.exec_()
        self.on_exit()

    def on_exit(self):
        self.listener.halt()
        i = 0
        while not self.listener.halted and i < 30:
            time.sleep(.1)
