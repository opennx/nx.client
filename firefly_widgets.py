import time
from functools import partial

from qt_common import *
from nx.common import *
from nx.common.metadata import meta_types
from dlg_texteditor import TextEditor


class ChannelDisplay(QLabel):
    pass

# radio or select data . array of [value, label] or array of values

class NXE_select(QComboBox):
    def __init__(self, parent, data):
        super(NXE_select,self).__init__(parent)
        self.cdata = []
        self.set_data(data)
        self.default = self.get_value()

    def setReadOnly(self, val):
        self.setEnabled(not val)

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
        for i, val in enumerate(self.cdata):
            if val == value:
                self.setCurrentIndex(i)
                break
        else:
            self.setCurrentIndex(-1)
        self.default = self.get_value()

    def get_value(self):
        if self.currentIndex() == -1:
            return ""
        return self.cdata[self.currentIndex()]



class NXE_radio(QWidget):
    def __init__(self, parent, data):
        super(NXE_radio,self).__init__(parent)
        self.cdata = []
        self.current_index = -1
        self.buttons = []
        self.set_data(data)
        self.default = self.get_value()

    def set_data(self, data):
        self.current_index = -1
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

        vbox.setContentsMargins(0,0,0,0)
        self.setLayout(vbox)

    def switch(self, index):
        self.current_index = index

    def set_value(self, value):
        if value == self.get_value():
            return
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
        self.default = self.get_value()

    def get_value(self):
        if self.current_index == -1:
            return ""
        return self.cdata[self.current_index]


    def setReadOnly(self, val):
        for w in self.buttons:
            w.setEnabled(not val)



class NXE_timecode(QLineEdit):
    def __init__(self, parent):
        super(NXE_timecode,self).__init__(parent)
        self.setInputMask("99:99:99:99")
        self.setText("00:00:00:00")
        self.default = self.get_value()

    def set_value(self, value):
        self.setText(s2time(value))
        self.setCursorPosition(0)
        self.default = self.get_value()

    def get_value(self):
        hh, mm, ss, ff = [int(i) for i in self.text().split(":")]
        return (hh*3600) + (mm*60) + ss + (ff/25.0) #FIXME: FPS


class NXE_datetime(QLineEdit):
    def __init__(self, parent, **kwargs):
        super(NXE_datetime,self).__init__(parent)
        mode = kwargs.get("mode", "datetime")

#        if not self.base_date:
#            mask = "9999-99-99 " + mask
#            tfmt = "%Y-%m-%d " + tfmt

        if mode == "date":
            self.mask   = "9999-99-99"
            self.format = "%Y-%m-%d"

        elif mode == "datetime":
            self.mask   = "9999-99-99 99:99"
            self.format = "%Y-%m-%d %H:%M"

            if kwargs.get("show_seconds", False):
                self.mask += ":99"
                self.format += ":%S"

        self.setInputMask(self.mask)
        self.default = self.get_value()

    def set_value(self, timestamp):
        self.setInputMask("")
        if timestamp:
            tt = time.localtime(timestamp)
            self.setText(time.strftime(self.format, tt))
        else:
            self.setText(self.format.replace("9","-"))
        self.setInputMask(self.mask)
        self.default = self.get_value()

    def get_value(self):
        if not self.text().replace("-", "").replace(":","").strip():
            return float(0)

        t = time.strptime(self.text(), self.format)
        return float(time.mktime(t))


class NXE_integer(QSpinBox):
    def __init__(self, parent, **kwargs):
        super(NXE_integer,self).__init__(parent)
        self.setMaximum(kwargs.get("max", 99999))
        self.default = self.get_value()

    def set_value(self, value):
        if value == self.get_value():
            return
        self.setValue(int(value))
        self.default = self.get_value()

    def get_value(self):
        return self.value()



class NXE_text(QLineEdit):
    def __init__(self, parent):
        super(NXE_text, self).__init__(parent)
        self.default = self.get_value()

    def set_value(self, value):
        if value == self.get_value():
            return
        self.setText(str(value))
        self.default = self.get_value()

    def get_value(self):
        return self.text()


class NXE_blob(QTextEdit):
    def __init__(self, parent):
        super(NXE_blob, self).__init__(parent)
        fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixed_font.setStyleHint(QFont.Monospace); 
        self.setCurrentFont(fixed_font)
        self.default = self.get_value()

    def set_value(self, value):
        if value == self.get_value():
            return
        self.setText(str(value))
        self.default = self.get_value()

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
            editor = NXE_datetime(parent, **settings)
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

                if len(settings) > 10:
                    self.inputs[tag] = NXE_select(self, settings)
                else:
                    self.inputs[tag] = NXE_radio(self, settings)


            elif meta_types[tag].class_ == BOOLEAN:
                self.inputs[tag] = NXE_radio(self, [[1,"Yes"],[0,"No"]])

            elif meta_types[tag].class_ == TIMECODE:
                self.inputs[tag] = NXE_timecode(self)


            elif meta_types[tag].class_ == DATETIME:
                self.inputs[tag] = NXE_datetime(self, **meta_types[tag].settings)

            elif meta_types[tag].class_ == INTEGER:
                self.inputs[tag] = NXE_integer(self, **(meta_types[tag].settings or {}))

            else:
                self.inputs[tag] = NXE_text(self)
                self.inputs[tag].setReadOnly(True)

            if type(conf) == dict and "default" in conf:
                self.inputs[tag].set_value(conf["default"])

            layout.addRow(tagname, self.inputs[tag])
        self.setLayout(layout)

    def keys(self):
        return self.inputs.keys()

    @property
    def meta(self):
        return {key : self[key] for key in self.keys()}

    def __getitem__(self, key):
        return self.inputs[key].get_value()

    def __setitem__(self, key, value):
        self.inputs[key].set_value(value)

    def setEnabled(self, stat):
        #super(MetaEditor, self).setEnabled(stat)
        for w in self.inputs:
            self.inputs[w].setReadOnly(not stat)

    @property
    def changed(self):
        for key in self.keys():
            if self[key] != self.inputs[key].default:
                return True
        return False

    def reset_changes(self):
        for key in self.keys():
            if self[key] != self.inputs[key].default:
                self.inputs[key].default = self[key]
                
