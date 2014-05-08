import time

from qt_common import *
from nx.common.constants import *
from dlg_texteditor import TextEditor


class NXE_timecode(QLineEdit):
    def __init__(self, parent, default=0):
        super(NXE_timecode,self).__init__(parent)
        self.setInputMask("99:99:99:99")
        if default:  
            self.SetSeconds(default)
        else:
            self.setText("00:00:00:00")
        self.setCursorPosition(0)
        self.default = default
      
    def set_seconds(self,seconds):
        try:
            self.setText(s2time(seconds))
        except:
            self.setText("00:00:00.00")

    def get_seconds(self):
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
    def __init__(self, parent, base_date=False, default=0, show_seconds=False):
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
        self.set_timestamp(default)
        self.default = default
      
    def set_timestamp(self, timestamp):
        if timestamp:
            tt = time.localtime(timestamp)
        else:
            tt = time.localtime(time.time())
        self.setText(time.strftime(self.tfmt, tt))

    def get_timestamp(self):
        ttext = self.text()
        if self.base_date:
            ttext = "{} {}".format(time.strftime("%Y-%m-%d",time.localtime(self.base_date)), ttext)
        if not self.show_seconds:
            ttext = "{}:00".format(ttext)
        t = time.strptime(ttext, "%Y-%m-%d %H:%M:%S")
        return time.mktime(t)
        





class NXE_date(QLineEdit):
    def __init__(self, parent, default=0):
        super(NDate,self).__init__(parent)
        self.setInputMask("9999-99-99")
        self.set_timestamp(default)
        self.default = default
      
    def set_timestamp(self, timestamp):
        if timestamp:
            self.setText (time.strftime("%Y-%m-%d", time.localtime(timestamp)))
        else:
            self.setText (time.strftime("%Y-%m-%d"))
      
    def get_timestamp(self):
        try:
             t = strptime (self.text(), "%Y-%m-%d")
             return time.mktime(t)
        except:
             #print "Wrong time format"
             return self.default


class NXE_select(QComboBox):
    def __init__(self, parent, data, default=False):
        super(NOption,self).__init__(parent)
        self.set_data(data,default)
        self.default = default
      
    def set_data(self, data, default=False):
        self.cdata = []
        for i,j in enumerate(sorted(data)):
            self.addItem(data[j])
            self.cdata.append(j)
            if default == j:
                self.setCurrentIndex(i)   
        if not default:
            self.setCurrentIndex(0)

    def get_value(self):
        return self.cdata[self.currentIndex()]





########################################################################

class MetaEditItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(MetaEditItemDelegate, self).__init__(parent)
        self.settings = {}

    def createEditor(self, parent, styleOption, index):
        self.parent().is_editing = True  
        try:
            tag, class_, msettings, default_value = index.model().data(index, Qt.EditRole)
        except:
            return None

        settings = self.settings

        if isinstance(msettings, dict):
            settings.update(msettings)
        
        if default_value == "None": 
            default_value = ""
        
        #########################################################################

        if class_ == DATETIME:
            if settings:
                base_date = settings.get("base_date", False)
            else:
                base_date = False

            editor = NXE_datetime(parent, base_date)

            if not default_value: 
                editor.default = int(time())
            else: 
                editor.default = int(default_value)
            editor.editingFinished.connect(self.commitAndCloseEditor)

        #########################################################################


        elif class_ == DATE:
            editor = NXE_date(parent)
            if not default_value: 
                editor.default = int(time())
            else: 
                editor.default = int(default_value)
            editor.editingFinished.connect(self.commitAndCloseEditor)

        elif class_ == SELECT:
            editor = NOption(parent, settings, default_value)
         
        elif class_ == TEXT:
            editor = QLineEdit(parent)
            editor.default = default_value
            editor.editingFinished.connect(self.commitAndCloseEditor)
         
        elif class_ == BLOB:
            parent.text_editor = TextEditor(default_value, index)
            return None
        
        elif class_ in [BOOLEAN, STAR]:
            model = index.model()
            model.setData(index, int(not default_value))
            return None

        else:
            editor = None

        return editor

     #######################################################################
     
    def commitAndCloseEditor(self):
         editor = self.sender()
         self.commitData.emit(editor)
         self.closeEditor.emit(editor, QAbstractItemDelegate.NoHint)
         self.parent().editor_closed_at = time.time()

     #######################################################################
     
    def setEditorData(self, editor, index):
        if isinstance(editor,NXE_datetime) or isinstance(editor, NXE_date):
            editor.set_timestamp(editor.default)
       
        elif isinstance(editor, QLineEdit) or isinstance(editor, QTextEdit) or isinstance(editor, TextEditor):
            editor.setText(editor.default)

     #######################################################################
     
    def setModelData(self, editor, model, index):
        if isinstance(editor,NXE_datetime) or isinstance(editor,NXE_date):
            val = editor.get_timestamp()
            if val != editor.default: 
                model.setData(index, val)
          
        elif isinstance(editor, QLineEdit):
            if editor.text() != editor.default: 
                model.setData(index, editor.text())
          
        elif isinstance(editor, QTextEdit) or isinstance(editor, wndTextEdit):
            if editor.toPlainText() != editor.default:
                model.setData(index, editor.toPlainText()) 
           
        elif isinstance(editor, NOption):
            if editor.GetValue() != editor.default: 
                model.setData(index, editor.get_value()) 
          
