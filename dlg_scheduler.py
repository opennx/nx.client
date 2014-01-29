import time
import datetime

from firefly_common import *
from firefly_view import *


def scheduler_toolbar(parent):
    toolbar = parent.addToolBar("Actions")
    toolbar.setMovable(False)
    toolbar.setFloatable(False)
  
    action_add_event = QAction(QIcon(pixlib["add"]), 'Add event', parent)
    action_add_event.setShortcut('+')
    action_add_event.triggered.connect(parent.on_add_event)        
    toolbar.addAction(action_add_event)
  
    action_remove_event = QAction(QIcon(pixlib["remove"]), 'Remove selected event', parent)
    action_remove_event.setShortcut('-')
    action_remove_event.triggered.connect(parent.on_remove_event)        
    self.toolbar.addAction(action_remove_event)
    
    toolbar.addSeparator()
  
    action_accept = QAction(QIcon(pixlib["accept"]), 'Accept changes', parent)
    action_accept.setShortcut('ESC')
    action_accept.triggered.connect(parent.on_accept)        
    toolbar.addAction(action_accept)
  
    action_cancel = QAction(QIcon(pixlib["cancel"]), 'Cancel', parent)
    action_cancel.setShortcut('Alt+F4')
    action_cancel.triggered.connect(parent.on_cancel)        
    toolbar.addAction(action_cancel)
  

class wndScheduler(QMainWindow):
    def __init__(self,  firefly, wident):
        super(wndScheduler, self).__init__()
        self.firefly = firefly
        self.wident = wident
      
        self.on_save = False
      
        self.blocks_view = BlocksView(self)
        self.setCentralWidget(self.blocks_view)
        self.setStyleSheet(base_css)
        self.resize(1060,600)
   
   

    def on_add_event(self):
        pass

    def on_remove_event(self):
        pass
   
    def on_accept(self):
        self.blocks_view.Save()
        if self.on_save:
            self.on_save()
   
    def on_cancel(self):
        self.close()
    
