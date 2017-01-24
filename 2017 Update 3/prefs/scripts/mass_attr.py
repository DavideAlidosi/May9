"""
Massive Attribute Editor;
This tool simpply wrap all the common attributes between the selected objects and display it in a list,
you can then filter this list and edit a given attribute for all the selection at the same time.

Version 1.0 currently handles :
    Float
    Integer
    Enum
    Bool

More scripts at http://mehdilouala.com/scripts
"""

__author__ = "Mehdi Louala"
__copyright__ = "Copyright 2017, Mehdi Louala"
__credits__ = ["Mehdi Louala"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Mehdi Louala"
__email__ = "mlouala@gmail.com"
__status__ = "Stable Version"

from maya import cmds

try:
    from PySide.QtCore import Qt
    from PySide.QtGui import QTreeWidgetItem, QDialog, QVBoxLayout, QPushButton, QLineEdit, QTreeWidget, QDoubleSpinBox, \
        QSpinBox, QComboBox, QCheckBox, QWidget
    from shiboken import wrapInstance as wrapinstance
except ImportError:
    from PySide2.QtCore import Qt
    from PySide2.QtWidgets import QTreeWidgetItem, QDialog, QVBoxLayout, QPushButton, QLineEdit, QTreeWidget, \
        QDoubleSpinBox, QSpinBox, QComboBox, QCheckBox, QWidget
    from shiboken2 import wrapInstance as wrapinstance

from maya.OpenMaya import MEventMessage, MMessage
import maya.OpenMayaUI as om


def get_maya_window():
    return wrapinstance(long(om.MQtUtil.mainWindow()), QWidget)


def get_shape(node):
    shape = cmds.listRelatives(node, s=True, ni=True, f=True)
    if shape:
        return shape[0]
    else:
        return shape

Shape, Object, Separator = range(3)


class QTreeWidget_Separator(QTreeWidgetItem):
    def __init__(self, text='_______'):
        super(QTreeWidget_Separator, self).__init__()
        self.setText(0, text)
        self.setTextAlignment(0, Qt.AlignRight)
        self.setData(0, Qt.UserRole, Separator)
        self.setDisabled(True)


class MassAttribute_UI(QDialog):
    def __init__(self, parent=None):
        super(MassAttribute_UI, self).__init__(parent)
        self.setFixedWidth(300)
        self.setWindowTitle('Massive Attribute Modifier')

        L_main = QVBoxLayout()

        self.WB_ok = QPushButton('Bake', self)
        self.WB_ok.clicked.connect(self.close)

        self.WV_search = QLineEdit()
        self.WV_search.textChanged.connect(self.filter)

        self.WL_attributes = QTreeWidget()
        self.WL_attributes.setHeaderHidden(True)
        self.WL_attributes.setRootIsDecorated(False)

        self.objs_attr = set()
        self.shps_attr = set()

        self.W_EDI_float = QDoubleSpinBox()
        self.W_EDI_integer = QSpinBox()
        self.W_EDI_enum = QComboBox()
        self.W_EDI_bool = QCheckBox()

        self.ctx = None
        self.toggleOffEditors()

        L_main.addWidget(self.WV_search)
        L_main.addWidget(self.WL_attributes)
        L_edits = QVBoxLayout()
        L_edits.addWidget(self.W_EDI_bool)
        L_edits.addWidget(self.W_EDI_integer)
        L_edits.addWidget(self.W_EDI_float)
        L_edits.addWidget(self.W_EDI_enum)
        L_main.addLayout(L_edits)
        L_main.addWidget(self.WB_ok)

        self.contexts = {'float': self.apply_float,
                         'doubleLinear': self.apply_float,
                         'double': self.apply_float,
                         'enum': self.apply_enum,
                         'long': self.apply_int,
                         'short': self.apply_int,
                         'bool': self.apply_bool,
                         'time': self.apply_float,
                         'byte': self.apply_int,
                         'doubleAngle': self.apply_float}

        self.setLayout(L_main)

        self.WL_attributes.itemSelectionChanged.connect(self.update_setter)
        self.callback = MEventMessage.addEventCallback('SelectionChanged', self.update_attributes)
        self.update_attributes()

    def closeEvent(self, *args, **kwargs):
        MMessage.removeCallback(self.callback)

    def apply_value(self, value):
        sel = cmds.ls(sl=True)
        item = self.WL_attributes.selectedItems()
        shape = item[0].data(0, Qt.UserRole) == Shape
        attr = item[0].text(0)

        value = {'bool': bool,
                 'int': int,
                 'float': float,
                 'enum': int}[self.ctx](value)

        for obj in sel:
            if shape:
                shp = get_shape(obj)
                if shp == obj:
                    continue
                else:
                    obj = shp

            cmds.setAttr('%s.%s' % (obj, attr), value)

    def update_setter(self):
        item = self.WL_attributes.selectedItems()
        if not len(item):
            return

        txt = item[0].text(0)
        sel = cmds.ls(sl=True)
        target = sel[0] if item[0].data(0, Qt.UserRole) == Object else get_shape(sel[0])

        if len(sel):
            tp = cmds.getAttr('%s.%s' % (target, txt), type=True)
            try:
                self.contexts[tp](target, txt)
            except IndexError:
                self.ctx = None

    def toggleOffEditors(self):
        for widget in (self.W_EDI_float, self.W_EDI_integer, self.W_EDI_enum, self.W_EDI_bool):
            widget.setVisible(False)

        event = {'float': self.W_EDI_float.valueChanged,
                 'enum': self.W_EDI_enum.currentIndexChanged,
                 'int': self.W_EDI_integer.valueChanged,
                 'bool': self.W_EDI_bool.stateChanged}

        try:
            event[self.ctx].disconnect(self.apply_value)
        except (KeyError, RuntimeError):
            pass

    def apply_float(self, obj, attr):
        self.toggleOffEditors()
        self.ctx = 'float'
        self.W_EDI_float.setVisible(True)
        self.W_EDI_float.setValue(cmds.getAttr('%s.%s' % (obj, attr)))
        self.W_EDI_float.valueChanged.connect(self.apply_value)

    def apply_enum(self, obj, attr):
        self.toggleOffEditors()
        self.ctx = 'enum'
        self.W_EDI_enum.setVisible(True)
        self.W_EDI_enum.clear()
        enums = [enum.split('=')[0] for enum in cmds.attributeQuery(attr, n=obj, listEnum=True)[0].split(':')]
        self.W_EDI_enum.addItems(enums)
        self.W_EDI_enum.setCurrentIndex(enums.index(cmds.getAttr('%s.%s' % (obj, attr), asString=True)))
        self.W_EDI_enum.currentIndexChanged.connect(self.apply_value)

    def apply_int(self, obj, attr):
        self.toggleOffEditors()
        self.ctx = 'int'
        self.W_EDI_integer.setVisible(True)
        self.W_EDI_integer.setValue(cmds.getAttr('%s.%s' % (obj, attr)))
        self.W_EDI_integer.valueChanged.connect(self.apply_value)

    def apply_bool(self, obj, attr):
        self.toggleOffEditors()
        self.ctx = 'bool'
        self.W_EDI_bool.setVisible(True)
        self.W_EDI_bool.setChecked(cmds.getAttr('%s.%s' % (obj, attr)))
        self.W_EDI_bool.setText(attr)
        self.W_EDI_bool.stateChanged.connect(self.apply_value)

    def update_attributes(self, selection=None):
        self.objs_attr = set()
        self.shps_attr = set()
        self.WL_attributes.clear()
        self.toggleOffEditors()

        sel = cmds.ls(sl=True)

        def get_usable_attrs(obj):
            return set(cmds.listAttr(obj, se=True, ro=False, sa=True, o=True, w=True))

        if len(sel):
            self.objs_attr = get_usable_attrs(sel[0])
            shape = get_shape(sel[0])
            self.shps_attr = get_usable_attrs(shape) if shape else set()

            for obj in sel:
                self.objs_attr.intersection_update(get_usable_attrs(obj))
                shape = get_shape(obj)
                if shape:
                    self.shps_attr.intersection_update(get_usable_attrs(shape))
                    relatives = cmds.listRelatives(obj, f=True)
                    if relatives:
                        for adds in cmds.listConnections(relatives):
                            self.shps_attr.intersection_update(get_usable_attrs(adds))

        self.add_set(self.objs_attr, 'Object\'s attributes', Object)
        self.add_set(self.shps_attr, 'Shape\'s attributes', Shape)
        self.filter(self.WV_search.text())

    def add_set(self, iterable, title=None, tpe=None):
        if len(iterable):
            if title:
                self.WL_attributes.addTopLevelItem(QTreeWidget_Separator(title))

            items = []
            for attr in sorted(iterable):
                item = QTreeWidgetItem([attr])
                item.setData(0, Qt.UserRole, tpe)
                items.append(item)

            self.WL_attributes.addTopLevelItems(items)

    def filter(self, mask=''):
        self.WL_attributes.clear()

        obj_start = set([attr for attr in self.objs_attr if attr.startswith(mask)])
        obj_contains = obj_start.symmetric_difference(set([attr for attr in self.objs_attr if mask in attr]))
        shp_start = set([attr for attr in self.shps_attr if attr.startswith(mask)])
        shp_contains = shp_start.symmetric_difference(set([attr for attr in self.shps_attr if mask in attr]))

        self.add_set(obj_start, 'Obj attribute starts with', Object)
        self.add_set(obj_contains, 'Obj attribute contains', Object)
        self.add_set(shp_start, 'Shape attribute starts with', Shape)
        self.add_set(shp_contains, 'Shape attribute contains', Shape)

        if self.WL_attributes.topLevelItemCount():
            self.WL_attributes.setItemSelected(self.WL_attributes.topLevelItem(1), True)


def Display_Massive_Toggle():
    Mass_Win = MassAttribute_UI(get_maya_window())
    Mass_Win.show()
    return Mass_Win
