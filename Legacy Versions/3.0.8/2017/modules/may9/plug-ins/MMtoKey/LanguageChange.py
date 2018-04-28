import re
import os
try:    # under Maya 2017
    from PySide.QtCore import *
    from PySide.QtGui import *
except ImportError:     # Maya 2017 and above
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
from maya import cmds
import UtilsQT


location = os.path.dirname(__file__)


class MainWindow(QMainWindow):
    """marking menu change language editor"""

    def __init__(self):
        QMainWindow.__init__(self, UtilsQT.wrapWidget())
        self.ui = UtilsQT.loadUI(location + "/resources/ui/LanguageChange.ui", location + "/resources/ui", self)
        UtilsQT.reloadWidget("MMtoKeyPyUI", self)
        self.setWindowTitle("Marking Menu change language")
        self.setWindowFlags(Qt.Tool)
        self.setFixedSize(500, 320)
        
        self.ui.btn_language._menu = QMenu()
        self.ui.btn_language.setMenu(self.ui.btn_language._menu)
        self.ui.btn_language._menu.addAction("mel", lambda: self._language("mel"))
        self.ui.btn_language._menu.addAction("python", lambda: self._language("python"))
        icon = UtilsQT.createWidget(cmds.image, 'MMtoKeyPyIconWidget', p=UtilsQT.parent)
        icon.setGeometry(250, 30, 32, 32)
        icon.setParent(self)
        self.menuBar().addAction('open', self._open)
        self.menuBar().addAction('save', self._save)
        self._file_read = ""
        self._data = []
        self.ui.btn_save.setEnabled(False)
        self.ui.btn_save.released.connect(self._command)
        self.ui.list_items.itemSelectionChanged.connect(self._select)
        self.show()

    def _saveCommand(self):
        """save command"""
        self.ui.list_items.currentItem().setCommand(self.ui.text_edit.toPlainText())

    def _open(self):
        """open marking menu"""
        self._file_read = cmds.fileDialog2(fm=1, ff='menu_*.mel', dir=cmds.internalVar(umm=True))[0]
        self.ui.list_items.clear()
        self.ui.list_items.setCurrentRow(-1)
        self._data = []
        self._mel_block = open(self._file_read).readlines()
        i = 0

        while i < len(self._mel_block):
            if 'menuItem' in self._mel_block[i]:
                i += 1
                item = {"label": "", "command": [-1, ""], "language": [-1, "mel"], "icon": ""}
                include = True
                while '-' in self._mel_block[i]:
                    if '-label ' in self._mel_block[i]:
                        item["label"] = re.match('(.*)-label "(.*)"(.*)', self._mel_block[i]).group(2)
                    elif '-command ' in self._mel_block[i]:
                        item["command"] = [i, re.match('(.*)-command "(.*)"(.*)', self._mel_block[i]).group(2)]
                    elif '-sourceType ' in self._mel_block[i]:
                        item["language"] = [i, re.match('(.*)-sourceType "(.*)"(.*)', self._mel_block[i]).group(2)]
                    elif '-image ' in self._mel_block[i]:
                        item["icon"] = re.match('(.*)-image "(.*)"(.*)', self._mel_block[i]).group(2)
                    elif '-subMenu 1' in self._mel_block[i] or '-optionBox 1' in self._mel_block[i]:
                        include = False
                    i += 1
                if include:
                    self._data.append(item)
                    self.ui.list_items.addItem(item["label"])
            else:
                i += 1

    def _select(self):
        """current index changed"""
        indices = [x.row() for x in self.ui.list_items.selectedIndexes()]
        if not indices:
            self.ui.text_edit.setText("")
            self.ui.btn_language.setText("")
            cmds.image("MMtoKeyPyIconWidget", e=True, vis=False)
            self.ui.text_edit.setEnabled(False)
            self.ui.btn_language.setEnabled(False)
            self.ui.btn_save.setEnabled(False)
        elif len(indices) == 1:
            self.ui.text_edit.setText(self._data[indices[0]]["command"][1].replace('\\"', '"').replace('\\n', '\n'))
            self.ui.btn_language.setText(self._data[indices[0]]["language"][1])
            cmds.image("MMtoKeyPyIconWidget", e=True, vis=True, i=self._data[indices[0]]["icon"])
            self.ui.text_edit.setEnabled(True)
            self.ui.btn_language.setEnabled(True)
            self.ui.btn_save.setEnabled(True)
        else:
            self.ui.text_edit.setText("")
            self.ui.btn_language.setText(self._data[indices[0]]["language"][1])
            cmds.image("MMtoKeyPyIconWidget", e=True, vis=False)
            self.ui.text_edit.setEnabled(False)
            self.ui.btn_language.setEnabled(True)
            self.ui.btn_save.setEnabled(False)

    def _save(self):
        """save marking menu"""
        with open(self._file_read, 'w') as fileread:
            fileread.write(''.join(self._mel_block))
        cmds.warning("saved")

    def _language(self, language):
        """apply new language"""
        indices = [x.row() for x in self.ui.list_items.selectedIndexes()]
        for i in indices:
            number = self._data[i]["language"][0]
            self._mel_block[number] = self._mel_block[number].replace(self._data[i]["language"][1], language)
            self._data[i]["language"][1] = language
        self.ui.btn_language.setText(self._data[indices[0]]["language"][1])

    def _command(self):
        """apply new command"""
        i = self.ui.list_items.selectedIndexes()[0].row()
        text = self.ui.text_edit.toPlainText().replace('"', '\\"').replace('\n', '\\n')
        number = self._data[i]["command"][0]
        self._mel_block[number] = self._mel_block[number].replace(self._data[i]["command"][1], text)
        self._data[i]["command"][1] = text
