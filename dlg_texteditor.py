from firefly_common import *
from firefly_syntaxhl import *


class TextWidget(QTextEdit):
    def __init__(self, parent, syntax=False):
        super(TextWidget, self).__init__(parent)
        self.parent = parent
        self.syntax = syntax

        if syntax == "python": 
            hl = PythonHL(self)
            #option = self.document().defaultTextOption()
            #option.setFlags(option.flags() | QTextOption.ShowTabsAndSpaces);
            #self.document().setDefaultTextOption(option)
        
    def keyPressEvent(self,  event):
        if event.key() == Qt.Key_Return:
            cursor = self.textCursor()
            txt = cursor.block().text()
            trail_spaces = (len(txt) - len(txt.lstrip()))

            if self.syntax == "python":
                words = txt.lstrip().split()
                if words and words[0] in ["if", "for", "while", "def", "class", "elif", "else", "try", "except", "finally"]:
                    trail_spaces += 4
                if words and words[0] in ["return", "pass", "break"]:
                    trail_spaces = max(trail_spaces-4, 0)

            cursor.insertText("\n" + " "*trail_spaces)            
            return

        elif event.key() == Qt.Key_Tab:
            cursor = self.textCursor()
            cursor.insertText("    ")
            return    

        QTextEdit.keyPressEvent(self,  event)







def editor_toolbar(parent):
    toolbar = QToolBar(parent)
    toolbar.setMovable(False)
    toolbar.setFloatable(False)
    
    toolbar.addSeparator()
  
    action_accept = QAction(QIcon(pixlib["accept"]), 'Accept changes', parent)
    action_accept.setShortcut('ESC')
    action_accept.triggered.connect(parent.on_accept)        
    toolbar.addAction(action_accept)
  
    action_cancel = QAction(QIcon(pixlib["cancel"]), 'Cancel', parent)
    action_cancel.setShortcut('Alt+F4')
    action_cancel.triggered.connect(parent.on_cancel)        
    toolbar.addAction(action_cancel)

    return toolbar
  


class TextEditor(QDialog):    
    def __init__(self, default, index=False, syntax=False):
        super(TextEditor, self).__init__()

        ttl = ""
        if index:
            model = index.model()
            ttl += model.object_data[index.row()]["Title"]
            if ttl:
                ttl += " / "
            ttl += model.headerData(index.column(), Qt.Horizontal, Qt.DisplayRole)
            ttl = ": " + ttl

        self.setWindowTitle('Firefly text editor'+ttl)
        self.setModal(True)

        self.toolbar = editor_toolbar(self)

        self.edit = TextWidget(self, syntax)
        self.default = default
        self.setText(default)
          
        self.index = index
          
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(5)

        layout.addWidget(self.toolbar, 1)
        layout.addWidget(self.edit,2) 
          
        self.setStyleSheet(base_css)
        self.setLayout(layout)
        self.resize(640,640)

        self.show()
        self.raise_()
        self.edit.activateWindow()
        self.edit.setFocus()
        

    def on_accept(self):
        if self.index:
            self.index.model().setData(self.index,self.toPlainText())
        self.close()

    def on_cancel(self):
        self.close()
        
    def setText(self,text):
        self.edit.setText(text)

    def toPlainText(self):
        return self.edit.toPlainText()






if __name__ == "__main__":
    r = """class SuperMegaClass(object)
    def match_multiline(self, text, delimiter, in_state, style):
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        else:
            start = delimiter.indexIn(text)
            add = delimiter.matchedLength()
        while start >= 0:
            end = delimiter.indexIn(text, start + add)
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            self.setFormat(start, length, style)
            start = delimiter.indexIn(text, start + length)
        if self.currentBlockState() == in_state:  return True
        else: return False
"""

    app = QApplication(sys.argv)
    dlg = TextEditor(r, syntax="python")
    dlg.exec_()
    