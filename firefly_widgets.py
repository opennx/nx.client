#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from firefly_skin   import *
from firefly_syntaxhl import *

from nx.common.constants import *


class NXE_timecode(QLineEdit):
    def __init__(self, parent, default=0):
        super(NTimeCode,self).__init__(parent)
        self.setInputMask("99:99:99.99")
        if default:  
            self.SetSeconds(default)
        else:
            self.setText("00:00:00.00")
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
    def __init__(self, parent, default=0):
        super(NDateTime,self).__init__(parent)
        self.setInputMask("9999-99-99 99:99:99")
        self.set_timestamp(default)
        self.default = default
      
    def set_timestamp(self, timestamp):
        if timestamp: 
            self.setText (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)))
        else:
            self.setText (time.strftime("%Y-%m-%d %H:%M:%S"))
      
    def get_timestamp(self):
        try:
            t = time.strptime (self.text(), "%Y-%m-%d %H:%M:%S")
            return mktime(t)
        except:
            print "Wrong time format"
            return self.default


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
             print "Wrong time format"
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



class NXE_blob(QDialog):    
    def __init__(self, index, default, syntax=False):
        super(wndTextEdit, self).__init__()
        self.setWindowTitle('Text editor: Press ESC to discard, Alt+F4 to Save and close')
        self.setModal(True)
        self.setStyleSheet(base_css)
          
        self.edit = QTextEdit(self)
        if syntax == "python": 
            hl = PythonHL(self.edit)
        self.edit.setStyleSheet("font: 9pt \"Courier\";")
          
        self.default = default
        self.setText(default)
          
        self.index = index
          
        layout = QVBoxLayout()
        layout.addWidget(self.edit)
          
        self.setLayout(layout)
        self.resize(640,640)
        self.show()
        self.raise_()
        self.edit.activateWindow()
        self.edit.setFocus()
        
    def closeEvent(self,evt):
        print self.index.model().setData(self.index,self.toPlainText())
        
    def setText(self,text):
        self.edit.setText(text)

    def toPlainText(self):
        return self.edit.toPlainText()






########################################################################

class MetaEditItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(MetaEditItemDelegate, self).__init__(parent)
        self.parent = parent

    def createEditor(self, parent, styleOption, index):
        self.parent.is_editing = True  
        try:
            tag, class_, ops, default_value = index.model().data(index, Qt.EditRole)
        except:
            print "hovno"
            return None
        
        print "EDIT:", tag, ">>", class_ , ops

        if default_value == "None": 
            default_value = ""
        
        if class_ == DATETIME:
            editor = NXE_datetime(parent)
            if not default_value: 
                editor.default = int(time())
            else: 
                editor.default = int(default_value)
            editor.editingFinished.connect(self.commitAndCloseEditor)
         
        elif class_ == DATE:
            editor = NXE_date(parent)
            if not default_value: 
                editor.default = int(time())
            else: 
                editor.default = int(default_value)
            editor.editingFinished.connect(self.commitAndCloseEditor)
        
        elif class_ == TIME:
            editor = QLineEdit(parent)
            editor.setInputMask("99:99")
            editor.default = strftime("%H:%M",localtime(default_value))
            editor.editingFinished.connect(self.commitAndCloseEditor)

        elif class_ == SELECT:
            editor = NOption(parent,ops,default_value)
         
        elif class_ == TEXT:
            editor = QLineEdit(parent)
            editor.default = default_value
            editor.editingFinished.connect(self.commitAndCloseEditor)
         
        elif class_ == BLOB:
            self.parent.text_editor = wndTextEdit(index, default_value)
            return None
        
        else:
            editor = None

        return editor

     #######################################################################
     
    def commitAndCloseEditor(self):
         editor = self.sender()
         self.commitData.emit(editor)
         self.closeEditor.emit(editor, QAbstractItemDelegate.NoHint)
         self.parent.editor_closed_at = time.time()

     #######################################################################
     
    def setEditorData(self, editor, index):
        if isinstance(editor,NXE_datetime) or isinstance(editor, NXE_date):
            editor.set_timestamp(editor.default)
       
        elif isinstance(editor, QLineEdit) or isinstance(editor, QTextEdit) or isinstance(editor, wndTextEdit):
            editor.setText(editor.default)

     #######################################################################
     
    def setModelData(self, editor, model, index):
        if isinstance(editor,NXE_datetime) or isinstance(editor,NXE_date):
            val = editor.GetTimestamp()
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
                model.setData(index, editor.GetValue()) 
          
        elif editor == "boolean":
            model.setData(index, str(int(not bool(int(model.data(index,Qt.DisplayRole)))))) 
