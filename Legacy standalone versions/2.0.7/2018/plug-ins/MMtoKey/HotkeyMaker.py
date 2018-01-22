try:    # under Maya 2017
    from PySide.QtCore import *
    from PySide.QtGui import *
except ImportError:     # Maya 2017 and above
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
import maya.cmds as cmds
import QtWrapper


class HotkeyMaker(QMainWindow):
    """Hotkey maker"""
    COMMANDS = (("selected", "selected"), ("selected", "custom"), ("custom", "custom"), ("preset", "preset"),
                ("preset", "custom"))

    def __init__(self):
        QMainWindow.__init__(self, QtWrapper.wrapWidget())
        self.setFixedSize(200, 350)
        self.setWindowTitle("MMtoKey Hotkey Maker")
        if cmds.window('MMtoKeyHotkey', ex=True):
            cmds.deleteUI('MMtoKeyHotkey')
        self.setObjectName("MMtoKeyHotkey")
        self.setWindowFlags(Qt.Tool)

        # QT designer
        self.layoutWidget = QWidget(self)
        self.layoutWidget.setGeometry(QRect(10, 10, 180, 330))
        grid_layout = QGridLayout(self.layoutWidget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(self.layoutWidget)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        label.setSizePolicy(size_policy)
        label.setMinimumSize(QSize(180, 20))
        label.setAlignment(Qt.AlignCenter)
        grid_layout.addWidget(label, 2, 0, 1, 3)
        self._cmb_menu = QComboBox(self.layoutWidget)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._cmb_menu.setSizePolicy(size_policy)
        self._cmb_menu.setMinimumSize(QSize(180, 20))
        grid_layout.addWidget(self._cmb_menu, 3, 0, 1, 3)
        self._line_menu = QLineEdit(self.layoutWidget)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._line_menu.setSizePolicy(size_policy)
        self._line_menu.setMinimumSize(QSize(180, 20))
        grid_layout.addWidget(self._line_menu, 4, 0, 1, 3)
        label_2 = QLabel(self.layoutWidget)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        label_2.setSizePolicy(size_policy)
        label_2.setMinimumSize(QSize(180, 20))
        label_2.setAlignment(Qt.AlignCenter)
        grid_layout.addWidget(label_2, 5, 0, 1, 3)
        self._cmb_command = QComboBox(self.layoutWidget)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._cmb_command.setSizePolicy(size_policy)
        self._cmb_command.setMinimumSize(QSize(180, 20))
        grid_layout.addWidget(self._cmb_command, 6, 0, 1, 3)
        self._cmb_method = QComboBox(self.layoutWidget)
        self._cmb_method.setMinimumSize(QSize(180, 20))
        grid_layout.addWidget(self._cmb_method, 1, 0, 1, 3)
        self._line_name = QLineEdit(self.layoutWidget)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._line_name.setSizePolicy(size_policy)
        self._line_name.setMinimumSize(QSize(120, 20))
        grid_layout.addWidget(self._line_name, 0, 0, 1, 2)
        self._line_command = QLineEdit(self.layoutWidget)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._line_command.setSizePolicy(size_policy)
        self._line_command.setMinimumSize(QSize(180, 20))
        grid_layout.addWidget(self._line_command, 7, 0, 1, 3)
        label_1 = QLabel(self.layoutWidget)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        label_1.setSizePolicy(size_policy)
        label_1.setMinimumSize(QSize(120, 20))
        label_1.setAlignment(Qt.AlignCenter)
        grid_layout.addWidget(label_1, 10, 1, 1, 2)
        self._chb_alt = QCheckBox(self.layoutWidget)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._chb_alt.setSizePolicy(size_policy)
        self._chb_alt.setMinimumSize(QSize(60, 20))
        grid_layout.addWidget(self._chb_alt, 9, 2, 1, 1)
        self._chb_ctrl = QCheckBox(self.layoutWidget)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._chb_ctrl.setSizePolicy(size_policy)
        self._chb_ctrl.setMinimumSize(QSize(60, 20))
        grid_layout.addWidget(self._chb_ctrl, 9, 1, 1, 1)
        button = QPushButton(self.layoutWidget)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.setSizePolicy(size_policy)
        button.setMinimumSize(QSize(60, 20))
        grid_layout.addWidget(button, 11, 0, 1, 1)
        self._line_hotkey = QLineEdit(self.layoutWidget)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._line_hotkey.setSizePolicy(size_policy)
        self._line_hotkey.setMinimumSize(QSize(60, 20))
        self._line_hotkey.setMaxLength(1)
        grid_layout.addWidget(self._line_hotkey, 10, 0, 1, 1)
        self._chb_shift = QCheckBox(self.layoutWidget)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._chb_shift.setSizePolicy(size_policy)
        self._chb_shift.setMinimumSize(QSize(60, 20))
        grid_layout.addWidget(self._chb_shift, 9, 0, 1, 1)
        label_3 = QLabel(self.layoutWidget)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        label_3.setSizePolicy(size_policy)
        label_3.setMinimumSize(QSize(60, 20))
        label_3.setAlignment(Qt.AlignCenter)
        grid_layout.addWidget(label_3, 0, 2, 1, 1)
        self._chb_command = QCheckBox(self.layoutWidget)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._chb_command.setSizePolicy(size_policy)
        self._chb_command.setMinimumSize(QSize(180, 20))
        grid_layout.addWidget(self._chb_command, 8, 0, 1, 1)

        # my code
        self._cmb_method.addItems(["menu %s, command %s" % d for d in self.COMMANDS])
        self._cmb_menu.addItems(["mel file", "python module"])
        self._cmb_command.addItems(["mel string", "python string", "python module"])
        label.setText("custom marking menu")
        label_1.setText("hotkey")
        label_2.setText("custom no-click command")
        label_3.setText("name")
        self._chb_alt.setText("alt")
        self._chb_shift.setText("shift")
        self._chb_ctrl.setText("ctrl")
        self._chb_command.setText("run always after release")
        button.setText("create")
        self._changeType()

        # signals
        button.released.connect(self._hotkey)
        self._cmb_method.currentIndexChanged.connect(self._changeType)
        self.show()

    def _hotkey(self):
        """create hotkey"""
        name = self._line_name.text()
        if cmds.runTimeCommand('%s_press' % name, exists=True):
            if cmds.confirmDialog(m='name is not unique! replace?', b=['yes', 'no']) == 'no':
                return
            else:
                cmds.runTimeCommand('%s_press' % name, delete=True, e=True)
                cmds.runTimeCommand('%s_release' % name, delete=True, e=True)
        hotkey = self._line_hotkey.text().lower()
        if not hotkey:
            return

        # build menu
        ctrl = self._chb_ctrl.isChecked()
        alt = self._chb_alt.isChecked()
        shift = self._chb_alt.isChecked()
        if self.COMMANDS[self._cmb_method.currentIndex()][0] == "custom":
            press = "MMtoKey.pressCustom(ctl=%s, alt=%s, sh=%s, menu_type=%i, menu_name='%s')"
            press %= ctrl, alt, shift, self._cmb_menu.currentIndex(), self._line_menu.text()
        elif self.COMMANDS[self._cmb_method.currentIndex()][0] == "selected":
            press = "MMtoKey.pressSelected(ctl=%s, alt=%s, sh=%s)" % (ctrl, alt, shift)
        else:
            press = "MMtoKey.pressPreset(ctl=%s, alt=%s, sh=%s)" % (ctrl, alt, shift)

        # release command
        if self.COMMANDS[self._cmb_method.currentIndex()][1] == "custom":
            release = "MMtoKey.releaseCustom(command_always=%s, command='%s', language=%i)"
            release %= (self._cmb_menu.currentIndex(), self._line_command.text().replace("'", "\\'"),
                        self._cmb_command.currentIndex())
        elif self.COMMANDS[self._cmb_method.currentIndex()][1] == "selected":
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
        self._cmb_command.setEnabled(self.COMMANDS[index][1] == "custom")
        self._line_command.setEnabled(self.COMMANDS[index][1] == "custom")
        self._chb_command.setEnabled(self.COMMANDS[index][1] == "custom")
        self._line_menu.setEnabled(self.COMMANDS[index][0] == "custom")
        self._cmb_menu.setEnabled(self.COMMANDS[index][0] == "custom")
