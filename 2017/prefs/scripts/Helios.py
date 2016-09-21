import maya.OpenMayaUI as omui
import maya.cmds as mc
import maya.mel as mel
import re
from functools import partial
import sys
import os
import webbrowser
import subprocess
import time
import cPickle as pickle

from glob import glob

try:
    from PySide import QtGui, QtCore
    from PySide.QtGui import *
    from PySide.QtCore import *
    maya_version = 2016
except ImportError:
    from PySide2 import QtGui, QtCore, QtWidgets
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    maya_version = 2017


# TODO:

class HeliosGUI(QWidget):
    def __init__(self):
        super(HeliosGUI, self).__init__()
        start_time = time.time()

        self.cur_path = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")
        
        if not os.path.isfile(self.cur_path + "/Helios/commands/_commands_use_frequency.pkl"):
            open(self.cur_path + "/Helios/commands/_commands_use_frequency.pkl", "a")

        if not os.path.isfile(self.cur_path + "/Helios/commands/_last_used_command.ini"):
            open(self.cur_path + "/Helios/commands/_last_used_command.ini", "a")

        # Get list of commands frequency       
        self.commands_use_frequency = {}
        commands_frequency_file = open(self.cur_path + "/Helios/commands/_commands_use_frequency.pkl", 'rb')
        try:
            self.commands_use_frequency = pickle.load(commands_frequency_file)
        except:
            pass
        #self.commands_use_frequency = [[key, value] for key, value in self.commands_use_frequency.items()]
        commands_frequency_file.close()

        # Get name of last used command
        last_command_file = open(self.cur_path + "/Helios/commands/_last_used_command.ini", "r")
        self.last_command = last_command_file.read()
        last_command_file.close()

        self.time_total = []

        # Get list of all commands
        self.Helios_Commands_init = glob("{0}/Helios/commands/*".format(self.cur_path))
        self.Helios_Commands_init = [os.path.split(command)[-1].replace(".py", "") for command in self.Helios_Commands_init if not "ini" in command and not "pkl" in command]
        self.Helios_Commands = []
        self.Helios_Commands_init = [command.replace("-advanced", "") for command in self.Helios_Commands_init]
        self.Helios_Commands = ["+" + command if self.Helios_Commands_init.count(command) == 2 else command for command in self.Helios_Commands_init]

        self.highlighted_frame_number = 0
        self.frames_list = []

        self.navigation_dir = "down"
        self.scroll_counter = 4
        with open(self.cur_path + "/Helios/style/style.css", "r") as fh:
            if maya_version == 2016:
                self.setStyleSheet('\nQWidget\n{\n\tbackground-color: rgba(50, 50, 50, 1);\n}' + fh.read())
            elif maya_version == 2017:
                self.setStyleSheet('\nQWidget\n{\n\tbackground-color: transparent;\n}' + fh.read())

        self.mouse_is_over = False
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Create main frame
        self.mainLayout = QVBoxLayout(self) # Main Layout
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.mainFrame = QFrame(self) # Main Frame
        #self.mainFrame.setStyleSheet('background-color: green;')
        self.mainLayout.addWidget(self.mainFrame) # Add main frame to main layout

        # Create layout inside main Frame for the first and second frame.
        self.mainFrameVerticalLayout = QVBoxLayout(self.mainFrame)
        self.mainFrameVerticalLayout.setContentsMargins(0, 0, 0, 0)
        self.mainFrameVerticalLayout.setSpacing(0)

        # Create first frame
        self.searchFrame = QFrame(self.mainFrame)
        #self.searchFrame.setStyleSheet('background-color: blue;')
        self.searchFrameLayout = QHBoxLayout(self.searchFrame)
        self.searchFrameLayout.setSpacing(0)
        self.searchFrameLayout.setContentsMargins(0, 0, 0, 0)

        # Create second frame
        self.resultFrame = QFrame(self.mainFrame)
        #self.resultFrame.setStyleSheet('background-color: red;')
        self.resultFrameLayout = QVBoxLayout(self.resultFrame)
        self.resultFrameLayout.setContentsMargins(0, 0, 0, 0)
        self.resultFrame.hide() # Hide it

        # Create indication label
        self.labelFrame = QFrame(self.mainFrame)
        self.labelFrameLayout = QVBoxLayout(self.labelFrame)
        #self.labelFrame.setStyleSheet('background-color: red;')
        self.labelFrame.setStyleSheet('color: rgb(240, 240, 240);')
        self.labelFrameLayout.setContentsMargins(0, 0, 0, 0)
        self.labelFrameLayout.setAlignment(Qt.AlignCenter)
        self.indicLabel = QLabel("Enter command name or type ? to see the help")
        self.labelFrameLayout.addWidget(self.indicLabel)

        # Create scroll frame
        self.scrollFrame = QFrame(self.mainFrame)
        self.scrollFrameLayout = QVBoxLayout(self.scrollFrame)
        #self.scrollFrame.setStyleSheet('background-color: red;')
        self.scrollFrameLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollFrameLayout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.scrollButton = QPushButton("v")
        self.scrollButton.clicked.connect(self.scroll_results)
        self.scrollButton.setFixedWidth(100)
        self.scrollButton.setFixedHeight(20)
        self.scrollFrameLayout.addWidget(self.scrollButton)
        self.scrollFrame.hide()
        # Add first and second frames to mainFrame layout
        self.mainFrameVerticalLayout.addWidget(self.searchFrame)
        self.mainFrameVerticalLayout.addWidget(self.resultFrame)
        self.mainFrameVerticalLayout.addWidget(self.scrollFrame)
        self.mainFrameVerticalLayout.addWidget(self.labelFrame)
        self.spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.mainFrameVerticalLayout.addItem(self.spacer)

        # Add widgets on first frame
        self.searchLineEdit = customLineEdit(self)
        self.searchLineEdit.setText(self.last_command)
        self.searchLineEdit.selectAll()
        self.searchLineEdit.textChanged.connect(self.show_searchUI)
        self.searchFrameLayout.addWidget(self.searchLineEdit)

        # Add widgets on second frame
        self.scrollArea = customScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.verticalScrollBar().actionTriggered.connect(self.scrollBarEvent)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 380, 280))
        self.scrollAreaHorizontalLayout = QHBoxLayout(self.scrollAreaWidgetContents)
        self.scrollAreaHorizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollAreaHorizontalLayout.setSpacing(0)
        self.scrollAreaHorizontalLayout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.gridLayout = QGridLayout()
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollAreaHorizontalLayout.addLayout(self.gridLayout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.resultFrameLayout.addWidget(self.scrollArea)
        # Set Fixed Size
        self.setFixedSize(300, 100)

        # Center Window on Screen
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

        # Show Window
        self.activateWindow()
        self.searchLineEdit.setFocus()
        self.raise_()
        self.show()

        print("--- %s seconds ---" % (time.time() - start_time))

    def scrollBarEvent(self):
        self.searchLineEdit.setFocus()

    def scroll_results(self):
        self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().value() + 44)


    def show_searchUI(self):
        self.scrollFrame.hide()
        self.labelFrame.hide()
        self.highlighted_frame_number = 0

        query = self.searchLineEdit.text().replace("?", "")

        query_words = query.lower().split(" ")
        query_words = filter(None, query_words)
        scoreList = {}

        for word in self.Helios_Commands:
            score = 0
            for query_word in query_words:
                if query_word in word.lower():
                    score += 1

            scoreList[word] = score

        # If user enter more than one words, get only result with a score at least equal to the number of words in the query
        sorted_matches = [i for i in scoreList.items() if i[1] >= len(query_words)]

        # Sort matches by score
        sorted_matches = sorted(sorted_matches, key=lambda x: x[1])
        sorted_matches = sorted_matches[0:8]

        # Sort matches by frequency of use
        sorted_matches_with_frequency = []
        for match in sorted_matches:
            match_command = match[0].lstrip("+")
            match_score = match[1]
            try:
                match_score += self.commands_use_frequency[match_command]
                sorted_matches_with_frequency.append((match[0], match_score))
            except:
                sorted_matches_with_frequency.append((match[0], match_score))
                pass

        sorted_matches_with_frequency = sorted(sorted_matches_with_frequency, key=lambda x: x[1], reverse=True)

        # Keep only the command and not the score
        sorted_matches_with_frequency = [i[0] for i in sorted_matches_with_frequency]

        # Remove all frames from searchLayout
        for i in range(self.gridLayout.count()): 
            self.gridLayout.itemAt(i).widget().close()

        # If there's no match, hide search result frame.
        if len(sorted_matches_with_frequency) == 0:
            self.setFixedSize(300, 100)
            self.resultFrame.hide()
            self.labelFrame.show()
            return

        self.frames_list = []
        for i, command in enumerate(sorted_matches_with_frequency):
            self.frame = customFrame(self, command) # Create custom frame and pass command name as arg
            self.frameLayout = QVBoxLayout(self.frame)
            self.label = QLabel("{0}. {1}".format(i + 1, command))
            
            self.frameLayout.addWidget(self.label)
            self.gridLayout.addWidget(self.frame)
            self.frames_list.append(self.frame)
        
        if len(query) > 0:
            first_result = self.frames_list[0]
            first_result.enterEvent(self)
            if len(sorted_matches) == 1:
                self.setFixedSize(300, 105)
            elif len(sorted_matches) == 2:
                self.setFixedSize(300, 140)
            elif len(sorted_matches) == 3:
                self.setFixedSize(300, 185)
            elif len(sorted_matches) == 4:
                self.setFixedSize(300, 230)
            else:
                self.scrollFrame.show()
                self.setFixedSize(300, 250)
                self.scrollAreaHorizontalLayout.setSpacing(4)
            self.resultFrame.show()
        else:
            self.setFixedSize(300, 100)
            self.scrollFrame.hide()
            self.resultFrame.hide()

        #self.time_total.append(time.time() - start_time)
        #print(sum(self.time_total) / float(len(self.time_total)))
        #print("--- %s seconds ---" % (time.time() - start_time))

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

        elif e.key() == Qt.Key_Return:

            if len(self.frames_list) > 0:
                if self.highlighted_frame_number == -1:
                    first_result = self.frames_list[0]
                else:
                    first_result = self.frames_list[self.highlighted_frame_number]
                first_result.mousePressEvent(self)
            else:
                # The user has not entered any new command. Execute last known command.
                repeatFrame = customFrame(self, self.last_command)
                repeatFrame.mousePressEvent(self)

        elif e.key() == Qt.Key_Down:
            if self.highlighted_frame_number == len(self.frames_list) - 1:
                self.highlighted_frame_number = 0
            else:
                self.highlighted_frame_number += 1

            for i, frame in enumerate(self.frames_list):
                if i == self.highlighted_frame_number:
                    frame.enterEvent(self)
                else:
                    frame.leaveEvent(self)

            self.scroll_counter += 1
            # Handle scrolling of results list
            if self.scroll_counter > 3:
                if self.highlighted_frame_number >= 4:
                    self.scrollArea.verticalScrollBar().setValue((self.highlighted_frame_number - 3) * 44)
                elif self.highlighted_frame_number == 0:
                    self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().minimum())
                self.scroll_counter = 4
        elif e.key() == Qt.Key_Up:
            if self.highlighted_frame_number > 0:
                self.highlighted_frame_number -= 1
            elif self.highlighted_frame_number == 0:
                self.highlighted_frame_number = len(self.frames_list) - 1
            elif self.highlighted_frame_number == -1:
                self.highlighted_frame_number = len(self.frames_list) - 1

            for i, frame in enumerate(self.frames_list):
                if i == self.highlighted_frame_number:
                    frame.enterEvent(self)
                else:
                    frame.leaveEvent(self)

            if self.highlighted_frame_number == len(self.frames_list) - 1 and self.scroll_counter == 4:
                # If true, user is at the top of the list and wants to go up to the end. Therefore go to end of scrollbar.
                self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())
                self.scroll_counter = 4

            else:

                if self.scroll_counter > 1:
                    self.scroll_counter -= 1
                else:
                    # Handle scrolling of results list
                    if self.highlighted_frame_number < len(self.frames_list) - 1:
                        self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().value() - 44)
                        self.scroll_counter = 0
                    elif self.highlighted_frame_number == len(self.frames_list) - 1:
                        self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())
                        self.scroll_counter = 4

        else:
            QWidget.keyPressEvent(self, e)

    def focusOutEvent(self, event):
        if not self.mouse_is_over:
            self.close()

    def enterEvent(self, event):
        self.mouse_is_over = True

    def leaveEvent(self, event):
        self.mouse_is_over = False


class customLineEdit(QLineEdit):
    def __init__(self, gui):
        super(customLineEdit, self).__init__()
        self.setFixedSize(300, 50)
        self.gui = gui

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.gui.close()
        else:
            QLineEdit.keyPressEvent(self, e)

    def focusOutEvent(self, event):
        if not self.gui.mouse_is_over:
            self.gui.close()

    def enterEvent(self, event):
        self.gui.mouse_is_over = True

    def leaveEvent(self, event):
        self.gui.mouse_is_over = False

class customScrollArea(QScrollArea):
    def __init__(self, gui):
        super(customScrollArea, self).__init__()
        self.gui = gui
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.gui.close()
        elif e.key() == Qt.Key_Return:
            self.gui.close()
        else:
            QScrollArea.keyPressEvent(self, e)
    def focusOutEvent(self, event):
        if not self.gui.mouse_is_over:
            self.gui.close()
    def enterEvent(self, event):
        self.gui.mouse_is_over = True
    def leaveEvent(self, event):
        self.gui.mouse_is_over = False

class customFrame(QFrame):
    def __init__(self, gui, frame_name):
        super(customFrame, self).__init__()
        #self.setStyleSheet('background-color: yellow;')
        self.setStyleSheet('background-color: rgba(50, 50, 50, 255);')
        self.gui = gui
        self.frame_name = frame_name.lstrip("+")
        self.setFixedHeight(40)
        self.setFixedWidth(275)

    def mousePressEvent(self, e):

        modifiers = QApplication.keyboardModifiers()

        if "?" in self.gui.searchLineEdit.text():
            self.gui.close()
            if modifiers == Qt.ControlModifier:
                if os.path.isfile('{0}/Helios/commands/{1}-advanced.py'.format(self.gui.cur_path, self.frame_name)):
                    subprocess.call(['notepad.exe', '{0}/Helios/commands/{1}-advanced.py'.format(self.gui.cur_path, self.frame_name)])
                else:
                    mc.inViewMessage(message="Script {0}-advanced.py doesn't exist".format(self.frame_name), pos='topCenter', fade=True, fadeStayTime=1500, fadeInTime=250, fadeOutTime=250)
        
            else:
                if os.path.isfile('{0}/Helios/commands/{1}.py'.format(self.gui.cur_path, self.frame_name)):
                    subprocess.call(['notepad.exe', '{0}/Helios/commands/{1}.py'.format(self.gui.cur_path, self.frame_name)])
                else:
                    mc.inViewMessage(message="Script {0}.py doesn't exist".format(self.frame_name), pos='topCenter', fade=True, fadeStayTime=1500, fadeInTime=250, fadeOutTime=250)
        

        else:

            if modifiers == Qt.ControlModifier:
                try:
                    exec(compile(open('{0}/Helios/commands/{1}-advanced.py'.format(self.gui.cur_path, self.frame_name)).read(), '{0}/Helios/commands/{1}-advanced.py'.format(self.gui.cur_path, self.frame_name), 'exec'))
                except Exception, e:
                    try:
                        errorLog = open(self.gui.cur_path + "/Helios/commands/errorLog.txt", "w")
                        errorLog.write(str(e))
                    except:
                        pass
                    print(str(e))
                    mc.inViewMessage(message="Errors occured while executing '{0}'".format(self.frame_name), pos='topCenter', fade=True, fadeStayTime=750, fadeInTime=250, fadeOutTime=250)
            else:
                try:
                    exec(compile(open('{0}/Helios/commands/{1}.py'.format(self.gui.cur_path, self.frame_name)).read(), '{0}/Helios/commands/{1}.py'.format(self.gui.cur_path, self.frame_name), 'exec'))
                except Exception, e:
                    try:
                        errorLog = open(self.gui.cur_path + "/Helios/commands/errorLog.txt", "w")
                        errorLog.write(str(e))
                    except:
                        pass
                    print(str(e))
                    mc.inViewMessage(message="Errors occured while executing '{0}'".format(self.frame_name), pos='topCenter', fade=True, fadeStayTime=750, fadeInTime=250, fadeOutTime=250)
            
            last_command_file = open(self.gui.cur_path + "/Helios/commands/_last_used_command.ini", "w")
            last_command_file.write(self.frame_name)
            last_command_file.close()

            try:
                self.gui.commands_use_frequency[self.frame_name] = self.gui.commands_use_frequency[self.frame_name] + 1
            except:
                self.gui.commands_use_frequency[self.frame_name] = 1

            afile = open(self.gui.cur_path + "/Helios/commands/_commands_use_frequency.pkl", 'wb')
            pickle.dump(self.gui.commands_use_frequency, afile)
            afile.close()

        self.gui.close()

    def isSelected(self):
        self.setStyleSheet('background-color: rgba(100, 160, 180, 255); color: rgb(40, 40, 40);')

    def enterEvent(self, event):
        self.gui.frames_list[0].leaveEvent(self) # Remove highlight on first frame if user put his mouse over another one
        self.setStyleSheet('background-color: rgba(100, 160, 180, 255); color: rgb(40, 40, 40);')

    def leaveEvent(self, event):
        self.setStyleSheet('background-color: rgba(50, 50, 50, 255);')


