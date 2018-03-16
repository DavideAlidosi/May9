import os
import importlib
import string
import pickle
import shutil
import zipfile
from maya import mel, cmds


location = os.path.dirname(__file__)
protocol = 1


class Menu(object):
    """manager of marking menus"""

    POSITIONS = "N", "NE", "E", "SE", "S", "SW", "W", "NW"
    LMB = 1
    MMB = 2
    MEL = 0
    PYTHON = 1
    PRESET = 2

    @classmethod
    def show(cls, menu_type, menu_name, preferences, **kwargs):
        """create marking menu"""
        cls.hide(kwargs["b"])
        if not menu_name:
            return
        if menu_type == cls.MEL:
            cls._mel(menu_name, p=cmds.layout(cmds.getPanel(up=True), q=True, p=True), aob=True, mm=True, **kwargs)
        elif menu_type == cls.PYTHON:
            cls._python(menu_name, p=cmds.layout(cmds.getPanel(up=True), q=True, p=True), aob=True, mm=True, **kwargs)
        else:
            cls._preset(menu_name, preferences, p=cmds.layout(cmds.getPanel(up=True), q=True, p=True), aob=True,
                        mm=True, **kwargs)

    @classmethod
    def hide(cls, *buttons):
        """destroy marking menu"""
        for button in buttons or (cls.LMB, cls.MMB):
            while cmds.popupMenu("mm_%i" % button, q=True, ex=True):
                cmds.deleteUI("mm_%i" % button)

    @classmethod
    def _preset(cls, item_list, preferences, **kwargs):
        """"show menu for presets"""
        cmds.popupMenu("mm_%i" % kwargs["b"], **kwargs)
        i = 0
        for item in item_list:
            if preferences["preset_radial"] and i < len(cls.POSITIONS):
                cmds.menuItem(stp="python", c="MMtoKey.engine.setPreset('%s')" % item, rp=cls.POSITIONS[i], label=item)
                i += 1
            else:
                cmds.menuItem(stp="python", c="MMtoKey.engine.setPreset('%s')" % item, label=item)

    @staticmethod
    def _mel(file_name, **kwargs):
        """show static marking menu"""
        cmds.popupMenu("mm_%i" % kwargs["b"], **kwargs)
        mel.eval("source menu_%s.mel" % file_name)

    @staticmethod
    def _python(module_name, **kwargs):
        """show python generated temp menu"""
        importlib.import_module("MMtoKey.menus." + module_name).run(cmds.popupMenu("mm_%i" % kwargs["b"], **kwargs))


class Command(object):
    """no click command manager"""
    MEL = 0
    PYTHON = 1
    PYTHON_MODULE = 2

    @classmethod
    def run(cls, command, language):
        """execute no-click command"""
        if language == cls.MEL:
            mel.eval(command)
        elif language == cls.PYTHON:
            exec command
        else:
            importlib.import_module("MMtoKey.commands." + command).run()


class DefaultData(object):
    """default data dicts generator"""
    @staticmethod
    def node():
        """empty by default node"""
        return {"search_filter": 6, "search_name": 0, "command": "", "command_type": 0, "menu": "", "menu_type": 0,
                "command_always": False}

    @classmethod
    def cluster(cls):
        """empty cluster for nodes"""
        cluster = {"panel": {}, "dag": {}, "non dag": {}, "preset": {}, "tool": {}, "name": {}}
        panels = (("any", 1), ("blendShapePanel", 6), ("clipEditorPanel", 6), ("componentEditorPanel", 6),
                  ("visorPanel", 6), ("createNodePanel", 6), ("dopeSheetPanel", 6), ("dynPaintScriptedPanel", 6),
                  ("dynRelEdPanel", 6), ("graphEditor", 6), ("hyperGraphPanel", 6), ("hyperShadePanel", 6),
                  ("nodeEditorPanel", 6), ("outlinerPanel", 6), ("scriptEditorPanel", 0), ("modelPanel", 1),
                  ("polyTexturePlacementPanel", 1), ("profilerPanel", 6), ("referenceEditorPanel", 6),
                  ("relationshipPanel", 6), ("renderView", 6), ("sequenceEditorPanel", 6))
        for panel in panels:
            node = cls.node()
            node["search_filter"] = panel[1]
            cluster["panel"][panel[0]] = node
        return cluster

    @staticmethod
    def preferences():
        """default preferences"""
        return {"same_dag": False, "same_non_dag": False, "preset_radial": True, "preset_hud": True, "preset_hud_s": 2,
                "preset_hud_b": 2, "default_lmb": "", "default_lmb_type": 0, "default_mmb": "", "default_mmb_type": 0}


class UserData(object):
    """read and write data into hdd"""

    @classmethod
    def load(cls):
        """load from hdd"""
        cls._createDirs()
        preferences, cluster = DefaultData.preferences(), DefaultData.cluster()
        try:  # check protocol version
            if os.path.isfile(location + "/UserData.mm"):  # import old data
                cls.write(*cls._import())
            data = pickle.load(open(location + "/data/data.mm", "rb"))
            preferences, cluster = data[1:]
            if data[0] != protocol:     # update data to current protocol
                cluster_empty = DefaultData.cluster()
                cluster_empty.update(cluster)
                for nodes in cluster_empty.values():
                    for node in nodes:
                        node_empty = DefaultData.node()
                        node_empty.update(nodes[node])
                        nodes[node] = node_empty
                cluster = cluster_empty
        except:
            pass
        finally:
            return preferences, cluster

    @classmethod
    def write(cls, preferences, nodes):
        """store data into file"""
        cls._createDirs()
        pickle.dump((protocol, preferences, nodes), open(location + "/data/data.mm", "wb"))

    @staticmethod
    def _createDirs():
        """create default directories for data"""
        for directory in location + "/menus", location + "/commands":
            if os.path.isfile(directory):
                os.remove(directory)
            if not os.path.isdir(directory):
                os.makedirs(directory)
            if not os.path.isfile(directory + "/__init__.py"):
                open(directory + "/__init__.py", "w").close()

    @staticmethod
    def _import():
        """import from version 1.0.5"""

        def loadNode(is_panel=False, add_prefix=False):
            """convert nodes into cluster one"""
            nodes = {}
            for i in xrange(ord(file_data.read(1))):
                node = DefaultData.node()
                node["menu"] = file_data.read(ord(file_data.read(1)))[:-4]
                node["command"] = file_data.read(ord(file_data.read(1)))
                node["menu_type"] = ord(file_data.read(1))
                if ord(file_data.read(1)) and os.path.isfile("%s/scripts/%s.script" % (location, node["command"])):
                    with open("%s/scripts/%s.script" % (location, node["command"]), "r") as command_file:
                        node["command"] = command_file.read()
                if is_panel:
                    node["search_filter"] = ord(file_data.read(1))
                    node["search_name"] = max(0, ord(file_data.read(1)))
                    panel_name = file_data.read(ord(file_data.read(1))).rstrip(string.digits)
                    nodes["any" if panel_name == "AllPanels" else panel_name] = node
                else:
                    nodes[("any " if add_prefix else "") + file_data.read(ord(file_data.read(1)))] = node
            return nodes

        preferences, cluster = DefaultData.preferences(), DefaultData.cluster()
        try:
            with open(location + "/UserData.mm", "rb") as file_data:
                assert ord(file_data.read(1)) == 1  # version 1.0.5 supported only
                ord(file_data.read(1))  # save into file (obsolete)
                preferences["same_non_dag"] = bool(ord(file_data.read(1)))
                preferences["same_dag"] = bool(ord(file_data.read(1)))
                ord(file_data.read(1))  # check for errors (obsolete)
                preferences["preset_hud"] = bool(ord(file_data.read(1)))
                preferences["preset_hud_s"] = ord(file_data.read(1))
                preferences["preset_hud_b"] = ord(file_data.read(1))
                preferences["preset_radial"] = bool(ord(file_data.read(1)))
                preferences["default_lmb"] = file_data.read(ord(file_data.read(1)))
                preferences["default_mmb"] = file_data.read(ord(file_data.read(1)))
                cluster["panel"] = loadNode(True)
                cluster["name"] = loadNode(False)
                cluster["non dag"] = loadNode(False, True)
                cluster["dag"] = loadNode(False, True)
                cluster["tool"] = loadNode(False, True)
                cluster["preset"] = loadNode(False)
        finally:
            os.remove(location + "/UserData.mm")
            shutil.rmtree(location + "/scripts", ignore_errors=True)
            return preferences, cluster

    @classmethod
    def exporter(cls, *args):
        """export to zip archive"""
        cls.write(*args)
        zip_file = zipfile.ZipFile(cmds.fileDialog2(fm=0, ff="*.zip")[0], "w")
        for directory in "/data", "/menus", "/commands":
            full_dir = location + directory
            files = filter(lambda f: os.path.isfile("%s/%s" % (full_dir, f)), os.listdir(full_dir))
            for x in files:
                zip_file.write("%s/%s" % (full_dir, x), "%s/%s" % (directory, x))
        marking_menu = cmds.internalVar(umm=True)
        for m in os.listdir(marking_menu):
            if os.path.isfile("%s/%s" % (marking_menu, m)):
                zip_file.write("%s/%s" % (marking_menu, m), "markingMenus/%s" % m)
        zip_file.close()

    @classmethod
    def importer(cls):
        """import from zip archive"""
        zip_file = zipfile.ZipFile(cmds.fileDialog2(fm=1, ff="*.zip")[0], "r")
        for f in zip_file.namelist():
            if f.find("markingMenus/") == 0:
                zip_file.extract(f, cmds.internalVar(upd=True))
            else:
                zip_file.extract(f, location)
        return cls.load()


class Engine(object):
    """marking menu manager"""
    EMPTY_NODE = DefaultData.node()
    SEARCH_NAME = 0b100
    SEARCH_NON_DAG = 0b010
    SEARCH_DAG = 0b001
    NAME_PREFIX = 0
    NAME_SUFFIX = 1
    NAME_ANY = 2
    NAME_ABSOLUTE = 3
    COMPONENTS = {0: 'handle', 3: 'joint', 11: 'CurvesOnSurface', 28: 'ControlVertices', 30: 'EditPoints',
                  31: 'PolygonVertices', 32: 'PolygonEdges', 34: 'PolygonFace', 35: 'PolygonUVs',
                  36: 'SubdivisionMeshPoints', 37: 'SubdivisionMeshEdges', 38: 'SubdivisionMeshFaces',
                  39: 'CurveParameterPoints', 40: 'CurveKnot', 41: 'SurfaceParameterPoints', 42: 'SurfaceKnot',
                  43: 'SurfaceRange', 44: 'TrimSurfaceEdge', 45: 'SurfaceIsoparms', 46: 'LatticePoints',
                  68: 'SubdivisionSurface', 70: 'PolygonVertexFace', 72: 'NURBSSurfaceFace', 73: 'SubdivisionMeshUVs'}

    def __init__(self):
        self.preferences, self.cluster = UserData.load()
        self._is_menu_open = False      # marks if menu been opened
        self._preset_changed = False    # marks if preset was changed in current session
        self._preset_modifiers = {}     # modifiers for last preset menu
        self._last_preset = self.EMPTY_NODE
        self._last_selected = self.EMPTY_NODE

    def _postMenu(self, *args):
        self._is_menu_open = True

    def findDagKey(self):
        """find selected dag keys"""
        selected = []
        for mask in self.COMPONENTS:  # search by mask components
            if cmds.filterExpand(sm=mask, ex=False):
                selected.append(self.COMPONENTS[mask])
                if len(selected) == 2:
                    break
        else:
            objects = cmds.ls(sl=True, an=True, o=True)
            for node in objects:
                child = cmds.listRelatives(node, s=True, f=True)
                if not child:
                    continue
                child = cmds.nodeType(child[0])
                if child not in selected or self.preferences["same_dag"]:
                    selected.append(child)
                    if len(selected) == 2:
                        break
        selected.sort()
        return selected

    def findNonDagKey(self):
        """find non dag selected keys"""
        selected = []
        objects = cmds.ls(sl=True, an=True, o=True)
        for node in objects:
            child = cmds.nodeType(node)
            if child not in selected or self.preferences["same_non_dag"]:
                selected.append(child)
                if len(selected) == 2:
                    break
        selected.sort()
        return selected

    @staticmethod
    def _findDagNonDagNode(selected, nodes):
        """find node for selected dag and non-dag nodes"""
        if not selected:
            return None
        panel = cmds.getPanel(underPointer=True)
        for panel in panel, panel.rstrip(string.digits), "any":
            if len(selected) == 2 and "%s %s %s" % (panel, selected[0], selected[1]) in nodes:
                return nodes["%s %s %s" % (panel, selected[0], selected[1])]
            elif "%s %s" % (panel, selected[0]) in nodes:
                return nodes["%s %s" % (panel, selected[0])]
            elif len(selected) == 2 and "%s %s" % (panel, selected[1]) in nodes:
                return nodes["%s %s" % (panel, selected[1])]

    def _findNameNode(self, search_type):
        """return node for selected name"""
        try:
            selected = cmds.ls(sl=True)[0]
        except IndexError:
            return None
        if search_type == self.NAME_PREFIX:  # by prefix
            for name in self.cluster["name"]:
                if selected.find(name) == 0:
                    return self.cluster["name"][name]
        elif search_type == self.NAME_SUFFIX:  # by suffix
            for name in self.cluster["name"]:
                if selected.rfind(name) == len(selected) - len(name):
                    return self.cluster["name"][name]
        elif search_type == self.NAME_ANY:  # any search
            for name in self.cluster["name"]:
                if name in selected:
                    return self.cluster["name"][name]
        elif search_type == self.NAME_ABSOLUTE and selected in self.cluster["name"]:  # absolute match
            return self.cluster["name"][selected]

    def _findSelectedNode(self):
        """find selected node of dag, non-dag and names"""
        panel = cmds.getPanel(underPointer=True)
        for panel in panel, panel.rstrip(string.digits), "any":
            if panel in self.cluster["panel"]:
                panel_node = self.cluster["panel"][panel]
                break
        else:
            self.cluster["panel"]["any"] = DefaultData.node()
            return self.EMPTY_NODE

        if panel_node["search_filter"] & self.SEARCH_NAME:
            node = self._findNameNode(panel_node["search_name"])
            if node:
                return node
        if panel_node["search_filter"] & self.SEARCH_NON_DAG:
            node = self._findDagNonDagNode(self.findNonDagKey(), self.cluster["non dag"])
            if node:
                return node
        if panel_node["search_filter"] & self.SEARCH_DAG:
            node = self._findDagNonDagNode(self.findDagKey(), self.cluster["dag"])
            if node:
                return node
        return panel_node

    def _findToolNode(self):
        """find current tool node"""
        context = cmds.currentCtx()  # context marking menu
        panel = cmds.getPanel(underPointer=True)
        for panel in panel, panel.rstrip(string.digits), "any":
            if "%s %s" % (panel, context) in self.cluster["tool"]:
                return self.cluster["tool"]["%s %s" % (panel, context)]
        return self.EMPTY_NODE

    def pressSelected(self, **kwargs):
        """press trigger for selected nodes and tools"""
        self._is_menu_open = False
        self._last_selected = self.EMPTY_NODE
        # build for current tool menu
        tool_node = self._findToolNode()
        if tool_node["menu"]:
            Menu.show(tool_node["menu_type"], tool_node["menu"], self.preferences, b=Menu.MMB,  pmc=self._postMenu,
                      **kwargs)
        else:
            Menu.show(self.preferences["default_mmb_type"], self.preferences["default_mmb"], self.preferences,
                      b=Menu.MMB, pmc=self._postMenu, **kwargs)
        # build for current selection menu
        self._last_selected = self._findSelectedNode()
        if self._last_selected["menu"]:
            Menu.show(self._last_selected["menu_type"], self._last_selected["menu"], self.preferences, b=Menu.LMB,
                      pmc=self._postMenu, **kwargs)
        else:
            Menu.show(self.preferences["default_lmb_type"], self.preferences["default_lmb"], self.preferences,
                      b=Menu.LMB, pmc=self._postMenu, **kwargs)

    def releaseSelected(self):
        """release trigger no-click command in case menu wasn't opened"""
        Menu.hide()
        if not self._is_menu_open or self._last_selected["command_always"]:
            Command.run(self._last_selected["command"], self._last_selected["command_type"])

    def pressPreset(self, **kwargs):
        """press trigger for preset press"""
        self._is_menu_open = False
        self._last_selected = self.EMPTY_NODE
        self._preset_changed = False
        self._preset_modifiers = kwargs     # store ctrl, alt and shift modifiers
        Menu.show(Menu.PRESET, self.cluster["preset"], self.preferences, b=Menu.MMB, pmc=self._postMenu, **kwargs)
        Menu.show(self._last_preset["menu_type"], self._last_preset["menu"], self.preferences, b=Menu.LMB,
                  pmc=self._postMenu, **kwargs)

    def releasePreset(self):
        """release trigger for preset"""
        Menu.hide()
        if not self._preset_changed and (not self._is_menu_open or self._last_preset["command_always"]):
            Command.run(self._last_preset["command"], self._last_preset["command_type"])

    def setPreset(self, preset):
        """change current preset. do not call marking menu"""
        self._preset_changed = True     # do not call no-click command this release
        self._last_preset = self.cluster["preset"][preset]
        if cmds.headsUpDisplay('MMtoKeyHUD', ex=True):
            cmds.headsUpDisplay('MMtoKeyHUD', remove=True)
        Menu.show(self._last_preset["menu_type"], self._last_preset["menu"], self.preferences, b=Menu.LMB,
                  pmc=self._postMenu, **self._preset_modifiers)
        if self.preferences["preset_hud"]:
            cmds.headsUpDisplay('MMtoKeyHUD', s=self.preferences["preset_hud_s"], b=self.preferences["preset_hud_b"],
                                label='MMtoKey preset', ba='center', lfs='large', dfs='large', c=lambda: preset,
                                ev='NewSceneOpened')

    def pressCustom(self, **kwargs):
        self._is_menu_open = False
        self._last_selected = self.EMPTY_NODE
        Menu.show(preferences=self.preferences, b=Menu.LMB, pmc=self._postMenu, **kwargs)

    def releaseCustom(self, command_always=False, **kwargs):
        """release trigger for custom """
        Menu.hide()
        if not self._is_menu_open or command_always:
            Command.run(**kwargs)
