import maya.OpenMayaUI as omui
from maya import cmds
try:
    from PySide.QtGui import QWidget
    from shiboken import wrapInstance
except ImportError:
    from PySide2.QtWidgets import QWidget
    from shiboken2 import wrapInstance


__parent__ = cmds.columnLayout(p=cmds.window())


def wrapWidget(name="MayaWindow"):

    """wrap maya widget into QWidget shell"""

    return wrapInstance(long(omui.MQtUtil.findControl(name)), QWidget)


def createWidget(function, *args, **kwargs):

    """create maya widget as QWidget"""

    return wrapInstance(long(omui.MQtUtil.findControl(function(*args, **kwargs))), QWidget)

