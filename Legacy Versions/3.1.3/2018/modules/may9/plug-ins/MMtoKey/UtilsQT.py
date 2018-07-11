import os
try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance
    from PySide.QtUiTools import QUiLoader
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from shiboken2 import wrapInstance
    from PySide2.QtUiTools import QUiLoader
from maya import cmds, OpenMayaUI as omui


version = "1.1.1"
parent = cmds.columnLayout(p=cmds.window())		# empty hidden layout for temp parenting
location = os.path.dirname(__file__)


def wrapWidget(name="MayaWindow"):
    """wrap maya widget into QWidget shell"""
    return wrapInstance(long(omui.MQtUtil.findControl(name)), QWidget)


def createWidget(function, *args, **kwargs):
    """create maya widget as QWidget"""
    return wrapInstance(long(omui.MQtUtil.findControl(function(*args, **kwargs))), QWidget)


def loadUI(ui_file, directory=location, parent_widget=None):
    """load .ui file as a QWidget"""
    loader = QUiLoader()
    loader.setWorkingDirectory(directory)
    return loader.load(ui_file, parent_widget)      # parent widget are good for QMainWindow only


def reloadWidget(widget_name, widget=None):
    """remove copies of widget with similar names"""
    while cmds.control(widget_name, q=True, ex=True):
        cmds.deleteUI(widget_name)
    if widget:
        widget.setObjectName(widget_name)


def removeWidgets(*widget_names):
    """remove all widgets by selected names"""
    for widget_name in widget_names:
        while cmds.control(widget_name, q=True, ex=True):
            cmds.deleteUI(widget_name)


def about():
    """show parent info"""
    import Version
    window = QMainWindow(wrapWidget())
    reloadWidget(Version.name + "About", window)
    window.setWindowTitle("About")
    window.setWindowFlags(Qt.Tool)
    window.setFixedSize(180, 160)
    title = QTextEdit(window)
    title.setGeometry(10, 10, 160, 110)
    title.setText("%s\nv%s\n\n%s" % (Version.name, Version.version, Version.vendor))
    title.setReadOnly(True)
    button = QPushButton(window)
    button.setText("apply")
    button.setGeometry(50, 130, 80, 20)
    button.released.connect(lambda: cmds.deleteUI(window.objectName()))
    window.show()
