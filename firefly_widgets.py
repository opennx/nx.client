import time
from functools import partial

from qt_common import *
from nx.common import *
from nx.common.metadata import meta_types
from dlg_texteditor import TextEditor


# radio or select data . array of [value, label] or array of values

class NXE_select(QComboBox):
    def __init__(self, parent, data):
        super(NXE_select,self).__init__(parent)
        self.cdata = []
        self.set_data(data)
        self.default = False
      
    def set_data(self, data):
        for i, row in enumerate(sorted(data)):
            value, label = row
            if not label:
                label = value
            self.cdata.append(value)
            self.addItem(label)
        self.setCurrentIndex(-1)

    def set_value(self, value):
        if value == self.get_value():
            return
        self.default = value
        for i, val in enumerate(self.cdata):
            if val == value:
                self.setCurrentIndex(i)
                break

    def get_value(self):
        if self.currentIndex() == -1:
            return ""
        return self.cdata[self.currentIndex()]



class NXE_radio(QWidget):
    def __init__(self, parent, data):
        super(NXE_radio,self).__init__(parent)
        self.cdata = []
        self.default = False
        self.current_index = -1
        self.buttons = []
        self.set_data(data)

    def set_data(self, data):
        self.current_index = -1
        groupBox = QButtonGroup()
        vbox = QHBoxLayout()
        for i, row in enumerate(sorted(data)):
            value, label = row
            if not label:
                label = value
            self.cdata.append(value)

            self.buttons.append(QPushButton(label))
            self.buttons[-1].setCheckable(True)
            self.buttons[-1].setAutoExclusive(True)
            self.buttons[-1].clicked.connect(partial(self.switch, i))
            vbox.addWidget(self.buttons[-1])

        self.setLayout(vbox)

    def switch(self, index):
        self.current_index = index

    def set_value(self, value):
        if value == self.get_value():
            return
        self.default = value
        for i, val in enumerate(self.cdata):
            if val == value:
                self.buttons[i].setChecked(True)
                self.current_index = i
                break
        else:
            self.current_index = -1
            for button in self.buttons:
                button.setAutoExclusive(False);
                button.setChecked(False);
                button.setAutoExclusive(True);
                
    def get_value(self):
        if self.current_index == -1:
            return ""
        return self.cdata[self.current_index]


class NXE_timecode(QLineEdit):
    def __init__(self, parent):
        super(NXE_timecode,self).__init__(parent)
        self.setInputMask("99:99:99:99")
        self.setText("00:00:00:00")
       
    def set_value(self, value):
        self.default = value
        self.setText(s2time(value))
        self.setCursorPosition(0)

    def get_value(self):
        try:
            hh,mm,ss = self.text().split(":")
            hh = int(hh)
            mm = int(mm)
            ss = float(ss)
            secs = (hh*3600) + (mm*60) + ss
        except:
            secs = self.default
        return secs


class NXE_datetime(QLineEdit):
    def __init__(self, parent, base_date=False, show_seconds=False):
        super(NXE_datetime,self).__init__(parent)
        self.show_seconds = show_seconds
        self.base_date    = base_date

        mask = "99:99"
        tfmt = "%H:%M"
        if not self.base_date:
            mask = "9999-99-99 " + mask
            tfmt = "%Y-%m-%d " + tfmt
        if self.show_seconds:
            mask = mask + ":99"
            tfmt = tfmt + ":%s"
        
        self.setInputMask(mask)
        self.tfmt = tfmt
      
    def set_value(self, timestamp):
        self.default = timestamp
        if timestamp:
            tt = time.localtime(timestamp)
        else:
            tt = time.localtime(time.time())
        self.setText(time.strftime(self.tfmt, tt))

    def get_value(self):
        ttext = self.text()
        if self.base_date:
            ttext = "{} {}".format(time.strftime("%Y-%m-%d",time.localtime(self.base_date)), ttext)
        if not self.show_seconds:
            ttext = "{}:00".format(ttext)
        t = time.strptime(ttext, "%Y-%m-%d %H:%M:%S")
        return time.mktime(t)
        

class NXE_text(QLineEdit):
    def set_value(self, value):
        self.default = value
        if value == self.get_value():
            return
        self.setText(str(value))

    def get_value(self):
        return self.text()


class NXE_blob(QTextEdit):
    def set_value(self, value):
        if value == self.get_value():
            return
        self.default = value
        self.setText(str(value))

    def get_value(self):
        return self.toPlainText()


########################################################################

class MetaEditItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(MetaEditItemDelegate, self).__init__(parent)
        self.settings = {}

    def createEditor(self, parent, styleOption, index):
        parent.is_editing = True  
        try:
            key, class_, msettings, obj = index.model().data(index, Qt.EditRole)
        except:
            return None

        default_value = obj[key]
        settings = self.settings

        if isinstance(msettings, dict):
            settings.update(msettings)
        
        if default_value == "None": 
            default_value = ""
        
        if class_ == DATETIME:
            if settings:
                base_date = settings.get("base_date", False)
            else:
                base_date = False
            editor = NXE_datetime(parent, base_date)
            editor.set_value(default_value or time.time())
            editor.editingFinished.connect(self.commitAndCloseEditor)

        elif class_ == SELECT:
            editor = NXE_select(parent, settings)
            editor.set_value(default_value)
            editor.editingFinished.connect(self.commitAndCloseEditor)

        elif class_ == TIMECODE:
            editor = NXE_timecode(parent)
            editor.set_value(default_value)
            editor.editingFinished.connect(self.commitAndCloseEditor)
         
        elif class_ == TEXT:
            editor = NXE_text(parent)
            editor.set_value(default_value)
            editor.editingFinished.connect(self.commitAndCloseEditor)
         
        elif class_ == BLOB:
            parent.text_editor = TextEditor(default_value, index=index)
            parent.text_editor.setWindowTitle('{} / {} : Firefly text editor'.format(obj["title"], key))
            parent.text_editor.exec_()
            return None
        
        elif class_ == BOOLEAN:
            model = index.model()
            model.setData(index, int(not default_value))
            return None

        else:
            editor = None

        return editor

     
    def commitAndCloseEditor(self):
         editor = self.sender()
         self.commitData.emit(editor)
         self.closeEditor.emit(editor, QAbstractItemDelegate.NoHint)
         self.parent().editor_closed_at = time.time()
    
    def setEditorData(self, editor, index):
        editor.set_value(editor.default)
        # why is this here??
            
    def setModelData(self, editor, model, index):
        if editor.get_value() != editor.default: 
            model.setData(index, editor.get_value())
      




class MetaEditor(QWidget):
    def __init__(self, parent, keys):
        super(MetaEditor, self).__init__(parent)
        self.inputs = {}
        layout = QFormLayout()

        for tag, conf in keys:
            tagname = meta_types.tag_alias(tag, config.get("language","en-US"))
            
            if meta_types[tag].class_ == TEXT:
                self.inputs[tag] = NXE_text(self)

            elif meta_types[tag].class_ == BLOB:
                self.inputs[tag] = NXE_blob(self)

            elif meta_types[tag].class_ in [CS_SELECT, SELECT, ENUM, CS_ENUM]:
                if conf.get("cs", False):
                    settings = conf["cs"]
                elif meta_types[tag].class_ in [CS_ENUM, CS_SELECT]:
                    settings = []
                    for value, label in config["cs"].get(meta_types[tag].settings, []):
                        if meta_types[tag].class_ == CS_ENUM:
                            value = int(value)
                        settings.append([value, label])
                else:
                    settings = meta_types[tag].settings

                #self.inputs[tag] = NXE_select(self, settings)
                self.inputs[tag] = NXE_radio(self, settings)

            elif meta_types[tag].class_ in [TIMECODE]:
                self.inputs[tag] = NXE_timecode(self)

            else:
                self.inputs[tag] = NXE_text(self)
                self.inputs[tag].setReadOnly(True)

            layout.addRow(tagname, self.inputs[tag])
        self.setLayout(layout)

    def __getitem__(self, key):
        return self.inputs[key].get_value()

    def __setitem__(self, key, value):
        self.inputs[key].set_value(value)

