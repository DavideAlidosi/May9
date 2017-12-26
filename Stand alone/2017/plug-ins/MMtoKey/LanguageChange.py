import re
try:    # under Maya 2017
    from PySide.QtCore import *
    from PySide.QtGui import *
except ImportError:     # Maya 2017 and above
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
from maya import cmds
import QtWrapper


class ChangeLanguage(QMainWindow):
    """marking menu change language editor"""

    def __init__(self):
        QMainWindow.__init__(self, QtWrapper.wrapWidget())
        while cmds.window('MMtoKeyPyUI', ex=True):
            cmds.deleteUI('MMtoKeyPyUI')
        while cmds.control('MMtoKeyPyIconWidget', ex=True):
            cmds.deleteUI('MMtoKeyPyIconWidget')
        self.setFixedSize(350, 220)
        self.setWindowTitle('Marking Menu change language')
        self.setWindowFlags(Qt.Tool)
        self.setObjectName('MMtoKeyPyUI')
        self._btn_language = QPushButton(self)
        menu = QMenu(self)
        menu.addAction("mel", lambda: self._language("mel"))
        menu.addAction("python", lambda: self._language("python"))
        self._btn_language.setMenu(menu)
        self._btn_language.setGeometry(180, 30, 80, 20)
        self._listwidget = QListWidget(self)
        self._listwidget.setGeometry(10, 30, 160, 180)
        self._listwidget.setSelectionMode(QListWidget.ExtendedSelection)
        self._text_edit = QTextEdit(self)
        self._text_edit.setGeometry(180, 100, 160, 110)
        self._text_edit.setEnabled(False)
        self._text_edit.setLineWrapMode(QTextEdit.NoWrap)
        icon = QtWrapper.createWidget(cmds.image, 'MMtoKeyPyIconWidget', p=QtWrapper.__parent__)
        icon.setGeometry(180, 60, 32, 32)
        icon.setParent(self)

        self._btn_save = QPushButton(self)
        self._btn_save.setGeometry(220, 60, 120, 30)
        self._btn_save.setText("save")
        self._btn_save.setEnabled(False)
        self._btn_save.released.connect(self._command)
        self._listwidget.itemSelectionChanged.connect(self._select)

        self.menuBar().addAction('open', self._open)
        self.menuBar().addAction('save', self._save)
        self._file_read = ""
        self._data = []
        self.show()

    def _saveCommand(self):
        """save command"""
        self._listwidget.currentItem().setCommand(self._text_edit.toPlainText())

    def _open(self):
        """open marking menu"""
        self._file_read = cmds.fileDialog2(fm=1, ff='menu_*.mel', dir=cmds.internalVar(umm=True))[0]
        self._listwidget.clear()
        self._listwidget.setCurrentRow(-1)
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
                    self._listwidget.addItem(item["label"])
            else:
                i += 1

    def _select(self):
        """current index changed"""
        indices = [x.row() for x in self._listwidget.selectedIndexes()]
        if not indices:
            self._text_edit.setText("")
            self._btn_language.setText("")
            cmds.image("MMtoKeyPyIconWidget", e=True, vis=False)
            self._text_edit.setEnabled(False)
            self._btn_language.setEnabled(False)
            self._btn_save.setEnabled(False)
        elif len(indices) == 1:
            self._text_edit.setText(self._data[indices[0]]["command"][1].replace('\\"', '"').replace('\\n', '\n'))
            self._btn_language.setText(self._data[indices[0]]["language"][1])
            cmds.image("MMtoKeyPyIconWidget", e=True, vis=True, i=self._data[indices[0]]["icon"])
            self._text_edit.setEnabled(True)
            self._btn_language.setEnabled(True)
            self._btn_save.setEnabled(True)
        else:
            self._text_edit.setText("")
            self._btn_language.setText(self._data[indices[0]]["language"][1])
            cmds.image("MMtoKeyPyIconWidget", e=True, vis=False)
            self._text_edit.setEnabled(False)
            self._btn_language.setEnabled(True)
            self._btn_save.setEnabled(False)

    def _save(self):
        """save marking menu"""
        with open(self._file_read, 'w') as fileread:
            fileread.write(''.join(self._mel_block))
        cmds.warning("saved")

    def _language(self, language):
        """apply new language"""
        indices = [x.row() for x in self._listwidget.selectedIndexes()]
        for i in indices:
            number = self._data[i]["language"][0]
            self._mel_block[number] = self._mel_block[number].replace(self._data[i]["language"][1], language)
            self._data[i]["language"][1] = language
        self._btn_language.setText(self._data[indices[0]]["language"][1])

    def _command(self):
        """apply new command"""
        i = self._listwidget.selectedIndexes()[0].row()
        text = self._text_edit.toPlainText().replace('"', '\\"').replace('\n', '\\n')
        number = self._data[i]["command"][0]
        self._mel_block[number] = self._mel_block[number].replace(self._data[i]["command"][1], text)
        self._data[i]["command"][1] = text
