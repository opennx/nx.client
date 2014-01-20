#!/usr/bin/env python
# -*- coding: utf-8 -*-

from firefly_common import *
from firefly_menu import create_menu



class Firefly(QMainWindow):
    def __init__(self, parent):
        super(Firefly, self).__init__()

        self.setWindowTitle("Firefly NX")

        create_menu(self)

        self.setStyleSheet(base_css)
        self.setWindowState(Qt.WindowMaximized)
        self.status("Ready")
        self.show()



    def status(self, msg):
        self.statusBar().showMessage(msg)

    def on_new_browser(self):
        pass

    def on_logout(self):
        pass

    def on_exit(self):
        pass




if __name__ == "__main__":
    app = Firestarter()
    wnd = Firefly(app)
    app.start()