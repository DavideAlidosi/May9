from PySide import QtCore, QtGui
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.mel as mel
import shiboken
import MMtoKey
import os
import re


MAYA_WINDOW = shiboken.wrapInstance(long(omui.MQtUtil.mainWindow()), QtGui.QWidget)
VERSION = '1.0.4'


class Button(QtGui.QLabel):
    def __init__(self, parent, geo, style, execute):
        QtGui.QLabel.__init__(self, parent)
        self.setGeometry(*geo)
        self.STYLE = style
        self.EXECUTE = execute
        self.setAlignment(self.STYLE.ALIGN)
        self.setStyleSheet(self.STYLE.LEAVE_EVENT)
        self.show()

    def enterEvent(self, *args, **kwargs):
        self.setStyleSheet(self.STYLE.ENTER_EVENT)

    def leaveEvent(self, *args, **kwargs):
        self.setStyleSheet(self.STYLE.LEAVE_EVENT)

    def mousePressEvent(self, QMouseEvent):
        self.setStyleSheet(self.STYLE.PRESS_EVENT)

    def mouseReleaseEvent(self, QMouseEvent):
        self.setStyleSheet(self.STYLE.RELEASE_EVENT)


class TextButtonFlat(Button):
    def __init__(self, parent, geo, style, execute, text):
        Button.__init__(self, parent, geo, style, execute)
        self.setText(self.STYLE.TEXT_FORMAT % text)

    def mousePressEvent(self, QMouseEvent):
        self.setStyleSheet(self.STYLE.PRESS_EVENT)
        if self.EXECUTE:
            self.EXECUTE()


class TextLeverFlat(Button):
    def __init__(self, parent, geo, style, execute, text_list, values_list):
        Button.__init__(self, parent, geo, style, execute)
        self.index = 0
        self.TEXT_LIST = tuple(text_list)
        self.VALUES_LIST = values_list
        self.setText(self.STYLE.TEXT_FORMAT % self.TEXT_LIST[self.index])

    def mousePressEvent(self, QMouseEvent):
        self.setStyleSheet(self.STYLE.PRESS_EVENT)
        self.index = (self.index + 1) % len(self.TEXT_LIST)
        self.setText(self.STYLE.TEXT_FORMAT % self.TEXT_LIST[self.index])
        if self.EXECUTE:
            self.EXECUTE(self.VALUES_LIST[self.index])

    def getValue(self, index=None):
        return self.VALUES_LIST[self.index] if not index else self.VALUES_LIST[index]

    def setValue(self, value):
        self.index = value % len(self.TEXT_LIST)
        self.setText(self.STYLE.TEXT_FORMAT % self.TEXT_LIST[self.index])


class Text(QtGui.QLabel):
    def __init__(self, parent, geo, style, text):
        QtGui.QLabel.__init__(self, parent)
        self.setGeometry(*geo)
        self.setAlignment(style.ALIGN)
        self.setStyleSheet(style.LEAVE_EVENT)
        self.setText(style.TEXT_FORMAT % text)


class SpinBox(QtGui.QSpinBox):
    def __init__(self, parent, geo, value, maximum, minimum, step):
        QtGui.QSpinBox.__init__(self, parent)
        self.setGeometry(*geo)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)
        self.setSingleStep(step)


class Style(object):
    PRESS_EVENT = 'background-color: rgb(110, 110, 110); border-radius: 3px;'
    RELEASE_EVENT = 'background-color: rgb(80, 80, 80); border-radius: 3px;'
    ENTER_EVENT = 'background-color: rgb(80, 80, 80); border-radius: 3px;'
    LEAVE_EVENT = 'background-color: transparent; border-radius: 3px;'
    ALIGN = QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
    TEXT_FORMAT = '<b><font size=3>%s</font></b>'

    def __init__(self, **kwargs):
        for key in kwargs:
            self.__setattr__(key, kwargs[key])


class WidgetBase(QtGui.QWidget):
    PREFIX = ''
    NODE = MMtoKey.Node
    IS_PANELS = False

    def __init__(self, data, mmtokey):
        QtGui.QWidget.__init__(self)
        self.DATA = data
        self.ENGINE = mmtokey
        self.setFixedSize(380, 265)
        y = 50 * (not self.IS_PANELS)
        # left side
        self.ui_ls_node = QtGui.QListWidget(self)
        self.ui_ls_node.setGeometry(5, 5, 180, 180 + y)
        self.ui_btn_add = TextButtonFlat(self, (5, 190 + y, 60, 20), Style, self._addNode, 'add')
        self.ui_btn_remove = TextButtonFlat(self, (65, 190 + y, 60, 20), Style, self._removeNode, 'remove')
        self.ui_btn_break = TextButtonFlat(self, (125, 190 + y, 60, 20), Style, self._breakNode, 'break')
        if self.IS_PANELS:
            self.ui_cmb_keys = QtGui.QComboBox(self)
            self.ui_cmb_keys.setGeometry(5, 215, 120, 20)
            self.ui_cmb_keys.addItems(['none', 'dag', 'non-dag', 'non-dag, dag', 'name', 'name, dag', 'name, non-dag',
                                       'name, non-dag, dag'])
            self.connect(self.ui_cmb_keys, QtCore.SIGNAL('currentIndexChanged(int)'), self._changeSearchNode)
            self.ui_cmb_names = QtGui.QComboBox(self)
            self.ui_cmb_names.setGeometry(5, 240, 120, 20)
            self.ui_cmb_names.addItems(['names none', 'names prefix', 'names suffix', 'names any', 'names absolute'])
            self.connect(self.ui_cmb_names, QtCore.SIGNAL('currentIndexChanged(int)'), self._changeSearchNames)
            self.ui_btn_all1 = TextButtonFlat(self, (130, 215, 55, 20), Style, self._changeSearchNodeAll, 'to all')
            self.ui_btn_all2 = TextButtonFlat(self, (130, 240, 55, 20), Style, self._changeSearchNamesAll, 'to all')
        # right side. bodies
        ui_wdg_bottom_0 = QtGui.QWidget()
        ui_wdg_bottom_0.setMinimumHeight(1)
        ui_wdg_bottom_1 = QtGui.QWidget()
        ui_wdg_bottom_1.setFixedSize(185, 24)
        ui_wdg_bottom_1.setMinimumHeight(24)
        ui_vbox_column = QtGui.QVBoxLayout(ui_wdg_bottom_0)
        ui_vbox_column.setContentsMargins(0, 0, 0, 0)
        ui_vbox_column.setSpacing(0)
        # right top
        self.ui_ls_menu = QtGui.QListWidget(ui_wdg_bottom_0)
        self.ui_ls_menu.setMinimumHeight(1)
        # right bottom
        self.ui_txt_command = QtGui.QTextEdit()
        self.ui_btn_language = TextLeverFlat(ui_wdg_bottom_1, (2, 2, 60, 20), Style, self._changeLanguage,
                                             ('mel', 'python'), (0, 1))
        self.ui_btn_save = TextButtonFlat(ui_wdg_bottom_1, (64, 2, 60, 20), Style, self._changeCommand, 'save')
        ui_vbox_column.addWidget(self.ui_txt_command)
        ui_vbox_column.addWidget(ui_wdg_bottom_1)
        # divider
        self.ui_divide = QtGui.QSplitter(self)
        self.ui_divide.setOrientation(QtCore.Qt.Vertical)
        self.ui_divide.setGeometry(190, 5, 185, 255)
        self.ui_divide.addWidget(self.ui_ls_menu)
        self.ui_divide.addWidget(ui_wdg_bottom_0)

        self.connect(self.ui_ls_node, QtCore.SIGNAL('currentRowChanged(int)'), self._changeNode)
        self.connect(self.ui_ls_menu, QtCore.SIGNAL('currentRowChanged(int)'), self._changeMenu)
        self.updateInterface()

    def updateInterface(self):
        self.ui_ls_node.clear()
        self.ui_ls_menu.clear()
        self.ui_ls_node.addItems(sorted(self.DATA.keys()))
        self.ui_ls_menu.addItems([x.replace('menu_', '') for x in os.listdir(cmds.internalVar(umm=True))])
        self._lockUI()

    def _lockUI(self):
        if not self.DATA:
            self.ui_ls_menu.setCurrentItem(None)
            self.ui_divide.setDisabled(True)
            self.ui_txt_command.setText('')
            if self.IS_PANELS:
                self.ui_cmb_keys.setDisabled(True)
                self.ui_cmb_names.setDisabled(True)
        else:
            self.ui_divide.setEnabled(True)
            if self.IS_PANELS:
                self.ui_cmb_keys.setEnabled(True)
                self.ui_cmb_names.setEnabled(True)

    def _addNodeName(self, name):
        if name in self.DATA or not name or len(self.DATA) == 0xff:
            return
        self.DATA[name] = self.NODE()
        self.ui_ls_node.addItems([name])
        self._lockUI()

    def _addNode(self):
        pass

    def _removeNode(self):
        item_node = self.ui_ls_node.currentItem()
        if not item_node:
            return
        else:
            name = str(item_node.text())
        self.ui_ls_node.takeItem(self.ui_ls_node.currentRow())
        self.DATA.pop(name)
        self._lockUI()
    
    def _breakNode(self):
        item_node = self.ui_ls_node.currentItem()
        if not item_node:
            return
        else:
            name = str(item_node.text())
            node = self.DATA[name]
        node.menu = ''
        self.ui_ls_menu.setCurrentItem(None)

    def _changeNode(self):
        item_node = self.ui_ls_node.currentItem()
        if not item_node:
            return
        else:
            name = str(item_node.text())
            node = self.DATA[name]
        item_menu = self.ui_ls_menu.findItems(node.menu, QtCore.Qt.MatchExactly)
        if item_menu:
            self.ui_ls_menu.setCurrentItem(item_menu[0])
        else:
            self.ui_ls_menu.setCurrentItem(None)
        language, command = node.getCommand()
        self.ui_btn_language.setValue(language)
        self.ui_txt_command.setText(command)
        if self.IS_PANELS:
            self.ui_cmb_keys.setCurrentIndex(node.search)
            self.ui_cmb_names.setCurrentIndex(node.names)

    def _changeMenu(self):
        item_node = self.ui_ls_node.currentItem()
        if not item_node:
            return
        else:
            self._lockUI()
            name = str(item_node.text())
            node = self.DATA[name]
        item_menu = self.ui_ls_menu.currentItem()
        if item_menu:
            node.menu = str(item_menu.text())
        else:
            node.menu = ''

    def _changeSearchNode(self):
        item_node = self.ui_ls_node.currentItem()
        if not item_node:
            return
        else:
            name = str(item_node.text())
            node = self.DATA[name]
        node.search = self.ui_cmb_keys.currentIndex()

    def _changeSearchNodeAll(self):
        for node in self.DATA.values():
            node.search = self.ui_cmb_keys.currentIndex()

    def _changeSearchNames(self):
        item_node = self.ui_ls_node.currentItem()
        if not item_node:
            return
        else:
            name = str(item_node.text())
            node = self.DATA[name]
        node.names = self.ui_cmb_names.currentIndex()

    def _changeSearchNamesAll(self):
        for node in self.DATA.values():
            node.names = self.ui_cmb_names.currentIndex()

    def _changeCommand(self):
        item_node = self.ui_ls_node.currentItem()
        if not item_node:
            return
        else:
            name = str(item_node.text())
            node = self.DATA[name]
        command = self.ui_txt_command.toPlainText()
        save = self.ENGINE.pref_save_file
        if (save == 0 and len(command) > 0xff) or (save == 1 and '\n' in command) or save == 2:
            script = open('%s/scripts/%s_%s.script' % (self.ENGINE.PATH, self.PREFIX, name), 'w')
            script.write(command)
            script.close()
            node.setCommand('%s_%s' % (self.PREFIX, name), self.ui_btn_language.getValue(), 1)
        else:
            node.setCommand(command, self.ui_btn_language.getValue(), 0)
            if os.path.isfile('%s/scripts/%s_%s.script' % (self.ENGINE.PATH, self.PREFIX, name)):
                os.remove('%s/scripts/%s_%s.script' % (self.ENGINE.PATH, self.PREFIX, name))

    def _changeLanguage(self, value):
        item_node = self.ui_ls_node.currentItem()
        if not item_node:
            return
        else:
            name = str(item_node.text())
            node = self.DATA[name]
        node.language = value


class WidgetPanel(WidgetBase):
    PREFIX = 'panel'
    NODE = MMtoKey.PanelNode
    IS_PANELS = True

    def _addNode(self):
        cmds.warning('panel under pointer is "%s"' % cmds.getPanel(up=True))
        self._addNodeName(raw_input().replace(' ', ''))


class WidgetName(WidgetBase):
    PREFIX = 'name'

    def _addNode(self):
        self._addNodeName(raw_input().replace(' ', ''))


class WidgetNonDag(WidgetBase):
    PREFIX = 'nondag'

    def _addNode(self):
        keys = self.ENGINE.findNonDagKey()
        self._addNodeName(' '.join(keys))


class WidgetDag(WidgetBase):
    PREFIX = 'dag'

    def _addNode(self):
        keys = self.ENGINE.findDagKey()
        self._addNodeName(' '.join(keys))


class WidgetTool(WidgetBase):
    PREFIX = 'tool'

    def __init__(self, *args):
        WidgetBase.__init__(self, *args)
        self.ui_ls_menu.setParent(self)
        self.ui_divide.setParent(None)
        self.ui_ls_menu.setGeometry(190, 5, 185, 255)

    def _addNode(self):
        context = cmds.currentCtx()
        cmds.contextInfo(context, title=True)
        self._addNodeName(context)

    def _lockUI(self):
        if not self.DATA:
            self.ui_ls_menu.setDisabled(True)
            self.ui_ls_menu.setCurrentItem(None)
        else:
            self.ui_ls_menu.setEnabled(True)


class WidgetPreset(WidgetBase):
    PREFIX = 'preset'

    def _addNode(self):
        self._addNodeName(raw_input())


class MainWindow(QtGui.QMainWindow):
    def __init__(self, mmtokey):
        QtGui.QMainWindow.__init__(self, MAYA_WINDOW)
        self.ENGINE = mmtokey
        self.setFixedSize(380, 305)
        if cmds.window('MMtoKeyUI', ex=True):
            cmds.deleteUI('MMtoKeyUI')
        if cmds.window('MMtoKeyPreferences', ex=True):
            cmds.deleteUI('MMtoKeyPreferences')
        if cmds.window('MMtoKeyAbout', ex=True):
            cmds.deleteUI('MMtoKeyAbout')
        self.setObjectName('MMtoKeyUI')
        self.setWindowTitle('MMtoKey %s' % VERSION)

        self.ui_tab_widgets = QtGui.QTabWidget(self)
        self.ui_tab_widgets.setGeometry(0, 20, 380, 285)
        self.ui_tab_widgets.setDocumentMode(True)
        self.ui_tab_widgets.addTab(WidgetPanel(mmtokey.DATA_PANEL, mmtokey), 'panel')
        self.ui_tab_widgets.addTab(WidgetName(mmtokey.DATA_NAME, mmtokey), 'name')
        self.ui_tab_widgets.addTab(WidgetNonDag(mmtokey.DATA_NONDAG, mmtokey), 'nondag')
        self.ui_tab_widgets.addTab(WidgetDag(mmtokey.DATA_DAG, mmtokey), 'dag')
        self.ui_tab_widgets.addTab(WidgetTool(mmtokey.DATA_TOOL, mmtokey), 'tool')
        self.ui_tab_widgets.addTab(WidgetPreset(mmtokey.DATA_PRESET, mmtokey), 'preset')

        menu_file = QtGui.QMenu('file')
        menu_file.addAction('save', self.ENGINE.saveNodes)
        menu_file.addAction('update', self._updateInterface)
        menu_file.addAction('preferences', self._preferences)
        self.menuBar().addMenu(menu_file)
        menu_tools = QtGui.QMenu('tools')
        menu_tools.addAction('marking menu editor', self._markingMenuEditor)
        menu_tools.addAction('marking menu language', ChangeLanguage)
        menu_tools.addAction('hotkey maker', HotkeyMaker)
        self.menuBar().addMenu(menu_tools)
        self.menuBar().addAction('about', About)
        self.show()

    def _updateInterface(self):
        for i in xrange(6):
            self.ui_tab_widgets.widget(i).updateInterface()

    def _preferences(self):
        Preferences(self.ENGINE)

    @staticmethod
    def _markingMenuEditor():
        mel.eval('menuEditorWnd;')


class Preferences(QtGui.QMainWindow):
    def __init__(self, mmtokey):
        QtGui.QMainWindow.__init__(self, MAYA_WINDOW)
        if cmds.window('MMtoKeyPreferences', ex=True):
            cmds.deleteUI('MMtoKeyPreferences')
        self.setObjectName('MMtoKeyPreferences')
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setWindowTitle('MMtoKey preferences')
        self.setFixedSize(210, 345)
        self.ENGINE = mmtokey
        Text(self, (10, 10, 190, 20), Style, 'save no-click command as .script file:')
        Text(self, (0, 55, 210, 20), Style, 'LMB (selected) special marking menu')
        Text(self, (0, 100, 210, 20), Style, 'MMB (tools) special marking menu')
        Text(self, (80, 270, 120, 20), Style, 'HUD section')
        Text(self, (80, 295, 120, 20), Style, 'HUD block')
        self.ui_cmb_files = QtGui.QComboBox(self)
        self.ui_cmb_files.setGeometry(10, 30, 190, 20)
        self.ui_cmb_files.addItems(['long only', 'more one line in script', 'always'])
        self.ui_cmb_files.setCurrentIndex(mmtokey.pref_save_file)
        self.ui_txt_special_0 = QtGui.QLineEdit(self)
        self.ui_txt_special_0.setGeometry(10, 75, 190, 20)
        self.ui_txt_special_0.setText(mmtokey.pref_special_0)
        self.ui_txt_special_1 = QtGui.QLineEdit(self)
        self.ui_txt_special_1.setGeometry(10, 120, 190, 20)
        self.ui_txt_special_1.setText(mmtokey.pref_special_1)
        self.ui_chb_sameDag = QtGui.QCheckBox('two same dag nodes', self)
        self.ui_chb_sameDag.setGeometry(10, 145, 190, 20)
        self.ui_chb_sameDag.setChecked(mmtokey.pref_same_dag)
        self.ui_chb_sameNonDag = QtGui.QCheckBox('two same non-dag nodes', self)
        self.ui_chb_sameNonDag.setGeometry(10, 170, 190, 20)
        self.ui_chb_sameNonDag.setChecked(mmtokey.pref_same_nondag)
        self.ui_chb_errors = QtGui.QCheckBox('remove obsolete .script files', self)
        self.ui_chb_errors.setGeometry(10, 195, 190, 20)
        self.ui_chb_errors.setChecked(mmtokey.pref_check_errors)
        self.ui_chb_radial = QtGui.QCheckBox('radial menu in presets select', self)
        self.ui_chb_radial.setGeometry(10, 220, 190, 20)
        self.ui_chb_radial.setChecked(mmtokey.pref_preset_radial)
        self.ui_chb_hud = QtGui.QCheckBox('heads-up for selected preset', self)
        self.ui_chb_hud.setGeometry(10, 245, 190, 20)
        self.ui_chb_hud.setChecked(mmtokey.pref_hud)
        self.ui_spn_section = SpinBox(self, (10, 270, 60, 20), mmtokey.pref_hud_x, 9, 0, 1)
        self.ui_spn_block = SpinBox(self, (10, 295, 60, 20), mmtokey.pref_hud_y, 9, 0, 1)
        TextButtonFlat(self, (140, 320, 60, 20), Style, self._savePreferences, 'save')
        self.show()

    def _savePreferences(self):
        self.ENGINE.pref_save_file = self.ui_cmb_files.currentIndex()
        self.ENGINE.pref_special_0 = self.ui_txt_special_0.text()
        self.ENGINE.pref_special_1 = self.ui_txt_special_1.text()
        self.ENGINE.pref_same_nondag = self.ui_chb_sameNonDag.isChecked()
        self.ENGINE.pref_same_dag = self.ui_chb_sameDag.isChecked()
        self.ENGINE.pref_check_errors = self.ui_chb_errors.isChecked()
        self.ENGINE.pref_hud = self.ui_chb_hud.isChecked()
        self.ENGINE.pref_hud_x = self.ui_spn_section.value()
        self.ENGINE.pref_hud_y = self.ui_spn_block.value()
        self.ENGINE.pref_preset_radial = self.ui_chb_radial.isChecked()


class About(QtGui.QMainWindow):
    def __init__(self, *args):
        QtGui.QMainWindow.__init__(self, MAYA_WINDOW)
        self.setFixedSize(160, 130)
        self.setWindowTitle('About')
        self.setWindowFlags(QtCore.Qt.Tool)
        if cmds.window('MMtoKeyAbout', ex=True):
            cmds.deleteUI('MMtoKeyAbout')
        self.setObjectName('MMtoKeyAbout')
        ui_text = QtGui.QLabel('MMtoKey\nv%s\n\n\nMenshikov Andrey\nDavide Alidosi, 2016' % VERSION, self)
        ui_text.setGeometry(10, 10, 140, 80)
        ui_btn = QtGui.QPushButton('OK', self)
        ui_btn.setGeometry(40, 100, 75, 20)
        self.connect(ui_btn, QtCore.SIGNAL('clicked()'), self.close)
        self.show()

    def close(self):
        cmds.deleteUI('MMtoKeyAbout')


class HotkeyMaker(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self, MAYA_WINDOW)
        if cmds.window('MMtoKeyHotkey', exists=True):
            cmds.deleteUI('MMtoKeyHotkey')
        dialog = cmds.confirmDialog(m='what hotkey to create?', b=['select based', 'preset based'])
        self.SELECT = 1 if dialog == 'select based' else 0
        y = 110 * self.SELECT
        self.setObjectName('MMtoKeyHotkey')
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setWindowTitle('MMtoKey Hotkey Maker')
        self.setFixedSize(200, 140 + y)
        Text(self, (10, 10, 180, 20), Style, 'hotkey name')
        Text(self, (10, 80 + y, 120, 20), Style, 'hotkey')
        if self.SELECT:
            Text(self, (10, 50, 180, 20), Style, 'certain menu (optional)')
            Text(self, (10, 90, 180, 20), Style, 'certain command (optional)')
            Text(self, (10, 140, 120, 20), Style, 'command language')
        self.ui_txt_name = QtGui.QLineEdit(self)
        self.ui_txt_name.setGeometry(10, 30, 180, 20)
        self.ui_txt_menu = QtGui.QLineEdit(self)
        self.ui_txt_menu.setGeometry(10, 70, 180, 20)
        self.ui_txt_command = QtGui.QLineEdit(self)
        self.ui_txt_command.setGeometry(10, 110, 180, 20)
        self.ui_txt_hotkey = QtGui.QLineEdit(self)
        self.ui_txt_hotkey.setGeometry(130, 80 + y, 60, 20)
        self.ui_txt_hotkey.setMaxLength(1)
        self.ui_cmb_language = QtGui.QComboBox(self)
        self.ui_cmb_language.setGeometry(130, 140, 60, 20)
        self.ui_cmb_language.addItems(['mel', 'python'])
        self.ui_txt_menu.setVisible(self.SELECT)
        self.ui_txt_command.setVisible(self.SELECT)
        self.ui_cmb_language.setVisible(self.SELECT)
        self.ui_chb_ctrl = QtGui.QCheckBox('ctrl', self)
        self.ui_chb_ctrl.setGeometry(10, 55 + y, 60, 20)
        self.ui_chb_alt = QtGui.QCheckBox('alt', self)
        self.ui_chb_alt.setGeometry(70, 55 + y, 60, 20)
        self.ui_chb_shift = QtGui.QCheckBox('shift', self)
        self.ui_chb_shift.setGeometry(130, 55 + y, 60, 20)
        TextButtonFlat(self, (130, 110 + y, 60, 20), Style, self._createHotkey, 'create')
        self.show()

    def _createHotkey(self):
        if cmds.runTimeCommand('%s_press' % self.ui_txt_name.text(), exists=True):
            if cmds.confirmDialog(m='name is not unique! replace?', b=['yes', 'no']) == 'no':
                return
            else:
                cmds.runTimeCommand('%s_press' % self.ui_txt_name.text(), delete=True, e=True)
                cmds.runTimeCommand('%s_release' % self.ui_txt_name.text(), delete=True, e=True)
        name = self.ui_txt_name.text()
        menu = self.ui_txt_menu.text()
        command = self.ui_txt_command.text()
        hotkey = self.ui_txt_hotkey.text().lower()
        if not hotkey:
            return
        ctrl = self.ui_chb_ctrl.isChecked()
        alt = self.ui_chb_alt.isChecked()
        shift = self.ui_chb_shift.isChecked()
        press = "MMtoKey.press_%i(%s, %s, %s, '%s')" % (self.SELECT, ctrl,  alt, shift, menu)
        release = "MMtoKey.release_%i('%s', %i)" % (self.SELECT, command, self.ui_cmb_language.currentIndex())
        cmds.runTimeCommand('%s_press' % name, c=press, category='MMtoKey', cl='python')
        cmds.runTimeCommand('%s_release' % name, c=release, category='MMtoKey', cl='python')
        cmds.nameCommand('%s_PressNameCommand' % name, annotation='%s_press' % name, command='%s_press' % name)
        cmds.nameCommand('%s_ReleaseNameCommand' % name, annotation='%s_release' % name, command='%s_release' % name)
        try:
            cmds.hotkey(k=hotkey, name='%s_PressNameCommand' % name, releaseName='%s_ReleaseNameCommand' % name,
                        ctl=ctrl, alt=alt, sht=shift)
        except TypeError:
            cmds.hotkey(k=hotkey, name='%s_PressNameCommand' % name, releaseName='%s_ReleaseNameCommand' % name,
                        ctl=ctrl, alt=alt)
        cmds.warning('hotkey created')


class MenuItem(QtGui.QListWidgetItem):
    NOT_INCLUDE = False

    def __init__(self, lines):
        QtGui.QListWidgetItem.__init__(self)
        self.TEXT = lines
        self.LANGUAGE = [-1, 'mel']
        self.COMMAND = [-1, '']
        self.ICON = ''
        self.LABEL = ''

    def lookThrow(self, i):
        while '-' in self.TEXT[i]:
            if '-label ' in self.TEXT[i]:
                self.LABEL = re.match('(.*)-label "(.*)"(.*)', self.TEXT[i]).group(2)
            elif '-command ' in self.TEXT[i]:
                self.COMMAND = [i, re.match('(.*)-command "(.*)"(.*)', self.TEXT[i]).group(2)]
            elif '-sourceType ' in self.TEXT[i]:
                self.LANGUAGE = [i, re.match('(.*)-sourceType "(.*)"(.*)', self.TEXT[i]).group(2)]
            elif '-image ' in self.TEXT[i]:
                self.ICON = re.match('(.*)-image "(.*)"(.*)', self.TEXT[i]).group(2)
            elif '-subMenu 1' in self.TEXT[i] or '-optionBox 1' in self.TEXT[i]:
                self.NOT_INCLUDE = True
            i += 1
        self.setText(self.LABEL)
        return i

    def getCommand(self):
        return self.COMMAND[1].replace('\\"', '"').replace('\\n', '\n')

    def setCommand(self, command):
        command = command.replace('"', '\\"').replace('\n', '\\n')
        text = self.TEXT[self.COMMAND[0]]
        self.TEXT[self.COMMAND[0]] = text.replace(self.COMMAND[1], command)
        self.COMMAND[1] = command

    def getLanguage(self):
        return 0 if self.LANGUAGE[1] == 'mel' else 1

    def setLanguage(self, language):
        language = 'mel' if language == 0 else 'python'
        text = self.TEXT[self.LANGUAGE[0]]
        self.TEXT[self.LANGUAGE[0]] = text.replace(self.LANGUAGE[1], language)
        self.LANGUAGE[1] = language


class ChangeLanguage(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self, MAYA_WINDOW)
        if cmds.window('MMtoKeyPyUI', ex=True):
            cmds.deleteUI('MMtoKeyPyUI')
        if cmds.control('MMtoKeyPyIconWidget', ex=True):
            cmds.deleteUI('MMtoKeyPyIconWidget')
        self.setFixedSize(350, 220)
        self.setWindowTitle('Marking Menu change language')
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setObjectName('MMtoKeyPyUI')
        self.ui_combobox = QtGui.QComboBox(self)
        self.ui_combobox.setGeometry(180, 30, 80, 20)
        self.ui_combobox.addItems(['mel', 'python'])
        self.ui_listwidget = QtGui.QListWidget(self)
        self.ui_listwidget.setGeometry(10, 30, 160, 180)
        self.ui_listwidget.setSelectionMode(QtGui.QListWidget.ExtendedSelection)
        self.ui_textedit = QtGui.QTextEdit(self)
        self.ui_textedit.setGeometry(180, 100, 160, 110)
        self.ui_textedit.setEnabled(False)
        self.ui_textedit.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.widget = QtGui.QWidget(self)
        self.widget.setGeometry(180, 60, 32, 32)
        self.ui_vbox = QtGui.QVBoxLayout(self.widget)
        self.ui_vbox.setContentsMargins(0, 0, 0, 0)
        self.ui_vbox.setSpacing(0)
        self.ui_vbox.setObjectName('MMtoKeyPyIcon')
        self.ui_button = TextButtonFlat(self, (220, 60, 120, 30), Style, self._saveCommand, 'save command')
        self.ui_button.setEnabled(False)
        cmds.image('MMtoKeyPyIconWidget', p='MMtoKeyPyIcon')
        self.connect(self.ui_listwidget, QtCore.SIGNAL('itemSelectionChanged()'), self._updateCommand)
        self.connect(self.ui_combobox, QtCore.SIGNAL('currentIndexChanged(int)'), self._updateLanguage)
        self.menuBar().addAction('open', self._selectMarkingMenu)
        self.menuBar().addAction('save', self._saveMarkingMenu)
        self.textblock = None
        self.fileread = None
        self.show()

    def _saveCommand(self):
        self.ui_listwidget.currentItem().setCommand(self.ui_textedit.toPlainText())

    def _selectMarkingMenu(self):
        fileread = cmds.fileDialog2(fm=1, ff='menu_*.mel', dir=cmds.internalVar(umm=True), cap='open Marking Menu')[0]
        self.ui_listwidget.clear()
        self.ui_listwidget.setCurrentRow(-1)
        self.ui_textedit.setText('')
        self.ui_button.setEnabled(False)
        cmds.image('MMtoKeyPyIconWidget', e=True, vis=False)
        self.fileread = fileread
        with open(self.fileread, 'r') as filelink:
            self.textblock = filelink.readlines()
        i = 0
        while i < len(self.textblock):
            if 'menuItem' in self.textblock[i]:
                element = MenuItem(self.textblock)
                i = element.lookThrow(i + 1)
                if not element.NOT_INCLUDE and element.LABEL:
                    self.ui_listwidget.addItem(element)
            else:
                i += 1

    def _saveMarkingMenu(self):
        with open(self.fileread, 'w') as fileread:
            fileread.write(''.join(self.textblock))

    def _updateLanguage(self):
        items = self.ui_listwidget.selectedItems()
        for item in items:
            item.setLanguage(self.ui_combobox.currentIndex())

    def _updateCommand(self):
        items = self.ui_listwidget.selectedItems()
        self.ui_textedit.setText('')
        cmds.image('MMtoKeyPyIconWidget', e=True, vis=False)
        self.ui_textedit.setEnabled(False)
        self.ui_button.setEnabled(False)
        if items:
            self.ui_combobox.setCurrentIndex(items[0].getLanguage())
        if len(items) == 1:
            self.ui_textedit.setText(items[0].getCommand())
            cmds.image('MMtoKeyPyIconWidget', e=True, vis=True, i=items[0].ICON)
            self.ui_textedit.setEnabled(True)
            self.ui_button.setEnabled(True)
