import os
import string
import functools
try:    # under Maya 2017
    from PySide.QtCore import *
    from PySide.QtGui import *
except ImportError:     # Maya 2017 and above
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
from maya import cmds, mel
import Engine
import LanguageChange
import HotkeyMaker
import UtilsQT
import Version


location = os.path.dirname(__file__)


class NodesEditor(QWidget):
    """editor for cluster node"""

    def __init__(self, engine, key):
        QWidget.__init__(self)
        self.ui = UtilsQT.loadUI(location + "/resources/ui/NodeEditor.ui", location + "/resources/ui", self)
        self._nodes = engine.cluster[key]
        self._engine = engine
        self._key = key

        # hide add menu
        if key == "panel":
            self.ui.btn_add._menu = QMenu(self)
            self.ui.btn_add.setMenu(self.ui.btn_add._menu)
            all_panels = set([x.rstrip(string.digits) for x in cmds.lsUI(p=True)])
            for panel in sorted(all_panels) + ["enter manually..."]:
                self.ui.btn_add._menu.addAction(panel, functools.partial(self._addKey, panel))
        else:
            self.ui.cmb_search_filter.hide()
            self.ui.cmb_search_name.hide()
            self.ui.btn_search_filter.hide()
            self.ui.btn_search_name.hide()
            self.ui.btn_add.released.connect(self._addKey)

        # hide prefix line
        if key in ("name", "preset", "panel"):
            self.ui.line_prefix.hide()
            self.ui.btn_panel.hide()
        else:
            self.ui.btn_panel._menu = QMenu()
            self.ui.btn_panel.setMenu(self.ui.btn_panel._menu)
            all_panels = set([x.rstrip(string.digits) for x in cmds.lsUI(p=True)])
            for panel in ["any"] + sorted(all_panels):
                self.ui.btn_panel._menu.addAction(panel, functools.partial(self.ui.line_prefix.setText, panel))

        # hide no click command
        if key == "tool":
            self.ui.grid_command.parent().hide()

        # signals
        self.ui.list_keys.currentItemChanged.connect(self._selectKey)
        self.ui.list_keys.itemClicked.connect(self._selectKey)
        self.ui.list_menu_mel.itemClicked.connect(self._selectMenu)
        self.ui.list_menu_python.itemClicked.connect(self._selectMenu)
        self.ui.list_command_python.itemClicked.connect(self._selectCommand)
        self.ui.cmb_menu.currentIndexChanged.connect(self.ui.stack_menu.setCurrentIndex)
        self.ui.cmb_command.currentIndexChanged.connect(self._selectCommandStack)
        self.ui.cmb_search_filter.currentIndexChanged.connect(self._selectSearchFilter)
        self.ui.cmb_search_name.currentIndexChanged.connect(self._selectSearchName)
        self.ui.btn_remove.released.connect(self._removeKey)
        self.ui.btn_break.released.connect(self._breakKey)
        self.ui.btn_search_filter.released.connect(self._selectSearchFilterAll)
        self.ui.btn_search_name.released.connect(self._selectSearchNameAll)
        self.ui.btn_command.released.connect(self._selectCommand)
        self.ui.chb_command.clicked.connect(self._selectCommandCondition)

        # init default. hide unnecessary
        self.reload(self._nodes)
        self._selectKey()

    def _selectKey(self):
        """trigger for change current key enable of disable UI elements load data from Node[]"""
        if self.ui.list_keys.currentRow() == -1:
            self.ui.btn_break.setEnabled(False)
            self.ui.btn_remove.setEnabled(False)
            self.ui.btn_search_filter.setEnabled(False)
            self.ui.btn_search_name.setEnabled(False)
            self.ui.split.setEnabled(False)
            self.ui.cmb_search_filter.setEnabled(False)
            self.ui.cmb_search_name.setEnabled(False)
        else:
            self.ui.btn_break.setEnabled(True)
            self.ui.btn_remove.setEnabled(True)
            self.ui.btn_search_filter.setEnabled(True)
            self.ui.btn_search_name.setEnabled(True)
            self.ui.split.setEnabled(True)
            self.ui.cmb_search_filter.setEnabled(True)
            self.ui.cmb_search_name.setEnabled(True)
            node = self._nodes[self.ui.list_keys.currentItem().text()]
            self.ui.cmb_search_filter.setCurrentIndex(node["search_filter"])
            self.ui.cmb_search_name.setCurrentIndex(node["search_name"])
            self.ui.cmb_command.setCurrentIndex(node["command_type"])
            self.ui.cmb_menu.setCurrentIndex(node["menu_type"])
            self.ui.chb_command.setChecked(node["command_always"])
            # load menu
            if node["menu_type"] == Engine.Menu.MEL:
                self.ui.list_menu_python.setCurrentRow(-1)
                item = self.ui.list_menu_mel.findItems(node["menu"], Qt.MatchExactly)
                if item:
                    self.ui.list_menu_mel.setCurrentItem(item[0])
                else:
                    self.ui.list_menu_mel.setCurrentRow(-1)
            else:
                self.ui.list_menu_mel.setCurrentRow(-1)
                item = self.ui.list_menu_python.findItems(node["menu"], Qt.MatchExactly)
                if item:
                    self.ui.list_menu_python.setCurrentItem(item[0])
                else:
                    self.ui.list_menu_python.setCurrentRow(-1)

            # load command
            if node["command_type"] == Engine.Menu.MEL:
                self.ui.list_command_python.setCurrentRow(-1)
                self.ui.text_command_python.setText("")
                self.ui.text_command_mel.setText(node["command"])
            elif node["command_type"] == Engine.Menu.PYTHON:
                self.ui.list_command_python.setCurrentRow(-1)
                self.ui.text_command_python.setText(node["command"])
                self.ui.text_command_mel.setText("")
            else:
                self.ui.text_command_mel.setText("")
                self.ui.text_command_python.setText("")
                item = self.ui.list_command_python.findItems(node["command"], Qt.MatchExactly)
                if item:
                    self.ui.list_command_python.setCurrentItem(item[0])
                else:
                    self.ui.list_command_python.setCurrentRow(-1)

    def _selectCommandCondition(self):
        """set if command should run always"""
        node = self._nodes[self.ui.list_keys.currentItem().text()]
        node["command_always"] = self.ui.chb_command.isChecked()

    def _addKey(self, value=None):
        """trigger for adding new key into cluster"""
        if self._key == "panel":
            if value == "enter manually...":
                key = raw_input().replace(" ", "")
            else:
                key = value
        elif self._key == "name":
            key = raw_input().replace(" ", "")
        elif self._key == "preset":
            key = raw_input()
        elif self._key == "dag":
            key = " ".join(self._engine.findDagKey())
            if not self.ui.line_prefix.text() or not key:
                return
            key = "%s %s" % (self.ui.line_prefix.text(), key)
        elif self._key == "non dag":
            key = " ".join(self._engine.findNonDagKey())
            if not self.ui.line_prefix.text() or not key:
                return
            key = "%s %s" % (self.ui.line_prefix.text(), key)
        elif self._key == "tool":
            if not self.ui.line_prefix.text():
                return
            key = "%s %s" % (self.ui.line_prefix.text(), cmds.currentCtx())
        else:
            return
        if key and key not in self._nodes:
            self._nodes[key] = Engine.DefaultData.node()
            self.ui.list_keys.addItem(key)

    def _removeKey(self):
        """trigger for remove key"""
        key = self.ui.list_keys.currentItem().text()
        if key == "any" and self._key == "panel":
            cmds.warning("protected key")
            return
        self._nodes.pop(key)
        self.ui.list_keys.takeItem(self.ui.list_keys.currentRow())

    def _breakKey(self):
        """break connection between selected node and menu"""
        node = self._nodes[self.ui.list_keys.currentItem().text()]
        node["menu"] = ""
        if node["menu_type"] == Engine.Menu.MEL:
            self.ui.list_menu_mel.setCurrentRow(-1)
        else:
            self.ui.list_menu_python.setCurrentRow(-1)

    def _selectSearchFilter(self, index):
        """set current filter"""
        node = self._nodes[self.ui.list_keys.currentItem().text()]
        node["search_filter"] = index

    def _selectSearchFilterAll(self):
        """apply current filter to all keys"""
        for node in self._nodes.values():
            node["search_filter"] = self.ui.cmb_search_filter.currentIndex()

    def _selectSearchName(self, index):
        """set current filter name"""
        node = self._nodes[self.ui.list_keys.currentItem().text()]
        node["search_name"] = index

    def _selectSearchNameAll(self):
        """apply current filter name to all keys"""
        for node in self._nodes.values():
            node["search_name"] = self.ui.cmb_search_name.currentIndex()

    def _selectMenu(self):
        """singal for selected menu"""
        node = self._nodes[self.ui.list_keys.currentItem().text()]
        node["menu_type"] = self.ui.cmb_menu.currentIndex()
        if node["menu_type"] == Engine.Menu.MEL:
            self.ui.list_menu_python.setCurrentRow(-1)
            node["menu"] = self.ui.list_menu_mel.currentItem().text()
        else:
            self.ui.list_menu_mel.setCurrentRow(-1)
            node["menu"] = self.ui.list_menu_python.currentItem().text()

    def _selectCommand(self):
        """signal for selected command"""
        node = self._nodes[self.ui.list_keys.currentItem().text()]
        node["command_type"] = self.ui.cmb_command.currentIndex()
        if node["command_type"] == Engine.Command.MEL:
            self.ui.text_command_python.setText("")
            self.ui.list_command_python.setCurrentRow(-1)
            node["command"] = self.ui.text_command_mel.toPlainText()
        elif node["command_type"] == Engine.Command.PYTHON:
            self.ui.text_command_mel.setText("")
            self.ui.list_command_python.setCurrentRow(-1)
            node["command"] = self.ui.text_command_python.toPlainText()
        else:
            self.ui.text_command_python.setText("")
            self.ui.text_command_mel.setText("")
            node["command"] = self.ui.list_command_python.currentItem().text()

    def _selectCommandStack(self, index):
        """signal for change command type"""
        self.ui.btn_command.setEnabled(index != 2)
        self.ui.stack_command.setCurrentIndex(index)

    def reload(self, nodes):
        """reload ui"""
        self._nodes = nodes
        self.ui.list_command_python.clear()
        self.ui.list_keys.clear()
        self.ui.list_menu_python.clear()
        self.ui.list_menu_mel.clear()
        self.ui.list_keys.addItems(sorted(self._nodes.keys()))
        if os.path.isdir(cmds.internalVar(umm=True)):
            self.ui.list_menu_mel.addItems([x[5:-4] for x in os.listdir(cmds.internalVar(umm=True))])
        same_file = set()
        if os.path.isdir(location + "/menus"):
            for f in os.listdir(location + "/menus"):
                if os.path.splitext(f)[1] in (".py", ".pyc") and f not in ("__init__.py", "__init__.pyc"):
                    same_file.add(os.path.splitext(f)[0])
            self.ui.list_menu_python.addItems(list(same_file))
        same_file.clear()
        if os.path.isdir(location + "/commands"):
            for f in os.listdir(location + "/commands"):
                if os.path.splitext(f)[1] in (".py", ".pyc") and f not in ("__init__.py", "__init__.pyc"):
                    same_file.add(os.path.splitext(f)[0])
            self.ui.list_command_python.addItems(list(same_file))


class MainWindow(QMainWindow):
    """main window"""

    def __init__(self, engine):
        QMainWindow.__init__(self, UtilsQT.wrapWidget())
        UtilsQT.removeWidgets("MMtoKeyUI", "MMtoKeyPreferences", "MMtoKeyAbout")
        UtilsQT.reloadWidget("MMtoKeyUI", self)
        self.ui = UtilsQT.loadUI(location + "/resources/ui/Editor.ui", location + "/resources/ui", self)
        self.setWindowTitle("MMtoKey %s" % Version.version)
        self.setFixedSize(430, 340)
        self._engine = engine
        for name in "panel", "name", "non dag", "dag", "tool", "preset":
            self.ui.tab_widgets.addTab(NodesEditor(engine, name), name)
        menu_file = QMenu("file")
        menu_file.addAction("save", lambda: Engine.UserData.write(self._engine.preferences, self._engine.cluster))
        menu_file.addAction("update", self._update)
        menu_file.addAction("preferences", lambda: Preferences(self._engine.preferences))
        menu_file.addAction("import", self._import)
        menu_file.addAction("export", lambda: Engine.UserData.exporter(self._engine.preferences, self._engine.cluster))
        self.menuBar().addMenu(menu_file)
        menu_file = QMenu("tools")
        menu_file.addAction("marking menu editor", lambda: mel.eval("menuEditorWnd;"))
        menu_file.addAction("marking menu language", LanguageChange.MainWindow)
        menu_file.addAction("hotkey maker", HotkeyMaker.MainWindow)
        self.menuBar().addMenu(menu_file)
        self.menuBar().addAction("about", UtilsQT.about)
        self._update()
        self.show()

    def _update(self):
        """give new nodes to all widgets and update"""
        for i, name in enumerate(["panel", "name", "non dag", "dag", "tool", "preset"]):
            self.ui.tab_widgets.widget(i).reload(self._engine.cluster[name])

    def _import(self):
        """import new config"""
        self._engine.preferences, self._engine.cluster = Engine.UserData.importer()
        self._update()


class Preferences(QMainWindow):

    def __init__(self, preferences):
        QMainWindow.__init__(self, UtilsQT.wrapWidget())
        self.ui = UtilsQT.loadUI(location + "/resources/ui/Preferences.ui", location + "/resources/ui", self)
        UtilsQT.reloadWidget("MMtoKeyPreferences", self)
        self._preferences = preferences
        self.setWindowTitle("MMtoKey Preferences")
        self.setWindowFlags(Qt.Tool)
        self.setFixedSize(260, 300)

        self.ui.cmb_lmb.setCurrentIndex(preferences["default_lmb_type"])
        self.ui.line_lmb.setText(preferences["default_lmb"])
        self.ui.cmb_mmb.setCurrentIndex(preferences["default_mmb_type"])
        self.ui.line_mmb.setText(preferences["default_mmb"])
        self.ui.chb_dag.setChecked(preferences["same_dag"])
        self.ui.chb_non_dag.setChecked(preferences["same_non_dag"])
        self.ui.chb_radial.setChecked(preferences["preset_radial"])
        self.ui.chb_hud.setChecked(preferences["preset_hud"])
        self.ui.spin_hud_s.setValue(preferences["preset_hud_s"])
        self.ui.spin_hud_b.setValue(preferences["preset_hud_b"])

        # signals
        self.ui.chb_hud.toggled.connect(self.ui.spin_hud_b.setEnabled)
        self.ui.chb_hud.toggled.connect(self.ui.spin_hud_s.setEnabled)
        self.ui.btn_save.released.connect(self._save)
        self.ui.spin_hud_s.setEnabled(preferences["preset_hud"])
        self.ui.spin_hud_b.setEnabled(preferences["preset_hud"])
        self.show()

    def _save(self):
        self._preferences["default_lmb_type"] = self.ui.cmb_lmb.currentIndex()
        self._preferences["default_mmb_type"] = self.ui.cmb_mmb.currentIndex()
        self._preferences["default_lmb"] = self.ui.line_lmb.text()
        self._preferences["default_mmb"] = self.ui.line_mmb.text()
        self._preferences["same_dag"] = self.ui.chb_dag.isChecked()
        self._preferences["same_non_dag"] = self.ui.chb_non_dag.isChecked()
        self._preferences["preset_radial"] = self.ui.chb_radial.isChecked()
        self._preferences["preset_hud"] = self.ui.chb_hud.isChecked()
        self._preferences["preset_hud_s"] = self.ui.spin_hud_s.value()
        self._preferences["preset_hud_b"] = self.ui.spin_hud_b.value()
        cmds.warning("preferences saved")
