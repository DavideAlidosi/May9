import os
import string
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
import QtWrapper


__location__ = os.path.dirname(__file__)


class NodesEditor(QWidget):
    """editor for cluster node"""
    FILTERS = 0b100
    PANEL_PREFIX = 0b010
    NO_CLICK = 0b001
    KEYS = {"panel": 0b101, "name": 0b001, "non dag": 0b011, "dag": 0b011, "tool": 0b010, "preset": 0b001}

    def __init__(self, engine, key):
        QWidget.__init__(self)
        self._nodes = engine.cluster[key]
        self._key = key
        self._engine = engine

        # from QT Designer
        self.setFixedSize(430, 300)
        self._list_menu_mel = QListWidget(self)
        self._list_menu_mel.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self._list_menu_mel.setMinimumSize(QSize(0, 0))
        self._list_menu_python = QListWidget(self)
        self._list_menu_python.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self._list_menu_python.setMinimumSize(QSize(0, 0))
        self._list_command = QListWidget(self)
        self._list_command.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self._list_command.setMinimumSize(QSize(0, 0))
        self._text_command_mel = QTextEdit(self)
        self._text_command_python = QTextEdit(self)
        self._splitter_node = QSplitter(self)
        self._splitter_node.setGeometry(QRect(220, 10, 201, 281))
        self._splitter_node.setOrientation(Qt.Vertical)
        vertical_layout_widget = QWidget(self._splitter_node)
        vertical_layout = QVBoxLayout(vertical_layout_widget)
        vertical_layout.setContentsMargins(0, 0, 0, 0)
        vertical_layout.setSpacing(2)
        self._cmb_menu = QComboBox(vertical_layout_widget)
        self._cmb_menu.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self._cmb_menu.setMinimumSize(QSize(200, 20))
        vertical_layout.addWidget(self._cmb_menu)
        self._stack_menu = QStackedWidget(vertical_layout_widget)
        self._stack_menu.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self._stack_menu.setMinimumSize(QSize(0, 50))
        vertical_layout.addWidget(self._stack_menu)
        grid_layout_widget = QWidget(self._splitter_node)
        grid_layout = QGridLayout(grid_layout_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setHorizontalSpacing(0)
        grid_layout.setVerticalSpacing(2)
        self._cmb_command = QComboBox(grid_layout_widget)
        self._cmb_command.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self._cmb_command.setMinimumSize(QSize(200, 20))
        grid_layout.addWidget(self._cmb_command, 0, 0, 1, 1)
        self._chb_command = QCheckBox(grid_layout_widget)
        self._chb_command.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self._chb_command.setMinimumSize(QSize(150, 20))
        grid_layout.addWidget(self._chb_command, 1, 0, 1, 1)
        self._btn_command = QPushButton(grid_layout_widget)
        self._btn_command.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self._btn_command.setMinimumSize(QSize(50, 20))
        grid_layout.addWidget(self._btn_command, 1, 1, 1, 1)
        self._stack_command = QStackedWidget(grid_layout_widget)
        self._stack_command.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self._stack_command.setMinimumSize(QSize(0, 50))
        grid_layout.addWidget(self._stack_command, 2, 0, 1, 2)
        widget = QWidget(self)
        widget.setGeometry(QRect(10, 10, 201, 281))
        grid_layout_1 = QGridLayout(widget)
        grid_layout_1.setContentsMargins(0, 0, 0, 0)
        grid_layout_1.setHorizontalSpacing(0)
        grid_layout_1.setVerticalSpacing(2)
        self._list_keys = QListWidget(widget)
        self._list_keys.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self._list_keys.setMinimumSize(QSize(0, 50))
        grid_layout_1.addWidget(self._list_keys, 0, 0, 1, 3)
        self._cmb_search_filter = QComboBox(widget)
        self._cmb_search_filter.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self._cmb_search_filter.setMinimumSize(QSize(0, 20))
        grid_layout_1.addWidget(self._cmb_search_filter, 1, 0, 1, 2)
        self._btn_search_filter = QPushButton(widget)
        self._btn_search_filter.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self._btn_search_filter.setMinimumSize(QSize(0, 20))
        grid_layout_1.addWidget(self._btn_search_filter, 1, 2, 1, 1)
        self._cmb_search_name = QComboBox(widget)
        self._cmb_search_name.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self._cmb_search_name.setMinimumSize(QSize(0, 20))
        grid_layout_1.addWidget(self._cmb_search_name, 2, 0, 1, 2)
        self._btn_search_name = QPushButton(widget)
        self._btn_search_name.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self._btn_search_name.setMinimumSize(QSize(0, 20))
        grid_layout_1.addWidget(self._btn_search_name, 2, 2, 1, 1)
        self._btn_panel = QPushButton(widget)
        self._btn_panel.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self._btn_panel.setMinimumSize(QSize(0, 20))
        grid_layout_1.addWidget(self._btn_panel, 3, 0, 1, 1)
        self._line_prefix = QLineEdit("any", widget)
        self._line_prefix.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self._line_prefix.setMinimumSize(QSize(0, 20))
        grid_layout_1.addWidget(self._line_prefix, 3, 1, 1, 2)
        self._btn_add = QPushButton("add", widget)
        self._btn_add.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self._btn_add.setMinimumSize(QSize(0, 20))
        grid_layout_1.addWidget(self._btn_add, 4, 0, 1, 1)
        self._btn_remove = QPushButton("remove", widget)
        self._btn_remove.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self._btn_remove.setMinimumSize(QSize(0, 20))
        grid_layout_1.addWidget(self._btn_remove, 4, 1, 1, 1)
        self._btn_break = QPushButton("break menu", widget)
        self._btn_break.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self._btn_break.setMinimumSize(QSize(0, 20))
        grid_layout_1.addWidget(self._btn_break, 4, 2, 1, 1)
        self._stack_menu.addWidget(self._list_menu_mel)
        self._stack_menu.addWidget(self._list_menu_python)
        self._stack_command.addWidget(self._text_command_mel)
        self._stack_command.addWidget(self._text_command_python)
        self._stack_command.addWidget(self._list_command)

        # my code
        self._btn_command.setText("save")
        self._btn_search_filter.setText("to all keys")
        self._btn_search_name.setText("to all keys")
        self._btn_panel.setText("panel")
        self._btn_add.setText("add")
        self._btn_remove.setText("remove")
        self._btn_break.setText("break menu")
        self._line_prefix.setText("any")
        self._chb_command.setText("run always after release")
        self._splitter_node.moveSplitter(100, 1)
        self._btn_command.setFlat(True)
        self._btn_add.setFlat(True)
        self._btn_remove.setFlat(True)
        self._btn_break.setFlat(True)
        self._btn_search_filter.setFlat(True)
        self._btn_search_name.setFlat(True)
        self._btn_panel.setFlat(True)
        self._cmb_menu.addItems(["mel file source", "python module"])
        self._cmb_command.addItems(["mel string source", "python string source", "python module"])
        self._cmb_search_name.addItems(['names prefix', 'names suffix', 'names contain', 'names absolute'])
        self._cmb_search_filter.addItems(['none', 'dag', 'non-dag', 'non-dag, dag', 'name', 'name, dag',
                                          'name, non-dag', 'name, non-dag, dag'])

        # hide parts
        if not self.FILTERS & self.KEYS[key]:
            self._cmb_search_filter.hide()
            self._cmb_search_name.hide()
            self._btn_search_filter.hide()
            self._btn_search_name.hide()
        else:
            menu = QMenu(self)
            mapper = QSignalMapper(self)
            for panel in sorted(set([x.rstrip(string.digits) for x in cmds.lsUI(p=True)])) + ["enter manually..."]:
                action = QAction(panel, self)
                action.triggered.connect(mapper.map)
                mapper.setMapping(action, panel)
                menu.addAction(action)
            mapper.mapped["QString"].connect(self._addKey)
            self._btn_add.setMenu(menu)
        if not self.PANEL_PREFIX & self.KEYS[key]:
            self._line_prefix.hide()
            self._btn_panel.hide()
        else:
            menu = QMenu(self)
            mapper = QSignalMapper(self)
            for panel in ["any"] + sorted(set([x.rstrip(string.digits) for x in cmds.lsUI(p=True)])):
                action = QAction(panel, self)
                action.triggered.connect(mapper.map)
                mapper.setMapping(action, panel)
                menu.addAction(action)
            mapper.mapped["QString"].connect(self._line_prefix.setText)
            self._btn_panel.setMenu(menu)
        if not self.NO_CLICK & self.KEYS[key]:
            grid_layout_widget.hide()

        # signals
        self._list_keys.currentItemChanged.connect(self._selectKey)
        self._list_keys.itemClicked.connect(self._selectKey)
        self._list_menu_mel.itemClicked.connect(self._selectMenu)
        self._list_menu_python.itemClicked.connect(self._selectMenu)
        self._list_command.itemClicked.connect(self._selectCommand)
        self._cmb_menu.currentIndexChanged.connect(self._stack_menu.setCurrentIndex)
        self._cmb_command.currentIndexChanged.connect(self._selectCommandStack)
        self._cmb_search_filter.currentIndexChanged.connect(self._selectSearchFilter)
        self._cmb_search_name.currentIndexChanged.connect(self._selectSearchName)
        if not self.FILTERS & self.KEYS[key]:
            self._btn_add.released.connect(self._addKey)
        self._btn_remove.released.connect(self._removeKey)
        self._btn_break.released.connect(self._breakKey)
        self._btn_search_filter.released.connect(self._selectSearchFilterAll)
        self._btn_search_name.released.connect(self._selectSearchNameAll)
        self._btn_command.released.connect(self._selectCommand)
        self._chb_command.clicked.connect(self._selectCommandCondition)

        # init default. hide unnecessary
        self.reload(self._nodes)
        self._selectKey()

    def _selectKey(self):
        """trigger for change current key enable of disable UI elements load data from Node[]"""
        if self._list_keys.currentRow() == -1:
            self._btn_break.setEnabled(False)
            self._btn_remove.setEnabled(False)
            self._btn_search_filter.setEnabled(False)
            self._btn_search_name.setEnabled(False)
            self._splitter_node.setEnabled(False)
            self._cmb_search_filter.setEnabled(False)
            self._cmb_search_name.setEnabled(False)
        else:
            self._btn_break.setEnabled(True)
            self._btn_remove.setEnabled(True)
            self._btn_search_filter.setEnabled(True)
            self._btn_search_name.setEnabled(True)
            self._splitter_node.setEnabled(True)
            self._cmb_search_filter.setEnabled(True)
            self._cmb_search_name.setEnabled(True)
            node = self._nodes[self._list_keys.currentItem().text()]
            self._cmb_search_filter.setCurrentIndex(node["search_filter"])
            self._cmb_search_name.setCurrentIndex(node["search_name"])
            self._cmb_command.setCurrentIndex(node["command_type"])
            self._cmb_menu.setCurrentIndex(node["menu_type"])
            self._chb_command.setChecked(node["command_always"])
            # load menu
            if node["menu_type"] == Engine.Menu.MEL:
                self._list_menu_python.setCurrentRow(-1)
                item = self._list_menu_mel.findItems(node["menu"], Qt.MatchExactly)
                if item:
                    self._list_menu_mel.setCurrentItem(item[0])
                else:
                    self._list_menu_mel.setCurrentRow(-1)
            else:
                self._list_menu_mel.setCurrentRow(-1)
                item = self._list_menu_python.findItems(node["menu"], Qt.MatchExactly)
                if item:
                    self._list_menu_python.setCurrentItem(item[0])
                else:
                    self._list_menu_python.setCurrentRow(-1)

            # load command
            if node["command_type"] == Engine.Menu.MEL:
                self._list_command.setCurrentRow(-1)
                self._text_command_python.setText("")
                self._text_command_mel.setText(node["command"])
            elif node["command_type"] == Engine.Menu.PYTHON:
                self._list_command.setCurrentRow(-1)
                self._text_command_python.setText(node["command"])
                self._text_command_mel.setText("")
            else:
                self._text_command_mel.setText("")
                self._text_command_python.setText("")
                item = self._list_command.findItems(node["command"], Qt.MatchExactly)
                if item:
                    self._list_command.setCurrentItem(item[0])
                else:
                    self._list_command.setCurrentRow(-1)

    def _selectCommandCondition(self):
        """set if command should run always"""
        node = self._nodes[self._list_keys.currentItem().text()]
        node["command_always"] = self._chb_command.isChecked()

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
            if not self._line_prefix.text() or not key:
                return
            key = "%s %s" % (self._line_prefix.text(), key)
        elif self._key == "non dag":
            key = " ".join(self._engine.findNonDagKey())
            if not self._line_prefix.text() or not key:
                return
            key = "%s %s" % (self._line_prefix.text(), key)
        elif self._key == "tool":
            if not self._line_prefix.text():
                return
            key = "%s %s" % (self._line_prefix.text(), cmds.currentCtx())
        else:
            return
        if key and key not in self._nodes:
            self._nodes[key] = Engine.DefaultData.node()
            self._list_keys.addItem(key)

    def _removeKey(self):
        """trigger for remove key"""
        key = self._list_keys.currentItem().text()
        if key == "any" and self._key == "panel":
            cmds.warning("protected key")
            return
        self._nodes.pop(key)
        self._list_keys.takeItem(self._list_keys.currentRow())

    def _breakKey(self):
        """break connection between selected node and menu"""
        node = self._nodes[self._list_keys.currentItem().text()]
        node["menu"] = ""
        if node["menu_type"] == Engine.Menu.MEL:
            self._list_menu_mel.setCurrentRow(-1)
        else:
            self._list_menu_python.setCurrentRow(-1)

    def _selectSearchFilter(self, index):
        """set current filter"""
        node = self._nodes[self._list_keys.currentItem().text()]
        node["search_filter"] = index

    def _selectSearchFilterAll(self):
        """apply current filter to all keys"""
        for node in self._nodes:
            self._nodes[node]["search_filter"] = self._cmb_search_filter.currentIndex()

    def _selectSearchName(self, index):
        """set current filter name"""
        node = self._nodes[self._list_keys.currentItem().text()]
        node["search_name"] = index

    def _selectSearchNameAll(self):
        """apply current filter name to all keys"""
        for node in self._nodes:
            self._nodes[node]["search_name"] = self._cmb_search_filter.currentIndex()

    def _selectMenu(self):
        """singal for selected menu"""
        node = self._nodes[self._list_keys.currentItem().text()]
        node["menu_type"] = self._cmb_menu.currentIndex()
        if node["menu_type"] == Engine.Menu.MEL:
            self._list_menu_python.setCurrentRow(-1)
            node["menu"] = self._list_menu_mel.currentItem().text()
        else:
            self._list_menu_mel.setCurrentRow(-1)
            node["menu"] = self._list_menu_python.currentItem().text()

    def _selectCommand(self):
        """signal for selected command"""
        node = self._nodes[self._list_keys.currentItem().text()]
        node["command_type"] = self._cmb_command.currentIndex()
        if node["command_type"] == Engine.Command.MEL:
            self._text_command_python.setText("")
            self._list_command.setCurrentRow(-1)
            node["command"] = self._text_command_mel.toPlainText()
        elif node["command_type"] == Engine.Command.PYTHON:
            self._text_command_mel.setText("")
            self._list_command.setCurrentRow(-1)
            node["command"] = self._text_command_python.toPlainText()
        else:
            self._text_command_python.setText("")
            self._text_command_mel.setText("")
            node["command"] = self._list_command.currentItem().text()

    def _selectCommandStack(self, index):
        """signal for change command type"""
        self._btn_command.setEnabled(index != 2)
        self._stack_command.setCurrentIndex(index)

    def reload(self, nodes):
        """reload ui"""
        self._nodes = nodes
        self._list_command.clear()
        self._list_keys.clear()
        self._list_menu_python.clear()
        self._list_menu_mel.clear()
        self._list_keys.addItems(sorted(self._nodes.keys()))
        if os.path.isdir(cmds.internalVar(umm=True)):
            self._list_menu_mel.addItems([x[5:-4] for x in os.listdir(cmds.internalVar(umm=True))])
        same_file = set()
        if os.path.isdir(__location__ + "/data/menu"):
            for f in os.listdir(__location__ + "/data/menu"):
                if os.path.splitext(f)[1] in (".py", ".pyc") and f not in ("__init__.py", "__init__.pyc"):
                    same_file.add(os.path.splitext(f)[0])
            self._list_menu_python.addItems(list(same_file))
        same_file.clear()
        if os.path.isdir(__location__ + "/data/command"):
            for f in os.listdir(__location__ + "/data/command"):
                if os.path.splitext(f)[1] in (".py", ".pyc") and f not in ("__init__.py", "__init__.pyc"):
                    same_file.add(os.path.splitext(f)[0])
            self._list_command.addItems(list(same_file))


class MainWindow(QMainWindow):
    """main window"""
    CLUSTER = "panel", "name", "non dag", "dag", "tool", "preset"
    WINDOWS = "MMtoKeyUI", "MMtoKeyPreferences", "MMtoKeyAbout"
    NAME = "MMtoKeyUI"

    def __init__(self, engine):
        QMainWindow.__init__(self, QtWrapper.wrapWidget())
        for name in self.WINDOWS:
            while cmds.window(name, ex=True):
                cmds.deleteUI(name)
        self.setObjectName(self.NAME)
        self.setWindowTitle("MMtoKey %s" % Engine.__version__)
        self._engine = engine
        self.setFixedSize(430, 340)
        self._tab_editors = QTabWidget(self)
        self._tab_editors.setGeometry(0, 20, 430, 320)
        for name in self.CLUSTER:
            self._tab_editors.addTab(NodesEditor(engine, name), name)

        menu_file = QMenu("file")
        menu_file.addAction("save", lambda: Engine.UserData.write(self._engine.preferences, self._engine.cluster))
        menu_file.addAction("update", self._update)
        menu_file.addAction("preferences", lambda: Preferences(self._engine.preferences))
        menu_file.addAction("import", self._import)
        menu_file.addAction("export", lambda: Engine.UserData.exporter(self._engine.preferences, self._engine.cluster))
        self.menuBar().addMenu(menu_file)
        menu_file = QMenu("tools")
        menu_file.addAction("marking menu editor", lambda: mel.eval("menuEditorWnd;"))
        menu_file.addAction("marking menu language", lambda: LanguageChange.ChangeLanguage())
        menu_file.addAction("hotkey maker", lambda: HotkeyMaker.HotkeyMaker())
        self.menuBar().addMenu(menu_file)
        self.menuBar().addAction("about", About)
        self._update()
        self.show()

    def _update(self):
        """update all widgets"""
        for i in xrange(6):
            self._tab_editors.widget(i).reload(self._engine.cluster[self.CLUSTER[i]])

    def _import(self):
        """import new config"""
        self._engine.preferences, self._engine.cluster = Engine.UserData.importer()
        self._update()


class Preferences(QMainWindow):

    def __init__(self, preferences):
        QMainWindow.__init__(self, QtWrapper.wrapWidget())
        self._preferences = preferences
        while cmds.window("MMtoKeyPreferences", ex=True):
            cmds.deleteUI("MMtoKeyPreferences")
        self.setObjectName("MMtoKeyPreferences")
        self.setWindowTitle("MMtoKey Preferences")
        self.setWindowFlags(Qt.Tool)

        # from QT designer
        self.setFixedSize(260, 280)
        layout_widget = QWidget(self)
        layout_widget.setGeometry(QRect(10, 10, 238, 260))
        grid_layout = QGridLayout(layout_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setHorizontalSpacing(2)
        grid_layout.setVerticalSpacing(2)
        label_4 = QLabel("LMB (selected) default marking menu", layout_widget)
        label_4.setMinimumSize(QSize(0, 20))
        grid_layout.addWidget(label_4, 0, 0, 1, 2)
        self._cmb_lmb = QComboBox(layout_widget)
        self._cmb_lmb.setMinimumSize(QSize(0, 20))
        self._cmb_lmb.addItems(["mel", "python"])
        self._cmb_lmb.setCurrentIndex(preferences["default_lmb_type"])
        grid_layout.addWidget(self._cmb_lmb, 1, 0, 1, 1)
        self._line_lmb = QLineEdit(preferences["default_lmb"], layout_widget)
        self._line_lmb.setMinimumSize(QSize(0, 20))
        grid_layout.addWidget(self._line_lmb, 1, 1, 1, 1)
        label_3 = QLabel("MMB (tools) default marking menu", layout_widget)
        label_3.setMinimumSize(QSize(0, 20))
        grid_layout.addWidget(label_3, 2, 0, 1, 2)
        self._cmb_mmb = QComboBox(layout_widget)
        self._cmb_mmb.setMinimumSize(QSize(0, 20))
        self._cmb_mmb.addItems(["mel", "python"])
        self._cmb_mmb.setCurrentIndex(preferences["default_mmb_type"])
        grid_layout.addWidget(self._cmb_mmb, 3, 0, 1, 1)
        self._line_mmb = QLineEdit(preferences["default_mmb"], layout_widget)
        self._line_mmb.setMinimumSize(QSize(0, 20))
        grid_layout.addWidget(self._line_mmb, 3, 1, 1, 1)
        self._chb_dag = QCheckBox("same dag nodes", layout_widget)
        self._chb_dag.setMinimumSize(QSize(0, 20))
        self._chb_dag.setChecked(preferences["same_dag"])
        grid_layout.addWidget(self._chb_dag, 4, 0, 1, 2)
        self._chb_non_dag = QCheckBox("same non dag nodes", layout_widget)
        self._chb_non_dag.setMinimumSize(QSize(0, 20))
        self._chb_non_dag.setChecked(preferences["same_non_dag"])
        grid_layout.addWidget(self._chb_non_dag, 5, 0, 1, 2)
        self._chb_radial = QCheckBox("radial menu for presets", layout_widget)
        self._chb_radial.setMinimumSize(QSize(0, 20))
        self._chb_radial.setChecked(preferences["preset_radial"])
        grid_layout.addWidget(self._chb_radial, 6, 0, 1, 2)
        self._chb_hud = QCheckBox("Heads-up display for presets", layout_widget)
        self._chb_hud.setMinimumSize(QSize(0, 20))
        self._chb_hud.setChecked(preferences["preset_hud"])
        grid_layout.addWidget(self._chb_hud, 7, 0, 1, 2)
        self._spin_hud_s = QSpinBox(layout_widget)
        self._spin_hud_s.setMinimumSize(QSize(0, 20))
        self._spin_hud_s.setMinimum(0)
        self._spin_hud_s.setMaximum(9)
        self._spin_hud_s.setValue(preferences["preset_hud_s"])
        grid_layout.addWidget(self._spin_hud_s, 8, 0, 1, 1)
        label = QLabel("HUD section", layout_widget)
        label.setMinimumSize(QSize(0, 20))
        grid_layout.addWidget(label, 8, 1, 1, 1)
        self._spin_hud_b = QSpinBox(layout_widget)
        self._spin_hud_b.setMinimumSize(QSize(0, 20))
        self._spin_hud_b.setMinimum(0)
        self._spin_hud_b.setMaximum(9)
        self._spin_hud_b.setValue(preferences["preset_hud_b"])
        grid_layout.addWidget(self._spin_hud_b, 9, 0, 1, 1)
        label_2 = QLabel("HUD block", layout_widget)
        label_2.setMinimumSize(QSize(0, 20))
        grid_layout.addWidget(label_2, 9, 1, 1, 1)
        button = QPushButton("save", layout_widget)
        button.setMinimumSize(QSize(0, 20))
        grid_layout.addWidget(button, 10, 0, 1, 1)

        # signals
        self._chb_hud.toggled.connect(self._spin_hud_b.setEnabled)
        self._chb_hud.toggled.connect(self._spin_hud_s.setEnabled)
        button.released.connect(self._save)
        self._spin_hud_s.setEnabled(preferences["preset_hud"])
        self._spin_hud_b.setEnabled(preferences["preset_hud"])
        self.show()

    def _save(self):
        self._preferences["default_lmb_type"] = self._cmb_lmb.currentIndex()
        self._preferences["default_mmb_type"] = self._cmb_mmb.currentIndex()
        self._preferences["default_lmb"] = self._line_lmb.text()
        self._preferences["default_mmb"] = self._line_mmb.text()
        self._preferences["same_dag"] = self._chb_dag.isChecked()
        self._preferences["same_non_dag"] = self._chb_non_dag.isChecked()
        self._preferences["preset_radial"] = self._chb_radial.isChecked()
        self._preferences["preset_hud"] = self._chb_hud.isChecked()
        self._preferences["preset_hud_s"] = self._spin_hud_s.value()
        self._preferences["preset_hud_b"] = self._spin_hud_b.value()


class About(QMainWindow):
    """about author window"""
    def __init__(self, *args):
        QMainWindow.__init__(self, QtWrapper.wrapWidget())
        self.setFixedSize(160, 130)
        self.setWindowTitle("About")
        self.setWindowFlags(Qt.Tool)
        while cmds.window("MMtoKeyAbout", ex=True):
            cmds.deleteUI("MMtoKeyAbout")
        self.setObjectName("MMtoKeyAbout")
        ui_text = QLabel('MMtoKey\nv%s\n\n\nAndrey Menshikov \nDavide Alidosi, 2017' % Engine.__version__, self)
        ui_text.setGeometry(10, 10, 140, 80)
        ui_btn = QPushButton('OK', self)
        ui_btn.setGeometry(40, 100, 75, 20)
        ui_btn.released.connect(self._close)
        self.show()

    @staticmethod
    def _close():
        cmds.deleteUI("MMtoKeyAbout")
