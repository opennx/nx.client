#!/usr/bin/env python
# -*- coding: utf-8 -*-

from firefly_view import *
from nx.assets import *


class BrowserModel(NXViewModel):
    def browse(self, **kwargs):
        start_time = time.time()
        self.beginResetModel()
        result, data = query("browse",kwargs)
        self.object_data = []
        if result >= 300:
            print "error message"
        else:
            if "asset_data" in data:
                for adata in data["asset_data"]:
                    self.object_data.append(Asset(from_data=adata))
                self.header_data = ["content_type", "title", "role/performer", "duration", "file/size"]

        self.endResetModel()
        self.parent.showMessage("Got %d assets in %.03f seconds." % (len(self.object_data), time.time()-start_time))


    def flags(self,index):
        flags = super(BrowserModel, self).flags(index)
        if index.isValid():
            if self.object_data[index.row()]["id_object"]:
             #if self.parent.parent.edit_mode: 
             flags |= Qt.ItemIsEditable
             flags |= Qt.ItemIsDragEnabled # Itemy se daji dragovat
        return flags



class SearchBox(QWidget):
    def __init__(self,parent):
        super(SearchBox, self).__init__()
        self.parent = parent

        self.line_edit =  QLineEdit()
        self.line_edit.setPlaceholderText ("type something...")
        self.line_edit.keyPressEvent = self.line_keyPressEvent

        layout = QHBoxLayout()
        layout.setContentsMargins(0,4,0,0)
        layout.setSpacing(2)

        layout.addWidget(self.line_edit,1)
        self.setLayout(layout)

    def line_keyPressEvent(self, event):
        if event.key() in [Qt.Key_Return,Qt.Key_Enter]:
            if event.modifiers() & Qt.ControlModifier:
                print "extend search"
                #self.parent.OnSearch(extend=True)
            else:
                self.parent.search_query["fulltext"] = self.line_edit.text()
                self.parent.browse()
            return True
        elif event.key() == Qt.Key_Escape:
            self.line_edit.setText("")
        elif event.key() == Qt.Key_Down:
            self.parent.view.setFocus()
        return QLineEdit.keyPressEvent(self.line_edit, event)



class BrowserWidget(QWidget):
    def __init__(self, parent):
        super(BrowserWidget, self).__init__(parent)
        self.parent = parent
        self.statusbar = False
        
        self.search_query = {}
        self.search_box = SearchBox(self)

        self.view = NXView(self)
        self.view.setSortingEnabled(True)
        self.view.setItemDelegate(MetaEditItemDelegate(self.view))
        self.view.activated.connect(self.on_activate)

        self.editor_closed_at = time.time()

        self.model      = BrowserModel(self) 
        self.sortModel  = NXSortModel(self.model)
        self.view.setModel(self.sortModel)

        layout = QVBoxLayout()
        layout.setContentsMargins(5,0,5,5)
        layout.setSpacing(5)
        layout.addWidget(self.search_box, 0)
        layout.addWidget(self.view, 1)
        self.setLayout(layout)

        self.browse()
        
    def browse(self,**kwargs):
        if self.model.header_data:
            self.saveColumnWidths()
        self.search_query.update(kwargs)
        self.model.browse(**self.search_query)
        self.loadColumnWidths()
 
    def on_activate(self,mi):
        print "activated"
        #if not self.parent.edit_mode:
        #   row =  self.proxyModel.mapToSource(mi).row()
        #   id_asset = self.model.arraydata[row][0][0]
        #   self.parent.OpenDetail(id_asset)
        #   return False   
        #else:
        if time.time() - self.view.editor_closed_at > 0.2:
            self.view.edit(mi)
        #return True  



    def loadColumnWidths(self):
        for id_column in range(self.model.columnCount(False)):
            col_tag = self.model.header_data[id_column]
            w = app_state.get("col_widths",{}).get(col_tag,False)
            if w:
                self.view.setColumnWidth(id_column, w) 
            else:
                self.view.resizeColumnToContents(id_column)

    def saveColumnWidths(self):
        if not "col_widths" in app_state:
            app_state["col_widths"] = {}

        for id_column in range(self.model.columnCount(False)):
            app_state["col_widths"][self.model.header_data[id_column]] = self.view.columnWidth(id_column)
        
    def hideEvent(self, event):
        self.saveColumnWidths()


    def showMessage(self, message, message_type=INFO):
        print message # todo - show in status bar
        if self.statusbar and message_type > DEBUG:
            pass






class BrowserTabs(QTabWidget):
    def __init__(self, parent=None):
        super(BrowserTabs, self).__init__()  

        self.action_new_tab = QAction('New tab', self)  
        self.action_new_tab.setShortcut('Ctrl+T')
        self.action_new_tab.setStatusTip('New browser tab')
        self.action_new_tab.triggered.connect(self.new_tab)
        self.addAction(self.action_new_tab)

        self.action_close_tab = QAction('Close tab', self)  
        self.action_close_tab.setShortcut('Ctrl+W')
        self.action_close_tab.setStatusTip('Close current browser tab')
        self.action_close_tab.triggered.connect(self.close_tab)
        self.addAction(self.action_close_tab)

        self.action_next_tab = QAction('Next tab', self)  
        self.action_next_tab.setShortcut('Ctrl+TAB')
        self.action_next_tab.setStatusTip('Next tab')
        self.action_next_tab.triggered.connect(self.next_tab)
        self.addAction(self.action_next_tab)

        self.action_prev_tab = QAction('Previous tab', self)  
        self.action_prev_tab.setShortcut('Ctrl+Shift+TAB')
        self.action_prev_tab.setStatusTip('Previous tab')
        self.action_prev_tab.triggered.connect(self.prev_tab)
        self.addAction(self.action_prev_tab)

        self.new_tab()

    def new_tab(self, evt=None):
        idx = self.addTab(BrowserWidget(self), "Browser")
        self.setTabText(idx, "Browse %d" % idx )
        self.setCurrentIndex(idx)

    def close_tab(self, evt=None):
        self.removeTab(self.currentIndex())

    def next_tab(self, evt=None):
        cnt = self.count()
        idx = self.currentIndex()
        if idx == cnt-1: idx = -1
        self.setCurrentIndex(idx+1)

    def prev_tab(self, evt=None):
        cnt = self.count()
        idx = self.currentIndex()
        if idx == 0: idx = cnt
        self.setCurrentIndex(idx-1)

class BrowserDock(QDockWidget):
    """ Dockable variant for rundown window """
    def __init__(self, parent=None, draggable=False):
        super(BrowserDock, self).__init__()
        self.parent = parent
        self.setWindowTitle("Asset browser")
        self.tabs = BrowserTabs ()
        self.setWidget(self.tabs)
        if not draggable:
            self.setTitleBarWidget(QWidget())  



if __name__ == "__main__":
    app = Firestarter()

    wnd = QMainWindow()
    wnd.setStyleSheet(base_css)
    brw = BrowserTabs(wnd)
    wnd.setCentralWidget(brw)    
    wnd.show()
    wnd.resize(690,450)


    app.start()