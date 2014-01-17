#!/usr/bin/env python
# -*- coding: utf-8 -*-

from firefly_common import *


if __name__ == "__main__":
    app = Firestarter()

    wnd = QMainWindow()
    wnd.setStyleSheet(base_css)
    brw = BrowserTabs(wnd)
    wnd.setCentralWidget(brw)    
    wnd.show()
    wnd.resize(690,450)


    app.start()