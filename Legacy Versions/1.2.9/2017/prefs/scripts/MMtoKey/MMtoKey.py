import maya.cmds as cmds
import maya.mel as mel
import struct
import os


class Node(object):

    def __init__(self, menu='', command='', language=0, outside=0):
        self.menu = menu
        self.command = command
        self.language = language
        self.outside = outside

    def __del__(self):
        if self.outside:
            try:
                os.remove('%s/scripts/%s.script' % (MMtoKey.PATH, self.command))
            except WindowsError:
                pass

    def getCommand(self):
        try:
            if self.outside:
                open_file = open('%s/scripts/%s.script' % (MMtoKey.PATH, self.command), 'r')
                command = open_file.read()
                open_file.close()
                return self.language, command
            else:
                return self.language, self.command
        except IOError:
            self.command = ''
            self.outside = 0
            return self.language, ''

    def setCommand(self, command, language, outside):
        self.command = command
        self.language = language
        self.outside = outside

    def writeNode(self, node_name, file_save):
        file_save.write(b'%s' * 8 % (struct.pack('B', len(self.menu)), self.menu,
                        struct.pack('B', len(self.command)), self.command,
                        struct.pack('B', self.language), struct.pack('B', self.outside),
                        struct.pack('B', len(node_name)), node_name))

    def getCommandName(self):
        return '%s.script' % self.command if self.outside else ''


class PanelNode(Node):

    def __init__(self, menu='', command='', language=0, outside=0, search=6, names=0):
        Node.__init__(self, menu, command, language, outside)
        self.search = search
        self.names = names

    def writeNode(self, node_name, file_save):
        file_save.write(b'%s' * 10 % (struct.pack('B', len(self.menu)), self.menu,
                        struct.pack('B', len(self.command)), self.command,
                        struct.pack('B', self.language), struct.pack('B', self.outside),
                        struct.pack('B', self.search), struct.pack('B', self.names),
                        struct.pack('B', len(node_name)), node_name))


class MMtoKey(object):

    PATH = os.path.dirname(__file__)
    EMPTY_NODE = Node()
    POSITION = 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'
    COMPONENTS = {0: 'handle', 3: 'joint', 11: 'CurvesOnSurface', 28: 'ControlVertices', 30: 'EditPoints',
                  31: 'PolygonVertices', 32: 'PolygonEdges', 34: 'PolygonFace', 35: 'PolygonUVs',
                  36: 'SubdivisionMeshPoints', 37: 'SubdivisionMeshEdges', 38: 'SubdivisionMeshFaces',
                  39: 'CurveParameterPoints', 40: 'CurveKnot', 41: 'SurfaceParameterPoints', 42: 'SurfaceKnot',
                  43: 'SurfaceRange', 44: 'TrimSurfaceEdge', 45: 'SurfaceIsoparms', 46: 'LatticePoints',
                  68: 'SubdivisionSurface', 70: 'PolygonVertexFace', 72: 'NURBSSurfaceFace', 73: 'SubdivisionMeshUVs'}
    PANELS = ('1AllPanels', '6blendShapePanel1', '6clipEditorPanel1', '6componentEditorPanel1', '6visorPanel1',
              '6createNodePanel1', '6dopeSheetPanel1', '6dynPaintScriptedPanel', '6dynRelEdPanel1', '6graphEditor1',
              '6hyperGraphPanel1', '6hyperShadePanel1', '6nodeEditorPanel1', '6outlinerPanel1', '6scriptEditorPanel1',
              '1polyTexturePlacementPanel1', '6profilerPanel1', '6referenceEditorPanel1', '6relationshipPanel1',
              '6renderView', '6sequenceEditorPanel1')

    def __init__(self):
        if not os.path.isdir('%s/scripts' % self.PATH):
            os.makedirs('%s/scripts' % self.PATH)
        try:
            file_data = open('%s/UserData.mm' % MMtoKey.PATH, 'rb')
            version = ord(file_data.read(1))
            file_reader = self.__getattribute__('_import_%i' % version)
            file_reader(file_data)
        except (IOError, AttributeError, TypeError):
            self.pref_save_file = 0
            self.pref_same_nondag = 0
            self.pref_same_dag = 0
            self.pref_check_errors = 1
            self.pref_hud = 1
            self.pref_hud_x = 2
            self.pref_hud_y = 2
            self.pref_preset_radial = 1
            self.pref_special_0 = ''
            self.pref_special_1 = ''

            self.DATA_PANEL = {}
            self.DATA_NAME = {}
            self.DATA_NONDAG = {}
            self.DATA_DAG = {}
            self.DATA_TOOL = {}
            self.DATA_PRESET = {}
            for node in self.PANELS:
                self.DATA_PANEL[node[1:]] = PanelNode(search=int(node[0]))
        finally:
            self._is_open_menu = False
            self._current_node = None
            self._current_node_preset = self.EMPTY_NODE
            self.activePreset = ''

    @staticmethod
    def _cleanMenu():
        while cmds.popupMenu('MMtoKey_LMB', exists=True):
            cmds.deleteUI('MMtoKey_LMB')
        while cmds.popupMenu('MMtoKey_MMB', exists=True):
            cmds.deleteUI('MMtoKey_MMB')

    def _import_0(self, file_data):
        def asInt():
            return ord(file_data.read(1))

        def asStr():
            return file_data.read(ord(file_data.read(1)))

        def loadNode():
            nodes = {}
            for i in xrange(asInt()):
                nodes[asStr()] = Node(asStr(), asStr(), asInt(), asInt())
            return nodes

        def loadPanelNode():
            nodes = {}
            for i in xrange(asInt()):
                nodes[asStr()] = PanelNode(asStr(), asStr(), asInt(), asInt(), asInt(), asInt())
            return nodes

        self.pref_save_file = asInt()   # read preferences
        self.pref_same_nondag = asInt()
        self.pref_same_dag = asInt()
        self.pref_check_errors = asInt()
        asInt()
        self.pref_hud = asInt()
        self.pref_hud_x = asInt()
        self.pref_hud_y = asInt()
        self.pref_preset_radial = asInt()
        self.pref_special_0 = asStr()
        self.pref_special_1 = ''

        self.DATA_PANEL = loadPanelNode()   # read nodes
        self.DATA_NAME = loadNode()
        self.DATA_NONDAG = loadNode()
        self.DATA_DAG = loadNode()
        self.DATA_TOOL = loadNode()
        self.DATA_PRESET = loadNode()

    def _import_1(self, file_data):
        def asInt():
            return ord(file_data.read(1))

        def asStr():
            return file_data.read(ord(file_data.read(1)))

        def loadNode():
            nodes = {}
            for i in xrange(asInt()):
                nodes[asStr()] = Node(asStr(), asStr(), asInt(), asInt())
            return nodes

        def loadPanelNode():
            nodes = {}
            for i in xrange(asInt()):
                nodes[asStr()] = PanelNode(asStr(), asStr(), asInt(), asInt(), asInt(), asInt())
            return nodes

        self.pref_save_file = asInt()   # read preferences
        self.pref_same_nondag = asInt()
        self.pref_same_dag = asInt()
        self.pref_check_errors = asInt()
        self.pref_hud = asInt()
        self.pref_hud_x = asInt()
        self.pref_hud_y = asInt()
        self.pref_preset_radial = asInt()
        self.pref_special_0 = asStr()
        self.pref_special_1 = asStr()

        self.DATA_PANEL = loadPanelNode()   # read nodes
        self.DATA_NAME = loadNode()
        self.DATA_NONDAG = loadNode()
        self.DATA_DAG = loadNode()
        self.DATA_TOOL = loadNode()
        self.DATA_PRESET = loadNode()

    def saveNodes(self):
        file_write = open('%s/UserData.mm' % MMtoKey.PATH, 'wb')
        file_write.write(b'\x01')
        for b in (self.pref_save_file, self.pref_same_nondag, self.pref_same_dag, self.pref_check_errors,
                  self.pref_hud, self.pref_hud_x, self.pref_hud_y, self.pref_preset_radial):
            file_write.write(struct.pack('B', b))
        file_write.write(b'%s%s' % (struct.pack('B', len(self.pref_special_0)), self.pref_special_0))
        file_write.write(b'%s%s' % (struct.pack('B', len(self.pref_special_1)), self.pref_special_1))
        all_scripts = set()
        for nodes in self.DATA_PANEL, self.DATA_NAME, self.DATA_NONDAG, self.DATA_DAG, self.DATA_TOOL, self.DATA_PRESET:
            file_write.write(struct.pack('B', len(nodes)))
            for name in nodes:
                nodes[name].writeNode(name, file_write)
                all_scripts.add(nodes[name].getCommandName())

        if self.pref_check_errors:    # remove unused scripts
            for script in os.listdir('%s/scripts' % MMtoKey.PATH):
                if script not in all_scripts:
                    os.remove('%s/scripts/%s' % (MMtoKey.PATH, script))
        file_write.close()

    def findDagKey(self):
        selected = []
        for mask in self.COMPONENTS:       # search by mask components
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
                if child not in selected or self.pref_same_dag:
                    selected.append(child)
                    if len(selected) == 2:
                        break
        selected.sort()
        return selected

    def findNonDagKey(self):
        selected = []
        objects = cmds.ls(sl=True, an=True, o=True)
        for node in objects:
            child = cmds.nodeType(node)
            if child not in selected or self.pref_same_nondag:
                selected.append(child)
                if len(selected) == 2:
                    break
        selected.sort()
        return selected

    @staticmethod
    def _findNodeObject(selected, nodes):
        try:
            if ' '.join(selected) in nodes:
                return nodes[' '.join(selected)]
            elif selected[1] in nodes:
                return nodes[selected[1]]
            elif selected[0] in nodes:
                return nodes[selected[0]]
        except (AttributeError, IndexError):
            return None

    def _findNodeName(self, search_type):
        try:
            selected = cmds.ls(sl=True)[0]
        except IndexError:
            return None

        if search_type == 1:     # by prefix
            for name in self.DATA_NAME:
                if selected.find(name) == 0:
                    return self.DATA_NAME[name]

        elif search_type == 2:   # by suffix
            for name in self.DATA_NAME:
                if selected.rfind(name) == len(selected) - len(name):
                    return self.DATA_NAME[name]

        elif search_type == 3:   # any search
            for name in self.DATA_NAME:
                if name in selected:
                    return self.DATA_NAME[name]

        elif search_type == 4 and selected in self.DATA_NAME:    # absolute match
            return self.DATA_NAME[selected]

    def _findNode(self):
        panel = cmds.getPanel(underPointer=True)
        try:
            preset = self.DATA_PANEL[panel] if panel in self.DATA_PANEL else self.DATA_PANEL['AllPanels']
        except KeyError:
            self.DATA_PANEL['AllPanels'] = PanelNode()
            return self.EMPTY_NODE

        if preset.search & 0b100 and preset.names:     # search by name
            node = self._findNodeName(preset.names)
            if node:
                return node

        if preset.search & 0b10:      # search non-dag
            node = self._findNodeObject(self.findNonDagKey(), self.DATA_NONDAG)
            if node:
                return node

        if preset.search & 0b1:       # search dag
            node = self._findNodeObject(self.findDagKey(), self.DATA_DAG)
            if node:
                return node
        return preset

    def press_selected(self, menu, **mod):
        self._is_open_menu = False
        self._current_node = self.EMPTY_NODE
        self._cleanMenu()
        context = cmds.currentCtx()     # context marking menu
        cmds.contextInfo(context, title=True)
        cmds.popupMenu('MMtoKey_MMB', b=2, aob=True, mm=True, p=self._getPanel(), pmc=self._openMarkingMenu, **mod)
        if context in self.DATA_TOOL and self.DATA_TOOL[context].menu:
            mel.eval('source "menu_%s";' % self.DATA_TOOL[context].menu)
        elif self.pref_special_1:
            mel.eval('source "menu_%s";' % self.pref_special_1)

        # common menu
        cmds.popupMenu('MMtoKey_LMB', b=1, aob=True, mm=True, p=self._getPanel(), pmc=self._openMarkingMenu, **mod)
        if menu:
            mel.eval('source "menu_%s";' % menu)
            return
        self._current_node = self._findNode()
        if self._current_node.menu:
            mel.eval('source "menu_%s";' % self._current_node.menu)
        elif self.pref_special_0:
            mel.eval('source "menu_%s";' % self.pref_special_0)

    def release_selected(self, command, language):
        self._cleanMenu()
        if self._is_open_menu:
            return
        if not command:
            language, command = self._current_node.getCommand()
        if language:
            exec(command)
        else:
            mel.eval(command)

    def press_preset(self, **mod):
        self._is_open_menu = False
        self._cleanMenu()
        position = self.POSITION if self.pref_preset_radial else ()
        cmds.popupMenu('MMtoKey_MMB', b=2, aob=True, mm=True, p=self._getPanel(), pmc=self._openMarkingMenu, **mod)
        i = 0
        for preset in self.DATA_PRESET:
            try:
                cmds.menuItem(stp='python', c='MMtoKey.mmtokey.changePreset("%s")' % preset, l=preset, rp=position[i])
                i += 1
            except IndexError:
                cmds.menuItem(stp='python', c='MMtoKey.mmtokey.changePreset("%s")' % preset, l=preset)

        if self._current_node_preset.menu:
            cmds.popupMenu('MMtoKey_LMB', b=1, aob=True, mm=True, p=self._getPanel(), pmc=self._openMarkingMenu, **mod)
            mel.eval('source "menu_%s";' % self._current_node_preset.menu)

    def release_preset(self):
        self._cleanMenu()
        if self._is_open_menu:
            return
        language, command = self._current_node_preset.getCommand()
        if language:
            exec(command)
        else:
            mel.eval(command)

    def changePreset(self, preset):
        self.activePreset = preset
        self._current_node_preset = self.DATA_PRESET[preset]
        if cmds.headsUpDisplay('MMtoKeyHUD', ex=True):
            cmds.headsUpDisplay('MMtoKeyHUD', remove=True)
        if self.pref_hud:
            cmds.headsUpDisplay('MMtoKeyHUD', s=self.pref_hud_x, b=self.pref_hud_y, l='MMtoKey preset', ba='center',
                                lfs='large', dfs='large', c=self._activePreset, ev='NewSceneOpened')

    def _activePreset(self):
        print "active"
        return self.activePreset

    def _openMarkingMenu(self, *args):
        self._is_open_menu = True

    @staticmethod
    def _getPanel():
        return cmds.layout(cmds.getPanel(up=True), q=True, p=True)
