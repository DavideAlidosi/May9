import os
try:    # under Maya 2017
    from PySide.QtCore import *
    from PySide.QtGui import *
except ImportError:     # Maya 2017 and above
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
import maya.cmds as cmds
import UtilsQT


location = os.path.dirname(__file__)


class MainWindow(QMainWindow):
    """Hotkey maker"""
    COMMANDS = (("selected", "selected"), ("selected", "custom"), ("custom", "custom"), ("preset", "preset"),
                ("preset", "custom"))

    def __init__(self):
        QMainWindow.__init__(self, UtilsQT.wrapWidget())
        self.ui = UtilsQT.loadUI(location + "/resources/ui/HotkeyMaker.ui", location + "/resources/ui", self)
        self.setFixedSize(230, 360)
        self.setWindowTitle("MMtoKey Hotkey Maker")
        UtilsQT.reloadWidget("MMtoKeyHotkey", self)
        self.setWindowFlags(Qt.Tool)

        # signals
        self.ui.btn_create.released.connect(self._hotkey)
        self.ui.cmb_method.currentIndexChanged.connect(self._changeType)
        self._changeType()
        self.show()

    def _hotkey(self):
        """create hotkey"""
        name = self.ui.line_name.text()
        if cmds.runTimeCommand('%s_press' % name, exists=True):
            if cmds.confirmDialog(m='name is not unique! replace?', b=['yes', 'no']) == 'no':
                return
            else:
                cmds.runTimeCommand('%s_press' % name, delete=True, e=True)
                cmds.runTimeCommand('%s_release' % name, delete=True, e=True)
        hotkey = self.ui.line_hotkey.text().lower()
        if not hotkey:
            return

        # build menu
        ctrl = self.ui.chb_ctrl.isChecked()
        alt = self.ui.chb_alt.isChecked()
        shift = self.ui.chb_alt.isChecked()
        if self.COMMANDS[self.ui.cmb_method.currentIndex()][0] == "custom":
            press = "MMtoKey.pressCustom(ctl=%s, alt=%s, sh=%s, menu_type=%i, menu_name='%s')"
            press %= ctrl, alt, shift, self.ui.cmb_menu.currentIndex(), self.ui.line_menu.text()
        elif self.COMMANDS[self.ui.cmb_method.currentIndex()][0] == "selected":
            press = "MMtoKey.pressSelected(ctl=%s, alt=%s, sh=%s)" % (ctrl, alt, shift)
        else:
            press = "MMtoKey.pressPreset(ctl=%s, alt=%s, sh=%s)" % (ctrl, alt, shift)

        # release command
        if self.COMMANDS[self.ui.cmb_method.currentIndex()][1] == "custom":
            release = "MMtoKey.releaseCustom(command_always=%s, command='%s', language=%i)"
            release %= (self.ui.cmb_menu.currentIndex(), self.ui.line_command.text().replace("'", "\\'"),
                        self.ui.cmb_command.currentIndex())
        elif self.COMMANDS[self.ui.cmb_method.currentIndex()][1] == "selected":
            release = "MMtoKey.releaseSelected()"
        else:
            release = "MMtoKey.releasePreset()"

        # create runtime and name commands
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

    def _changeType(self, index=0):
        """change type combobox"""
        self.ui.cmb_command.setEnabled(self.COMMANDS[index][1] == "custom")
        self.ui.line_command.setEnabled(self.COMMANDS[index][1] == "custom")
        self.ui.chb_command.setEnabled(self.COMMANDS[index][1] == "custom")
        self.ui.line_menu.setEnabled(self.COMMANDS[index][0] == "custom")
        self.ui.cmb_menu.setEnabled(self.COMMANDS[index][0] == "custom")
