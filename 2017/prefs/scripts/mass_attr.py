"""
Massive Attribute Editor;
This tool simpply wrap all the common attributes between the selected objects and display it in a list,
you can then filter this list and edit a given attribute for all the selection at the same time.

Version 1.4 currently handles :
    Float
    Integer
    Enum
    Bool
    Float 3
    Float 4
    Color
    String

More scripts at http://mehdilouala.com/scripts
"""

__author__ = "Mehdi Louala"
__copyright__ = "Copyright 2017, Mehdi Louala"
__credits__ = ["Mehdi Louala"]
__license__ = "GPL"
__version__ = "1.4.0"
__maintainer__ = "Mehdi Louala"
__email__ = "mlouala@gmail.com"
__status__ = "Stable Version"

from maya import cmds
from maya.OpenMaya import MEventMessage, MMessage
import maya.OpenMayaUI as om

try:
    from PySide.QtCore import QObject, QLocale, Qt, Signal
    from PySide.QtGui import QDialog, QTreeWidget, QSpinBox, QComboBox, QCheckBox, QIcon, QTreeWidgetItem, QWidget, \
        QGroupBox, QDoubleSpinBox, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QColorDialog, QLineEdit
    from shiboken import wrapInstance as wrapinstance
except ImportError:
    from PySide2.QtCore import QObject, QLocale, Qt
    from PySide2.QtCore import pyqtSignal as Signal
    from PySide2.QtGui import QIcon
    from PySide2.QtWidgets import QDialog, QTreeWidget, QSpinBox, QComboBox, QCheckBox, QTreeWidgetItem, QWidget, \
        QGroupBox, QDoubleSpinBox, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QColorDialog, QLineEdit
    from shiboken2 import wrapInstance as wrapinstance


Shape, Object, Separator = range(3)


def get_maya_window():
    return wrapinstance(long(om.MQtUtil.mainWindow()), QWidget)


def get_shape(node):
    shape = cmds.listRelatives(node, s=True, ni=True, f=True)
    if shape:
        return shape[0]
    else:
        return shape


class QTreeWidget_Separator(QTreeWidgetItem):
    def __init__(self, text='_______'):
        super(QTreeWidget_Separator, self).__init__()
        self.setText(0, text)
        self.setTextAlignment(0, Qt.AlignRight)
        self.setData(0, Qt.UserRole, Separator)
        self.setDisabled(True)


class Double3Group(QGroupBox):
    valuesChanged = Signal(list)

    def __init__(self, parent=None):
        super(Double3Group, self).__init__(parent)
        self.x = QDoubleSpinBox()
        self.y = QDoubleSpinBox()
        self.z = QDoubleSpinBox()
        self.setLayout(line(self.x, self.y, self.z))
        for elem in (self.x, self.y, self.z):
            elem.valueChanged.connect(self.element_value_changed)

    def element_value_changed(self):
        self.valuesChanged.emit([self.x.value(), self.y.value(), self.z.value()])

    def setValues(self, xyz):
        x, y, z = xyz
        self.x.setValue(x)
        self.y.setValue(y)
        self.z.setValue(z)


class Double4Group(Double3Group):
    def __init__(self, parent=None):
        super(Double4Group, self).__init__(parent)
        self.w = QDoubleSpinBox()
        self.layout().addWidget(self.w)
        self.w.valueChanged.connect(self.element_value_changed)

    def element_value_changed(self):
        self.valuesChanged.emit([self.x.value(), self.y.value(), self.z.value(), self.w.value()])

    def setValues(self, xyzw):
        x, y, z, w = xyzw
        self.x.setValue(x)
        self.y.setValue(y)
        self.z.setValue(z)
        self.z.setValue(w)


class ColorPicker(QPushButton):
    colorChanged = Signal(list)

    def __init__(self, parent=None):
        super(ColorPicker, self).__init__(parent)
        self.setText('Pick color...')
        self.clicked.connect(self.get_color)

    def get_color(self):
        dial = QColorDialog()
        dial.setOptions(QColorDialog.DontUseNativeDialog)
        res = dial.exec_()
        if res:
            rgb = dial.currentColor().red(), dial.currentColor().green(), dial.currentColor().blue()
            self.setColor(rgb)
            rgb = [c / 255.0 for c in rgb]
            self.colorChanged.emit(rgb)

    def setColor(self, rgb=(255, 255, 255)):
        r, g, b = rgb
        color = 'rgb({},{},{})'.format(r, g, b)
        fg = 'white' if sum([r, g, b]) < 255 else 'black'
        self.setStyleSheet('QPushButton{background-color:%s;color:%s;}' % (color, fg))
        self.update()


class Filter(QLineEdit):
    def __init__(self, *args):
        super(Filter, self).__init__(*args)
        self.textChanged.connect(self.isClean)

        self.clear_button = QPushButton('x', self)
        self.clear_button.setVisible(False)
        self.clear_button.setCursor(Qt.ArrowCursor)
        self.clear_button.clicked.connect(self.clear)

    def isClean(self, text):
        self.clear_button.setVisible(text != '')

    def resizeEvent(self, e):
        super(Filter, self).resizeEvent(e)
        self.clear_button.setGeometry(self.width() - 18, 2, 16, 16)


def line(*widgets):
    """
    Creates a horizontal layout

    :param widgets: the widgets you wan to add to the layout
    :type  widgets: tuple[QWidget]

    :return: the horizontal layout
    :rtype: QHBoxLayout
    """
    l = QHBoxLayout()
    apply_layout(l, *widgets)
    return l


def col(*widgets):
    """
    Creates a vertical layout

    :param widgets: the widgets you wan to add to the layout
    :type  widgets: tuple[QWidget]

    :return: the vertical layout
    :rtype: QVBoxLayout
    """
    l = QVBoxLayout()
    apply_layout(l, *widgets)
    return l


def group(title='', *widgets):
    """
    Creates a groupBox with the widgets inside

    :param   title: group's title
    :param widgets: widgets you wqnt to qdd
    :type  widgets: tuple[QWidget]

    :return: the group box
    :rtype: QGroupBox
    """
    g = QGroupBox()
    g.setTitle(title)
    l = QVBoxLayout()
    apply_layout(l, *widgets)
    l.setContentsMargins(4, 4, 4, 4)
    g.setLayout(l)
    return g


def apply_layout(l, *widgets):
    """
    Apply the widgets to the given layout

    :param       l: the layout
    :type        l: QHBoxLayout | QVBoxLayout
    :param widgets: the widgets you want to add
    :type  widgets: tuple[QWidget]
    """
    # looping through widget and add them to the given layout
    for i, widget in enumerate(widgets):
        if isinstance(widget, basestring):
            widget = QLabel(widget)

        try:
            l.addWidget(widget)

        except TypeError:
            l.addLayout(widget)

        l.setStretch(i, int(not isinstance(widget, QLabel)))

    l.setContentsMargins(0, 0, 0, 0)


class MassAttribute_UI(QDialog):
    class Applikator(QObject):
        def __init__(self, parent=None):
            super(MassAttribute_UI.Applikator, self).__init__()
            self.root = parent

        def widget_event(self, t):
            return {'float': self.root.W_EDI_float.valueChanged, 'enum': self.root.W_EDI_enum.currentIndexChanged,
                    'int': self.root.W_EDI_int.valueChanged, 'bool': self.root.W_EDI_bool.stateChanged,
                    'str': self.root.W_EDI_str.textChanged, 'd3': self.root.W_EDI_d3.valuesChanged,
                    'd4': self.root.W_EDI_d4.valuesChanged, 'color': self.root.W_EDI_color.colorChanged}[t]

        def unset_editors(self):
            for widget in (self.root.W_EDI_float, self.root.W_EDI_int, self.root.W_EDI_enum,
                           self.root.W_EDI_bool, self.root.W_EDI_str, self.root.W_EDI_d3,
                           self.root.W_EDI_d4, self.root.W_EDI_color):
                widget.setVisible(False)

            try:
                self.widget_event(self.root.ctx).disconnect(self.root.apply_value)
            except (KeyError, RuntimeError):
                pass

        def _prepare(applier_name):
            def sub_wrapper(func):
                def wrapper(self, *args, **kwargs):
                    self.unset_editors()
                    self.root.ctx = applier_name
                    self.root.__getattribute__('W_EDI_%s' % applier_name).setVisible(True)
                    ret = func(self, *args, **kwargs)
                    return ret
                return wrapper
            return sub_wrapper

        @_prepare('float')
        def apply_float(self, obj, attr):
            self.root.W_EDI_float.setValue(cmds.getAttr('%s.%s' % (obj, attr)))

        @_prepare('enum')
        def apply_enum(self, obj, attr):
            self.root.W_EDI_enum.clear()
            enums = [enum.split('=')[0] for enum in cmds.attributeQuery(attr, n=obj, listEnum=True)[0].split(':')]
            self.root.W_EDI_enum.addItems(enums)
            self.root.W_EDI_enum.setCurrentIndex(enums.index(cmds.getAttr('%s.%s' % (obj, attr), asString=True)))

        @_prepare('int')
        def apply_int(self, obj, attr):
            self.root.W_EDI_int.setValue(cmds.getAttr('%s.%s' % (obj, attr)))

        @_prepare('bool')
        def apply_bool(self, obj, attr):
            self.root.W_EDI_bool.setChecked(cmds.getAttr('%s.%s' % (obj, attr)))
            self.root.W_EDI_bool.setText(attr)

        @_prepare('str')
        def apply_str(self, obj, attr):
            self.root.W_EDI_str.setText(cmds.getAttr('%s.%s' % (obj, attr)))

        @_prepare('d3')
        def apply_d3(self, obj, attr):
            self.root.W_EDI_d3.setValues(cmds.getAttr('%s.%s' % (obj, attr))[0])

        @_prepare('d4')
        def apply_d4(self, obj, attr):
            self.root.W_EDI_d4.setValues(cmds.getAttr('%s.%s' % (obj, attr))[0])

        @_prepare('color')
        def apply_color(self, obj, attr):
            try:
                colors = cmds.getAttr('%s.%s' % (obj, attr))[0]
                self.root.W_EDI_color.setColor([int(c * 255) for c in colors])
            except TypeError:
                self.apply_int(obj, attr)

    ctx_icons = {'float': QIcon(':render_decomposeMatrix.png'),
                 'enum': QIcon(':showLineNumbers.png'),
                 'bool': QIcon(':out_decomposeMatrix.png'),
                 'time': QIcon(':time.svg'),
                 'byte': QIcon(':out_defaultTextureList.png'),
                 'doubleAngle': QIcon(':angleDim.png'),
                 'string': QIcon(':text.png'),
                 'double3': QIcon(':animCurveTA.svg'),
                 'color': QIcon(':clampColors.svg')}

    for ctx in ('doubleLinear', 'double', 'long', 'short'):
        ctx_icons[ctx] = ctx_icons['float']

    for ctx in ('float3', 'double4', 'float4'):
        ctx_icons[ctx] = ctx_icons['double3']

    def __init__(self, parent=None):
        super(MassAttribute_UI, self).__init__(parent)
        self.setLocale(QLocale.C)
        self.setFixedWidth(300)
        self.setWindowTitle('Massive Attribute Modifier')

        L_main = QVBoxLayout()
        self.applier = self.Applikator(self)

        self.WV_search = Filter()
        self.WV_search.textChanged.connect(self.filter)

        self.WL_attributes = QTreeWidget()
        self.setStyleSheet('''
QTreeView {
    alternate-background-color: #1b1b1b;
}''')
        self.WL_attributes.setAlternatingRowColors(True)
        self.WL_attributes.setHeaderHidden(True)
        self.WL_attributes.setRootIsDecorated(False)

        self.objs_attr = set()
        self.shps_attr = set()

        self.W_EDI_float = QDoubleSpinBox()
        self.W_EDI_int = QSpinBox()
        self.W_EDI_enum = QComboBox()
        self.W_EDI_bool = QCheckBox()
        self.W_EDI_str = QLineEdit()
        self.W_EDI_d3 = Double3Group()
        self.W_EDI_d4 = Double4Group()
        self.W_EDI_color = ColorPicker()

        self.ctx = None
        self.applier.unset_editors()

        L_main.addWidget(self.WV_search)
        L_main.addWidget(self.WL_attributes)
        L_main.addLayout(col(self.W_EDI_bool, self.W_EDI_int, self.W_EDI_float,
                             self.W_EDI_enum, self.W_EDI_str, self.W_EDI_d3, self.W_EDI_d4,
                             self.W_EDI_color))
        L_main.setStretch(1, 1)

        self.contexts = {'float': self.applier.apply_float,
                         'doubleLinear': self.applier.apply_float,
                         'double': self.applier.apply_float,
                         'enum': self.applier.apply_enum,
                         'long': self.applier.apply_int,
                         'short': self.applier.apply_int,
                         'bool': self.applier.apply_bool,
                         'time': self.applier.apply_float,
                         'byte': self.applier.apply_int,
                         'doubleAngle': self.applier.apply_float,
                         'string': self.applier.apply_str,
                         'double3': self.applier.apply_d3,
                         'float3': self.applier.apply_d3,
                         'double4': self.applier.apply_d4,
                         'float4': self.applier.apply_d4,
                         'color': self.applier.apply_color}

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
        tpe = item[0].attrType

        value = {'bool': bool,
                 'int': int,
                 'float': float,
                 'enum': int,
                 'str': str,
                 'd3': list,
                 'd4': list,
                 'color': list}[self.ctx](value)

        cmds.undoInfo(openChunk=True)

        for obj in sel:
            if shape:
                shp = get_shape(obj)
                if shp == obj:
                    continue
                else:
                    obj = shp
            if tpe == 'string':
                cmds.setAttr('%s.%s' % (obj, attr), value, type='string')
            elif tpe in ('double3', 'double4', 'float3', 'float4', 'color'):
                cmds.setAttr('%s.%s' % (obj, attr), *value, type='double%d' % len(value))
            else:
                cmds.setAttr('%s.%s' % (obj, attr), value)

        cmds.undoInfo(closeChunk=True)

    def update_setter(self):
        item = self.WL_attributes.selectedItems()
        if not len(item):
            return

        txt = item[0].text(0)
        sel = cmds.ls(sl=True)
        target = sel[0] if item[0].data(0, Qt.UserRole) == Object else get_shape(sel[0])

        if len(sel):
            try:
                self.contexts[item[0].attrType](target, txt)
                self.applier.widget_event(self.ctx).connect(self.apply_value)

            except IndexError:
                self.ctx = None

    @staticmethod
    def get_attributes_type(obj, attrs):
        raw_attrs = list(attrs)
        raw_attrs.sort()
        attrs, attrs_types = [], []

        for i, attr in enumerate(raw_attrs):
            try:
                tpe = cmds.getAttr('%s.%s' % (obj, attr), typ=True)
                assert tpe
                attrs.append(attr)
                attrs_types.append(tpe)
            except (AssertionError, ValueError, RuntimeError):
                pass

        rm_list = set()
        layers = {'3': 'XYZ', '4': 'XYZW'}
        for i, attr in enumerate(attrs):
            if i in rm_list:
                continue

            tpe = attrs_types[i]

            if attr.endswith('RGB'):
                if '%sR' % attr[:-3] in attrs:
                    attrs_types[i] = 'color'
                    for chan in 'RGB':
                        rm_list.add(attrs.index('%s%s' % (attr[:-3], chan)))

            elif tpe not in MassAttribute_UI.ctx_icons:
                rm_list.add(i)

            elif attr.endswith('R'):
                if '%sG' % attr[:-1] in attrs and attr[:-1] in attrs:
                    attrs_types[attrs.index(attr[:-1])] = 'color'
                    for chan in 'RGB':
                        rm_list.add(attrs.index('%s%s' % (attr[:-1], chan)))

            elif tpe in ('double3', 'double4', 'float3', 'float4'):
                if '%sX' % attr in attrs:
                    for chan in layers[tpe[-1]]:
                        rm_list.add(attrs.index('%s%s' % (attr, chan)))
                        # print attrs

        for i in sorted(rm_list, reverse=True):
            attrs_types.pop(i)
            attrs.pop(i)

        return [(attr, tpe) for attr, tpe in zip(attrs, attrs_types)]

    def update_attributes(self, selection=None):
        self.objs_attr = set()
        self.shps_attr = set()
        self.WL_attributes.clear()
        self.applier.unset_editors()

        sel = cmds.ls(sl=True)

        def get_usable_attrs(obj):
            return set(cmds.listAttr(obj, se=True, ro=False, m=True, w=True))

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
                        for adds in (cmds.listConnections(relatives) or []):
                            self.shps_attr.intersection_update(get_usable_attrs(adds))

            self.objs_attr = self.get_attributes_type(sel[0], self.objs_attr)
            self.shps_attr = self.get_attributes_type(shape, self.shps_attr)

        self.add_set(self.objs_attr, 'Object\'s attributes', Object)
        self.add_set(self.shps_attr, 'Shape\'s attributes', Shape)
        self.filter(self.WV_search.text())

    def add_set(self, iterable, title=None, tpe=None):
        if len(iterable):
            if title:
                self.WL_attributes.addTopLevelItem(QTreeWidget_Separator(title))

            items = []
            for attr, attr_type in sorted(iterable, key=lambda x: x[0]):
                item = QTreeWidgetItem([attr])
                item.attrType = attr_type
                item.setData(0, Qt.UserRole, tpe)
                items.append(item)

            self.WL_attributes.addTopLevelItems(items)

    def filter(self, mask=''):
        self.WL_attributes.clear()

        obj_start = set([attr for attr in self.objs_attr if attr[0].startswith(mask)])
        obj_contains = obj_start.symmetric_difference(set([attr for attr in self.objs_attr if mask in attr[0]]))
        shp_start = set([attr for attr in self.shps_attr if attr[0].startswith(mask)])
        shp_contains = shp_start.symmetric_difference(set([attr for attr in self.shps_attr if mask in attr[0]]))

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
