import maya.OpenMayaUI as omui
import maya.cmds as mc
import maya.mel as mel
import maya.app.mayabullet.BulletUtils as BulletUtils
BulletUtils.checkPluginLoaded()
import maya.app.mayabullet.RigidBody as RigidBody

import sys

import Helios_Commands

reload(Helios_Commands)

from PySide import QtCore
from PySide import QtGui

from shiboken import wrapInstance


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


class Helios(QtGui.QComboBox):
    def __init__(self, parent=None):
        super(Helios, self).__init__(parent)

        self.close()

        self.mouse_is_over = False

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setEditable(True)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        self.pFilterModel = QtGui.QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        self.completer = QtGui.QCompleter(self)
        self.completer.setModel(self.pFilterModel)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer.setCompletionMode(QtGui.QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)

        def filter(entered_string):
            self.pFilterModel.setFilterFixedString(str(entered_string))

        self.lineEdit().textEdited[unicode].connect(filter)
        self.completer.activated.connect(self.on_completer_activated)
        self.activated.connect(self.on_completer_activated)

        names = sorted(Helios_Commands.all_commands.keys())

        font = QtGui.QFont()
        font.setPointSize(12.5)
        self.setFont(font)

        self.addItems(names)

        self.setModelColumn(0)
        self.clearEditText()
        self.resize(300, 40)
        self.show()
        self.activateWindow()
        self.setFocus()
        self.raise_()

    def on_completer_activated(self, entered_string):
        if entered_string:
            index = self.findText(str(entered_string))
            self.setCurrentIndex(index)

        command = entered_string

        try:
            exec Helios_Commands.all_commands[command]
            sys.stdout.write("Success: {0}.".format(command))
        except:
            mc.warning("Couldn't complete operation...")

        self.close()

    def setModel(self, model):
        super(Helios, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(Helios, self).setModelColumn(column)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
        else:
            QtGui.QComboBox.keyPressEvent(self, e)

    def focusOutEvent(self, event):
        if not self.mouse_is_over:
            self.close()

    def enterEvent(self, event):
        self.mouse_is_over = True

    def leaveEvent(self, event):
        self.mouse_is_over = False


if __name__ == "__main__":
    try:
        ui.close()
    except:
        pass

    Helios()
