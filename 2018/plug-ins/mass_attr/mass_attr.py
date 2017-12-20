"""
Massive Attribute Editor;
This tool simply wrap all the common attributes between the selected objects and display them in a list,
you can then filter this list and edit a given attribute for all the selection at the same time.

Version 2.0 currently handles :
        Float
        Integer
        Enum
        Bool
        Float 3
        Float 4
        Color
        String
    Version 2 includes filtering options,
     improved attributes' values controllers,
     deeper attribute search

More scripts at http://mehdilouala.com/scripts
"""

__author__ = "Mehdi Louala"
__copyright__ = "Copyright 2017, Mehdi Louala"
__credits__ = ["Mehdi Louala"]
__license__ = "GPL"
__version__ = "2.0.0"
__maintainer__ = "Mehdi Louala"
__email__ = "mlouala@gmail.com"
__status__ = "Stable Version"

from functools import partial
import re

from maya import cmds
from maya.OpenMaya import MEventMessage, MMessage
import maya.OpenMayaUI as om

try:
    from PySide.QtCore import Qt, QObject, Signal, QLocale
    from PySide.QtGui import QTreeWidgetItem, QDialog, QVBoxLayout, QPushButton, QLineEdit, QTreeWidget, QDoubleSpinBox, \
        QSpinBox, QComboBox, QCheckBox, QWidget, QHBoxLayout, QGroupBox, QColorDialog, QIcon, QLabel, QFont, QFrame, \
        QSlider, QApplication
    from shiboken import wrapInstance as wrapinstance
except ImportError:
    from PySide2.QtCore import Qt, QObject, Signal, QLocale
    from PySide2.QtGui import QIcon, QFont
    from PySide2.QtWidgets import QTreeWidgetItem, QDialog, QVBoxLayout, QPushButton, QLineEdit, QTreeWidget, \
        QDoubleSpinBox, QSpinBox, QComboBox, QCheckBox, QWidget, QGroupBox, QHBoxLayout, QLabel, QFrame, QSlider, \
        QApplication
    from shiboken2 import wrapInstance as wrapinstance


def get_maya_window():
    return wrapinstance(long(om.MQtUtil.mainWindow()), QWidget)


History, Shape, Object, Separator = range(4)


class QTreeWidget_Separator(QTreeWidgetItem):
    """
    Simple unselectable item acting as separator in list
    """
    def __init__(self, text='_______'):
        super(QTreeWidget_Separator, self).__init__()
        self.setText(0, text)
        self.setTextAlignment(0, Qt.AlignRight)
        self.setDisabled(True)


class Double3(QFrame):
    """
    A 3 slider Line for 3d arrays
    """
    valuesChanged = Signal(list)

    def __init__(self, parent=None):
        super(Double3, self).__init__(parent)

        self.x = QDoubleSpinBox()
        self.y = QDoubleSpinBox()
        self.z = QDoubleSpinBox()

        self.setLayout(line(self.x, self.y, self.z))
        # connecting all signals
        for elem in (self.x, self.y, self.z):
            elem.valueChanged.connect(self.element_value_changed)

    def element_value_changed(self):
        self.valuesChanged.emit([self.x.value(), self.y.value(), self.z.value()])

    def setValues(self, xyz):
        x, y, z = xyz
        self.x.setValue(x)
        self.y.setValue(y)
        self.z.setValue(z)


class Double4(Double3):
    """
    A 4 slider Line for 4d arrays (quaternion)
    """
    def __init__(self, parent=None):
        super(Double4, self).__init__(parent)
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
    """
    A simple widget to pick a color and replace the background's color of the button with the new
    selected color
    """
    colorChanged = Signal(list)

    def __init__(self, parent=None):
        super(ColorPicker, self).__init__(parent)
        self.setText('Pick color...')
        self.clicked.connect(self.get_color)

    def get_color(self):
        """
        Raise a QColorDialog and apply the color to the background color of the button
        """
        dial = QColorDialog()
        dial.setOptions(QColorDialog.DontUseNativeDialog)
        res = dial.exec_()

        if res:
            rgb = dial.currentColor().red(), dial.currentColor().green(), dial.currentColor().blue()
            self.setColor(rgb)
            rgb = [c / 255.0 for c in rgb]
            self.colorChanged.emit(rgb)

    def setColor(self, rgb=(255, 255, 255)):
        """
        Apply the given rgb to the background and switching the text color depending on color's value
        :param rgb: red green blue
        :type  rgb: tuple
        """
        r, g, b = rgb
        color = 'rgb({},{},{})'.format(r, g, b)
        fg = 'white' if sum([r, g, b]) < 255 else 'black'

        self.setStyleSheet('QPushButton{background-color:%s;color:%s;}' % (color, fg))
        self.update()


class NumericBox(QFrame):
    """
    A box with a spinner and a slider to allow easier value manipulation by user
    """
    valueChanged = Signal(float)
    spinner = QDoubleSpinBox
    step = 0.1

    def __init__(self, parent=None):
        super(NumericBox, self).__init__(parent)
        self.slider = QSlider(Qt.Horizontal)

        self.spinner = self.spinner()
        self.spinner.setSingleStep(self.step)

        self.slider.setTickInterval(self.step * 100)
        self.slider.setSingleStep(self.step * 100)

        self.slider.sliderMoved.connect(lambda x: self.spinner.setValue(x / 100))
        self.spinner.valueChanged.connect(self.applyValue)

        self.setLayout(line(self.slider, self.spinner))
        self.layout().setStretch(1, 0)

    def applyValue(self, value):
        self.valueChanged.emit(value)
        self.slider.setValue(value * 100)

    def setValue(self, value):
        self.spinner.setValue(value)
        self.slider.setValue(value * 100)

    def setRange(self, mini, maxi):
        self.spinner.setRange(mini, maxi)
        self.slider.setRange(mini * 100, maxi * 100)

    def value(self):
        return self.spinner.value()


class FloatBox(NumericBox):
    """
    Float case
    """
    spinner = QDoubleSpinBox
    step = 0.1

    def __init__(self, parent=None):
        super(FloatBox, self).__init__(parent)


class IntBox(NumericBox):
    """
    Integer case
    """
    spinner = QSpinBox
    step = 1

    def __init__(self, parent=None):
        super(IntBox, self).__init__(parent)


class Filter(QLineEdit):
    """
    Filter widget to display a little X button on the right of the field if ever something's inside
    """
    def __init__(self, *args):
        super(Filter, self).__init__(*args)
        self.textChanged.connect(self.isClean)

        self.clear_button = QPushButton('x', self)
        self.clear_button.setVisible(False)
        self.clear_button.setCursor(Qt.ArrowCursor)
        self.clear_button.clicked.connect(self.clear)

    def isClean(self, text):
        """ Check the emptyness of the field """
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
    """
    The main UI
    """
    class Applikator(QObject):
        """
        This is the core applier which toggle the display of the corresponding widget and handling events' connections
        """
        def __init__(self, parent=None):
            super(MassAttribute_UI.Applikator, self).__init__()
            self.root = parent

        def widget_event(self, t):
            """
            Return the correct widget's event depending on attribute's type
            :param t: the attribute's type
            :type  t: str
            :return: the event
            :rtype : Signal
            """
            return {'float': self.root.W_EDI_float.valueChanged, 'enum': self.root.W_EDI_enum.currentIndexChanged,
                    'int': self.root.W_EDI_int.valueChanged, 'bool': self.root.W_EDI_bool.stateChanged,
                    'str': self.root.W_EDI_str.textChanged, 'd3': self.root.W_EDI_d3.valuesChanged,
                    'd4': self.root.W_EDI_d4.valuesChanged, 'color': self.root.W_EDI_color.colorChanged}[t]

        def unset_editors(self):
            """
            Toggle off all editors and disconnect the current one
            """
            for widget in (self.root.W_EDI_float, self.root.W_EDI_int, self.root.W_EDI_enum,
                           self.root.W_EDI_bool, self.root.W_EDI_str, self.root.W_EDI_d3,
                           self.root.W_EDI_d4, self.root.W_EDI_color):
                widget.setVisible(False)

            # trying to force disconnection
            try:
                self.widget_event(self.root.ctx).disconnect(self.root.apply_value)
            except (KeyError, RuntimeError):
                pass

        def prepare(applier_name):
            """
            A decorator to prepare the attribute depending on type for the corresponding widget and getting the
            attribute's value
            :param applier_name: attribute's type
            :type  applier_name: str
            """
            def sub_wrapper(func):
                def wrapper(self, attr_path):
                    self.unset_editors()
                    self.root.ctx = applier_name
                    self.root.__getattribute__('W_EDI_%s' % applier_name).setVisible(True)
                    ret = func(self, cmds.getAttr(attr_path), attr_path)
                    return ret
                return wrapper
            return sub_wrapper

        @staticmethod
        def get_bounds(obj, attr, min_default, max_default):
            """
            Try to retrieve the range for the given attribute, if min or max fail it'll set default values
            :param         obj: the object's name
            :type          obj: str
            :param        attr: attribute's name
            :type         attr: str
            :param min_default: minimum default value
            :param max_default: max default value
            :type  min_default: float | int
            :type  max_default: float | int
            :return: minimum, maximum
            :rtype : tuple
            """
            try:
                assert cmds.attributeQuery(attr, n=obj, mxe=True)
                maxi = cmds.attributeQuery(attr, n=obj, max=True)[0]
            except (RuntimeError, AssertionError):
                maxi = max_default
            try:
                assert cmds.attributeQuery(attr, n=obj, mne=True)
                mini = cmds.attributeQuery(attr, n=obj, min=True)[0]
            except (RuntimeError, AssertionError):
                mini = min_default
            return mini, maxi

        @prepare('float')
        def apply_float(self, value, path):
            """
            Float attribute case
            :param value: attribute's value
            :param  path: attribute's path = obj.attr
            """
            obj, attr = path.split('.', 1)
            self.root.W_EDI_float.setRange(*self.get_bounds(obj, attr, -100.0, 100.0))
            self.root.W_EDI_float.setValue(value)

        @prepare('enum')
        def apply_enum(self, value, path):
            """Enum case"""
            self.root.W_EDI_enum.clear()
            obj, attr = path.split('.', 1)
            try:
                enums = [enum.split('=')[0] for enum in cmds.attributeQuery(attr, n=obj, listEnum=True)[0].split(':')]
            except RuntimeError:
                self.apply_int(path)
            else:
                self.root.W_EDI_enum.addItems(enums)
                self.root.W_EDI_enum.setCurrentIndex(enums.index(cmds.getAttr(path, asString=True)))

        @prepare('int')
        def apply_int(self, value, path):
            """Integer case"""
            obj, attr = path.split('.', 1)
            self.root.W_EDI_int.setRange(*self.get_bounds(obj, attr, -1000, 1000))
            self.root.W_EDI_int.setValue(value)

        @prepare('bool')
        def apply_bool(self, value, path):
            """Boolean case"""
            self.root.W_EDI_bool.setChecked(value)
            self.root.W_EDI_bool.setText(path.split('.', 1)[1])

        @prepare('str')
        def apply_str(self, value, path):
            """String case"""
            self.root.W_EDI_str.setText(value)

        @prepare('d3')
        def apply_d3(self, value, path):
            """3D array case"""
            self.root.W_EDI_d3.setValues(value[0])

        @prepare('d4')
        def apply_d4(self, value, path):
            """4D array case"""
            self.root.W_EDI_d4.setValues(value[0])

        @prepare('color')
        def apply_color(self, value, path):
            """Color case"""
            try:
                colors = value[0]
                self.root.W_EDI_color.setColor([int(c * 255) for c in colors])
            except TypeError:
                self.apply_int(value, path)

    class Attribute(str):
        """
        A custom string attribute class to ship more information into the string variable
        """
        def __new__(cls, path='', super_type=Object):
            obj, attr = path.split('.', 1)

            str_obj = str.__new__(cls, attr)

            str_obj.obj, str_obj.attr = obj, attr
            str_obj.path = path
            str_obj.super_type = super_type
            str_obj.type = None

            return str_obj

    # static variables to pre-load icons and attributes short names
    ctx_icons = {'float': QIcon(':render_decomposeMatrix.png'),
                 'enum': QIcon(':showLineNumbers.png'),
                 'bool': QIcon(':out_decomposeMatrix.png'),
                 'time': QIcon(':time.svg'),
                 'byte': QIcon(':out_defaultTextureList.png'),
                 'angle': QIcon(':angleDim.png'),
                 'string': QIcon(':text.png'),
                 'float3': QIcon(':animCurveTA.svg'),
                 'float4': QIcon(':animCurveTA.svg'),
                 'color': QIcon(':clampColors.svg')}

    for ctx in ('doubleLinear', 'double', 'long', 'short'):
        ctx_icons[ctx] = ctx_icons['float']

    ctx_icons['double3'] = ctx_icons['float3']
    ctx_icons['double4'] = ctx_icons['float4']

    ctx_wide = {'float': ('float', 'doubleLinear', 'double', 'long', 'short'),
                'enum': ('enum',),
                'bool': ('bool',),
                'time': ('time',),
                'byte': ('byte',),
                'angle': ('doubleAngle',),
                'string': ('string',),
                'float3': ('double3', 'float3'),
                'float4': ('double4', 'float4'),
                'color': ('color',)}

    def __init__(self, parent=None):
        super(MassAttribute_UI, self).__init__(parent)
        # Abstract
        self.applier = self.Applikator(self)
        self.selection = []
        self.callback = None
        self.ctx = None
        # storing found attributes' types to avoid double check
        self.solved = {}
        self.setLocale(QLocale.C)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_QuitOnClose)

        self.setFixedWidth(300)
        self.setWindowTitle('Massive Attribute Modifier')

        # UI
        L_main = QVBoxLayout()

        self.WV_title = QLabel('')
        self.WV_title.setVisible(False)
        self.WV_title.setFont(QFont('Verdana', 10))
        self.WV_title.setContentsMargins(0, 0, 0, 7)

        self.WB_select = QPushButton('Select')
        self.WB_select.setVisible(False)
        self.WB_select.setFixedWidth(50)
        self.WB_select.clicked.connect(lambda: cmds.select(self.selection))

        self.WB_update = QPushButton('Update')
        self.WB_update.setFixedWidth(50)
        self.WB_update.clicked.connect(lambda:self.update_attributes(cmds.ls(sl=True)))

        self.WV_search = Filter()
        self.WV_search.textChanged.connect(self.filter)

        self.WC_cases = QCheckBox('Case sensitive')
        self.WC_cases.stateChanged.connect(self.filter)

        self.WC_types = QCheckBox('Type filtering')

        self.WL_attrtype = QComboBox()
        self.WL_attrtype.setEnabled(False)

        for i, ctx in enumerate(sorted(self.ctx_wide)):
            self.WL_attrtype.addItem(ctx.title())
            self.WL_attrtype.setItemIcon(i, self.ctx_icons[ctx])

        L_attrtype = line(self.WC_types, self.WL_attrtype)

        self.WC_types.stateChanged.connect(partial(self.update_attributes, self.selection))
        self.WC_types.stateChanged.connect(self.WL_attrtype.setEnabled)
        self.WL_attrtype.currentIndexChanged.connect(self.filter)

        self.WC_liveu = QCheckBox('Live')
        self.WC_liveu.stateChanged.connect(self.WB_update.setDisabled)
        self.WC_liveu.stateChanged.connect(self.set_callback)

        self.WC_histo = QCheckBox('Load history')
        self.WC_histo.setChecked(True)
        self.WC_histo.stateChanged.connect(partial(self.update_attributes, self.selection))

        self.WC_child = QCheckBox('Children')
        self.WC_child.stateChanged.connect(partial(self.update_attributes, self.selection))

        options = group('Options', line(self.WC_cases, L_attrtype),
                        line(self.WC_child, self.WC_histo, self.WC_liveu, self.WB_update))
        options.layout().setSpacing(2)

        self.WL_attributes = QTreeWidget()
        self.WL_attributes.setStyleSheet('QTreeView {alternate-background-color: #1b1b1b;}')
        self.WL_attributes.setAlternatingRowColors(True)
        self.WL_attributes.setHeaderHidden(True)
        self.WL_attributes.setRootIsDecorated(False)

        self.objs_attr = set()
        self.shps_attr = set()

        self.W_EDI_float = FloatBox()
        self.W_EDI_int = IntBox()
        self.W_EDI_enum = QComboBox()
        self.W_EDI_bool = QCheckBox()
        self.W_EDI_str = QLineEdit()
        self.W_EDI_d3 = Double3()
        self.W_EDI_d4 = Double4()
        self.W_EDI_color = ColorPicker()

        # Final layout
        L_title = line(self.WV_title, self.WB_select)
        L_title.setStretch(0, 1)
        L_main.addLayout(L_title)
        L_main.setAlignment(Qt.AlignLeft)
        L_main.addWidget(self.WV_search)
        L_main.addWidget(options)
        L_main.addWidget(self.WL_attributes)
        L_edits = col(self.W_EDI_bool, self.W_EDI_int, self.W_EDI_float,
                      self.W_EDI_enum, self.W_EDI_str, self.W_EDI_d3, self.W_EDI_d4,
                      self.W_EDI_color)
        L_edits.setContentsMargins(0, 8, 0, 0)
        L_main.addLayout(L_edits)
        L_main.setStretch(3, 1)
        L_main.setSpacing(2)

        self.appliers = {'float': self.applier.apply_float,
                         'enum': self.applier.apply_enum,
                         'bool': self.applier.apply_bool,
                         'time': self.applier.apply_float,
                         'byte': self.applier.apply_int,
                         'angle': self.applier.apply_float,
                         'string': self.applier.apply_str,
                         'float3': self.applier.apply_d3,
                         'float4': self.applier.apply_d4,
                         'color': self.applier.apply_color}

        self.setLayout(L_main)

        # final settings
        self.WL_attributes.itemSelectionChanged.connect(self.update_setter)
        self.applier.unset_editors()

    def closeEvent(self, *args, **kwargs):
        self.set_callback(False)

    def set_callback(self, state):
        """
        Toggle selection event callback
        :param state: checkbox's state
        :type  state: bool | int
        """
        if state and not self.callback:
            self.callback = MEventMessage.addEventCallback('SelectionChanged', self.update_attributes)
            self.update_attributes(cmds.ls(sl=True))

        elif not state and self.callback:
            MMessage.removeCallback(self.callback)
            self.callback = None

    @staticmethod
    def format_title(nodes):
        """
        Extract the matching characters from a given nodes selection, if begin matches it will return "joint*" with a
        wildcard when names don't match
        :param nodes: objects' list
        :type  nodes: list | tuple
        :return: the formatted name with the corresponding characters
        :rtype : str
        """
        res = None

        if nodes:
            # we get the first node as a reference
            node = nodes[0]
            # and compare with the other nodes
            subs = [w for w in nodes if w != node]

            l = 1
            valid = True
            # will continue until l (length) match the full name's length or until names don't match
            while l < len(node) and valid:
                for sub in subs:
                    if not sub.startswith(node[:l]):
                        valid = False
                        break

                else:
                    l += 1

            # if matching characters isn't long enough we only display the number of nodes selected
            if l <= 3:
                res = '%i objects' % len(nodes)

            # otherwise showing matching pattern
            elif l < len(node) or len(nodes) > 1:
                res = node[:l - 1] + '* (%i objects)' % len(nodes)

            else:
                res = node

        return res

    @staticmethod
    def get_history(node):
        """
        Extract history for the given node
        :rtype: list
        """
        return cmds.listHistory(node, il=2, pdo=True) or []

    @staticmethod
    def get_shapes(node):
        """
        Extract shape(s) for the given node
        :rtype: list
        """
        return cmds.listRelatives(node, s=True, ni=True, f=True)

    def get_attributes_type(self, attrs):
        """
        For a given list of attributes of type Attribute, will loop through and fill the type parameter of the
         attribute with the corresponding type, if type is invalid or not handled, it'll remove it
        :param attrs: attributes' list
        :type  attrs: [MassAttribute_UI.Attribute]
        :return: cleaned and filled attributes' list
        :rtype: [MassAttribute_UI.Attribute]
        """
        attrs = list(attrs)
        # first we sort the attributes' list
        attrs.sort()

        # then we try to extract the attribute's type
        for i, attr in enumerate(attrs):
            try:
                if attr.attr in self.solved:
                    attr.type = self.solved[attr.attr]
                    raise RuntimeError
                tpe = cmds.getAttr(attr.path, typ=True)
                assert tpe
                attr.type = tpe
                self.solved[attr.attr] = tpe
            except (AssertionError, ValueError, RuntimeError):
                pass

        # defining a to-remove list
        rm_list = set()

        layers = {'3': 'XYZ', '4': 'XYZW'}
        for i, attr in enumerate(attrs):
            if i in rm_list:
                continue

            # we handle some special cases here, if ever the attribute list contains RGB and separate R, G and B we
            # assume it's a color, if it's a double3 or float3 and we find the corresponding XYZ, we remove then to
            # avoid duplicates

            if attr.endswith('RGB'):
                if '%sR' % attr[:-3] in attrs:
                    attr.type = 'color'
                    for chan in 'RGB':
                        rm_list.add(attrs.index('%s%s' % (attr[:-3], chan)))

            # if the attribute's type isn't in the list, we remove
            elif attr.type not in MassAttribute_UI.ctx_icons:
                rm_list.add(i)

            elif attr.endswith('R'):
                if '%sG' % attr[:-1] in attrs and attr[:-1] in attrs:
                    attr.type = 'color'
                    for chan in 'RGB':
                        rm_list.add(attrs.index('%s%s' % (attr[:-1], chan)))

            elif attr.type in ('double3', 'double4', 'float3', 'float4'):
                if '%sX' % attr in attrs:
                    for chan in layers[attr.type[-1]]:
                        rm_list.add(attrs.index('%s%s' % (attr, chan)))

        # finally cleaning the list
        for i in sorted(rm_list, reverse=True):
            attrs.pop(i)

        return attrs

    def apply_value(self, value):
        """
        When the value is modified in the UI, we forward the given value and applies to the object's
        :param value: attribute's value, mixed type
        :type  value: mixed
        """
        # We get the only selected object in list and get it's super type (Shape, History or Object) and
        # type (float, int, string)
        item = self.WL_attributes.selectedItems()[0]
        attr = item.attribute
        shape = attr.super_type == Shape
        histo = attr.super_type == History
        tpe = item.attribute.type

        # eq dict for each context
        value = {'bool': bool,
                 'int': int,
                 'float': float,
                 'enum': int,
                 'str': str,
                 'd3': list,
                 'd4': list,
                 'color': list}[self.ctx](value)

        # converting the selection into a set
        cmds.undoInfo(openChunk=True)
        targets = set(self.selection)

        # we propagate to children if 'Children' checkbox is on
        if self.WC_child.isChecked():
            for obj in list(targets):
                targets |= set(cmds.listRelatives(obj, ad=True))

        # if the target attribute is on the history, we add all selection's history to the list
        if histo:
            for obj in list(targets):
                targets.remove(obj)
                targets |= set(self.get_history(obj))

        # then we loop through target objects
        for obj in targets:
            # if the target is on the shape we get object's shape
            if shape and not histo:
                shapes = self.get_shapes(obj)

                if obj in shapes:
                    continue
                else:
                    obj = shapes[0]

            # then we try to apply depending on attribute's type
            try:
                correct_path = attr.path.replace(attr.obj, obj)

                if tpe == 'string':
                    cmds.setAttr(correct_path, value, type='string')

                elif tpe in ('double3', 'double4', 'float3', 'float4', 'color'):
                    cmds.setAttr(correct_path, *value, type='double%d' % len(value))

                else:
                    cmds.setAttr(correct_path, value)

            except RuntimeError:
                pass

        cmds.undoInfo(closeChunk=True)

    def update_setter(self):
        """
        When the list's selection changes we update the applier widget
        """
        item = self.WL_attributes.selectedItems()
        # abort if no item is selected
        if not len(item):
            return

        # getting attribute's parameter
        attr = item[0].attribute

        if len(self.selection):
            try:
                # looping until we find a context having the current attribute's type
                for applier in self.ctx_wide:
                    if attr.type in self.ctx_wide[applier]:
                        break
                # then we apply for the given path (obj.attribute)
                self.appliers[applier](attr.path)

                # and connecting event to the self.apply_value function
                self.applier.widget_event(self.ctx).connect(self.apply_value)

            # otherwise selection or type is invalid
            except IndexError:
                self.ctx = None

    def update_attributes(self, selection=None, *args):
        """
        Update the attributes for the given selection, looping through objects' attributes, finding attr in common
        between all objects then cleaning the lists, doing the same for shapes and / or histories
        :param selection: object's selection
        """
        # redefining lists as set to intersect union etc
        self.objs_attr = set()
        self.shps_attr = set()

        # pre init
        self.WL_attributes.clear()
        self.applier.unset_editors()

        self.selection = selection or (cmds.ls(sl=True) if self.WC_liveu.isChecked() else self.selection)

        self.WV_title.setText(self.format_title(self.selection))
        self.WV_title.setVisible(bool(len(self.selection)))
        self.WB_select.setVisible(bool(len(self.selection)))

        if not len(self.selection):
            return

        def get_usable_attrs(obj, super_type):
            """
            Small internal function to get a compatible attributes' list for the given object and assign the given
            super_type to it (Object, Shape or History)
            :param        obj: object's name
            :type         obj: str
            :param super_type: attribute's main type
            :type  super_type: Object | Shape | History
            :return:
            """
            return set([MassAttribute_UI.Attribute('%s.%s' % (obj, attr), super_type) for attr in
                        cmds.listAttr(obj, se=True, ro=False, m=True, w=True)])

        if len(self.selection):
            self.objs_attr = get_usable_attrs(self.selection[0], Object)

            # if we also want the object's history we add it to the initial set
            if self.WC_histo.isChecked():
                for histo in self.get_history(self.selection[0]):
                    self.objs_attr |= get_usable_attrs(histo, History)

            # filling the shape's set
            for shape in (self.get_shapes(self.selection[0]) or []):
                self.shps_attr |= get_usable_attrs(shape, Shape)

            # if selection's length bigger than one we compare by intersection with the other sets
            if len(self.selection) > 1:
                for obj in self.selection:
                    sub_attr = get_usable_attrs(obj, Object)

                    if self.WC_histo.isChecked():
                        for histo in self.get_history(obj):
                            sub_attr |= get_usable_attrs(histo, History)

                    self.objs_attr.intersection_update(sub_attr)

                    for shape in (self.get_shapes(self.selection[0]) or []):
                        self.shps_attr.intersection_update(get_usable_attrs(shape, Shape))

            # finally getting all intersecting attributes' types
            self.objs_attr = self.get_attributes_type(self.objs_attr)
            self.shps_attr = self.get_attributes_type(self.shps_attr)

        # and filtering the list
        self.filter()

    def add_set(self, iterable, title=None):
        """
        Adding the given iterable to the list with a first Separator object with given title
        :param iterable: list of item's attributes
        :param    title: Separator's name
        """
        if len(iterable):
            # if title is given we first add a Separator item to indicate coming list title
            if title:
                self.WL_attributes.addTopLevelItem(QTreeWidget_Separator(title))

            items = []
            for attr in sorted(iterable):
                item = QTreeWidgetItem([attr])
                # assigning the attribute itself inside a custom parameter
                item.attribute = attr
                items.append(item)

            # finally adding all the items to the list
            self.WL_attributes.addTopLevelItems(items)

    def filter(self):
        """
        Filter the list with UI's parameters, such as name or type filtering, etc
        """
        # pre cleaning
        self.WL_attributes.clear()

        # using regex compile to avoid re execution over many attributes
        mask = self.WV_search.text()
        case = 0 if self.WC_cases.isChecked() else re.IGNORECASE
        re_start = re.compile(r'^%s.*?' % mask, case)
        re_cont = re.compile(r'.*?%s.*?' % mask, case)

        # getting the four different lists
        obj_start = set([at for at in self.objs_attr if re_start.search(at)])
        shp_start = set([at for at in self.shps_attr if re_start.search(at)])

        # if type filtering is one we only extract the wanted attribute's type
        if self.WC_types.isChecked():
            obj_start = set([at for at in obj_start if
                             at.type in self.ctx_wide[self.WL_attrtype.currentText().lower()]])
            shp_start = set([at for at in shp_start if
                             at.type in self.ctx_wide[self.WL_attrtype.currentText().lower()]])

        # finally adding the current sets if there is a mask we add the also the containing matches
        if mask:
            # getting contains filtering and type containers filtering
            obj_contains = obj_start.symmetric_difference(set([at for at in self.objs_attr if re_cont.search(at)]))
            shp_contains = shp_start.symmetric_difference(set([at for at in self.shps_attr if re_cont.search(at)]))
            if self.WC_types.isChecked():
                obj_contains = set([at for at in obj_contains if
                                    at.type in self.ctx_wide[self.WL_attrtype.currentText().lower()]])
                shp_contains = set([at for at in shp_contains if
                                    at.type in self.ctx_wide[self.WL_attrtype.currentText().lower()]])

            # adding the sets
            self.add_set(obj_start, 'Obj attributes starting with')
            self.add_set(obj_contains, 'Obj attributes containing')
            self.add_set(shp_start, 'Shape attributes starting with')
            self.add_set(shp_contains, 'Shape attributes containing')

        else:
            self.add_set(obj_start, 'Object\'s attributes')
            self.add_set(shp_start, 'Shape\'s attributes')

        # and we select the first one if ever there is something in the list
        if self.WL_attributes.topLevelItemCount():
            self.WL_attributes.setItemSelected(self.WL_attributes.topLevelItem(1), True)


def Display_Massive_Toggle():
    """ Display function """
    Mass_Win = MassAttribute_UI(get_maya_window())
    Mass_Win.show()
    return Mass_Win
