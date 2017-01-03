#!/usr/bin/env python
# -*- coding: utf-8 -*-
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om
from functools import partial

from PySide2 import QtWidgets, QtGui, QtCore
from shiboken2 import wrapInstance

import os, imp, types, webbrowser, logging, inspect, json
import utils
import mainWindow

version = "1.0"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)

fileName = __name__.split('.')[-1]
rootFolder = __file__.split(fileName)[0]
data_file = rootFolder + 'data.json'

# Compile Py from Ui u
#utils.compileUI()
#reload(mainWindow)

def mayaMainWindow():
	mainWindowPtr = omui.MQtUtil.mainWindow()
	return wrapInstance(long(mainWindowPtr), QtWidgets.QWidget)


class MainWindow(QtWidgets.QMainWindow, mainWindow.Ui_MainWindow):
	def __init__(self, parent=mayaMainWindow()):
		super(MainWindow, self).__init__(parent)
		self.setupUi(self)
		logger.debug("Start " + inspect.stack()[0][3])

		self.source = ""
		self.targets = []
		self.sourceType = "None"
		self.targetType = "None"
		self.contextData = []
		self.macrossData = {}
		self.data = {}

		self.connectSignals()
		self.readData()
		
		self.save_btn.setToolTip("Save connection template from two attributes")
		self.repeat_btn.setVisible(False)
		
		
		self.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "Context Connector " + version, None))


	def connectSignals(self):
		logger.debug("Start " + inspect.stack()[0][3])

		self.setSource_btn.clicked.connect(self.setSource)
		self.setTarget_btn.clicked.connect(self.setTarget)
		self.update_btn.clicked.connect(self.updateSelection)

		self.save_btn.clicked.connect(self.saveContextData)
		self.connect_btn.clicked.connect(self.customConnect)

	def setSource(self, selection=""):
		logger.debug("setSource ")

		if selection == "":
			selection = cmds.ls(sl=True)

		if len(selection) != 1:
			self.source = ""
			self.sourceType = "None"
			cmds.warning( "Select one source object" )

		else:
			self.source = selection[0]
			self.sourceType = cmds.objectType(self.source)

		self.source_lineEdit.setText(self.source)

		self.updateNodesType()
		self.updateAttrsList("source")
		self.updateContextButtons()
		self.updateMacrossButtons()
		self.updateSourceSelectMenu()

	def setTarget(self, selection=""):
		logger.debug("setTarget ")

		if selection == "":
			selection = cmds.ls(sl=True)

		if len(selection) == 0:
			cmds.warning ( "Select target object(s)" )
			self.target_lineEdit.setText("")
			self.targets = []
			self.targetType = "None"

		elif len(selection) == 1:
			self.targets = selection
			self.target_lineEdit.setText(self.targets[0])
			self.targetType = cmds.objectType(self.targets[0])

		else:
			# set multiple targets
			self.targets = selection
			self.target_lineEdit.setText("mult..")

			# check all targets type
			typesArray = []
			for t in self.targets:
				type_ = cmds.objectType(t)
				if type_ not in typesArray:
					typesArray.append(type_)
			if len(typesArray) == 1:
				self.targetType = typesArray[0]
			else:
				self.targetType = "Mixed.."

		self.updateNodesType()
		self.updateAttrsList("target")
		self.updateContextButtons()
		self.updateMacrossButtons()
		self.updateTargetSelectMenu()

	def updateSelection(self):
		logger.debug("Start " + inspect.stack()[0][3])
		
		selection = cmds.ls(sl=True)

		source = selection[:1]
		targets = selection[1:]

		self.setSource(source)
		self.setTarget(targets)

	def updateNodesType(self):
		logger.debug("Start " + inspect.stack()[0][3])

		self.nodes_label.setText(self.sourceType.capitalize() + " > " + self.targetType.capitalize())

	def updateAttrsList(self, type_):
		logger.debug("Start " + inspect.stack()[0][3])

		# get vars
		if type_ == "source":
			obj = self.source
			widget = self.sourceAttr_cbox
		else:
			if self.targetType != "None" and self.targetType != "Mixed..":
				obj = self.targets[0]
			else:
				obj = ""		
			widget = self.targetAttr_cbox

		oldAttr = widget.currentText()
		widget.clear()

		if obj == "":
			return

		# get full attrs list
		fullList = cmds.listAttr(obj)

		# get channelBox attrs list
		#unkeyable =  cmds.listAttr(obj, v=1, cb=1) or []
		#keyable = cmds.listAttr(obj, k=1) or []
		#user = cmds.listAttr(obj, ud=1)	or []

		#cbAttrs = unkeyable + keyable + user

		#attrs = []
		#for a in fullList:
			#if a in cbAttrs and a not in attrs:
				#attrs.append(a)

		# add channelBox attrs and full list
		#widget.addItems(attrs)
		#widget.insertSeparator(len(attrs))
		
		widget.addItems(fullList)
		
		if oldAttr in fullList:
			for x, name in enumerate(fullList):
				if name == oldAttr:
					widget.setCurrentIndex(x)

	def updateContextButtons(self):
		logger.debug("Start updateContextButtons")

		# clear buttons
		for x in range(self.context_lay.count()):
			b = self.context_lay.itemAt(x)
			b.widget().deleteLater()
		
		# load buttons
		for data in self.contextData:
			if self.sourceType == data.split("|")[0]:
				if self.targetType == data.split("|")[2]:
					btn = QtWidgets.QToolButton()
					btn.setText(data.split("|")[1]+' > '+data.split("|")[3])
					self.context_lay.addWidget(btn)
					
					btn.clicked.connect(partial(self.contextAction, data))
					self.buttonMenu(btn, data)
					
	def updateMacrossButtons(self):
		logger.debug("Start updateCMacrossButtons")	
		# clear macross buttons
		for x in range(self.macross_lay.count()):
			b = self.macross_lay.itemAt(x)
			b.widget().deleteLater()
			
		# load macross buttons
		pair = self.sourceType + "|" + self.targetType
		
		# get all macrosses of the pair
		try:
			macrosses = self.macrossData[pair]
		except:
			macrosses = []

		# for every macross
		for m in macrosses:
			# get needed macross
			btn = QtWidgets.QToolButton()
			btn.setText(m['name'])
			self.macross_lay.addWidget(btn)
			
			btn.clicked.connect(partial(self.macrossExec, m['name']))						

			btn.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
			btn.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
			btn.setFixedHeight(26)		
			
			self.macrossMenu(btn)

	def buttonMenu(self, btn, data):
		# menu
		#btn.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
		
		# create menues
		menu = QtWidgets.QMenu(self)
		
		macross_menu = QtWidgets.QMenu(self)
		macross_menu.setTitle("Add to Mactross")		

		
		# main menu actions
		delete_action = QtWidgets.QAction(self)
		delete_action.setText('Delete')			
		delete_action.triggered.connect(partial(self.removeFromContext, data))
		
		
		# macross menu actions
		newMacross_action = QtWidgets.QAction(self)
		newMacross_action.setText('New Mactross..')
		newMacross_action.triggered.connect(partial(self.newMacross, data))		
		macross_menu.addAction(newMacross_action)

		macross_menu.addSeparator()
		
		pair = data.split('|')[0] + "|" + data.split('|')[2]
		try:
			macrosses = self.macrossData[pair]
			for m in macrosses:
				m_action = QtWidgets.QAction(self)
				m_action.setText(m["name"])
				m_action.triggered.connect(partial(self.addToMacross, m["name"], data))	
				macross_menu.addAction(m_action)
		except: pass
		

		# main menu data
		menu.addAction(delete_action)
		menu.addMenu(macross_menu)
		
		# add menu to button
		btn.setMenu(menu)
		btn.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
		btn.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
		btn.setFixedHeight(26)
		
	def macrossMenu(self, btn):
		# menu
		#btn.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
		
		# create menues
		menu = QtWidgets.QMenu(self)
		
		connections_menu = QtWidgets.QMenu(self)
		connections_menu.setTitle("Connection")		

		
		# main menu actions
		rename_action = QtWidgets.QAction(self)
		rename_action.setText('Rename')			
		rename_action.triggered.connect(partial(self.renameMacross, btn.text()))		

		delete_action = QtWidgets.QAction(self)
		delete_action.setText('Delete')			
		delete_action.triggered.connect(partial(self.removeMacross, btn.text()))
		
		
		# macross menu actions
		m = self.getMacross(btn.text())
		connections = m["connections"]

		for c in connections:
			c_action = QtWidgets.QAction(self)
			c_action.setText(c.replace('|', ' > '))
			data = self.sourceType + "|" + c.split("|")[0] + "|" + self.targetType + "|" + c.split("|")[1]
			c_action.triggered.connect(partial(self.contextAction, data))	
			connections_menu.addAction(c_action)
		

		# main menu data
		menu.addAction(rename_action)
		menu.addAction(delete_action)
		menu.addMenu(connections_menu)
		
		# add menu to button
		btn.setMenu(menu)

	def updateSourceSelectMenu(self):
		
		# delete old actions
		actions = self.setSource_btn.actions()
		for a in actions:
			self.setSource_btn.removeAction(a)
		
		self.setSource_btn.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
		
		# main menu actions
		action = QtWidgets.QAction(self)
		action.setText(self.source)			
		action.triggered.connect(partial(self.selectObject, self.source))

		# add menu to button
		self.setSource_btn.addAction(action)
		
	def updateTargetSelectMenu(self):
		
		# delete old actions
		actions = self.setTarget_btn.actions()
		for a in actions:
			self.setTarget_btn.removeAction(a)
		
		self.setTarget_btn.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
		
		# main menu actions
		for t in self.targets:
			action = QtWidgets.QAction(self)
			action.setText(t)			
			action.triggered.connect(partial(self.selectObject, t))

			# add menu to button
			self.setTarget_btn.addAction(action)
	
	def selectObject(self, name):
		cmds.select(name)


	# Actions --------------------------------------------------------------------------

	def disconnect(self, target, attr):
		if cmds.connectionInfo(target + '.' + attr, isDestination=True) :
			sourceAttr = cmds.connectionInfo(target + '.' + attr, sourceFromDestination=True)
			cmds.disconnectAttr( sourceAttr, target + '.' + attr)		

	def customConnect(self, sourceAttr="", targetAttr=""):
		logger.debug("Start Custom Connect")

		if sourceAttr == "" or targetAttr == "":
			sourceAttr = self.sourceAttr_cbox.currentText()
			targetAttr = self.targetAttr_cbox.currentText()

		for target in self.targets:
			self.disconnect(target, targetAttr)
			cmds.connectAttr( self.source + '.' + sourceAttr, target + '.' + targetAttr, f=True)

	def contextAction(self, connectData):
		logger.debug("Start " + inspect.stack()[0][3])
		
		# get vars
		sourceAttr = connectData.split("|")[1]
		targetAttr = connectData.split("|")[3]
		
		# connect
		for target in self.targets:
			self.disconnect(target, targetAttr)
			cmds.connectAttr( self.source + '.' + sourceAttr, target + '.' + targetAttr, f=True)		

	def removeFromContext(self, data):
		logger.debug("Start " + inspect.stack()[0][3])

		self.contextData.remove(data)
		self.data['connections'] = self.contextData
		json.dump(self.data, open(data_file, 'w'), indent=4)	
		self.updateContextButtons()




	# Macrosses ---------------------------------------------------------

	def newMacross(self, data):
		logger.debug("Start " + inspect.stack()[0][3])	
		
		text, ok = QtWidgets.QInputDialog.getText(self, "Create Macross", "Please enter new macross name")
		
		if ok:
			pair = data.split('|')[0] + "|" + data.split('|')[2]
			connection = data.split('|')[1] + "|" + data.split('|')[3]
			
			# get all macrosses from pair
			try:
				macrosses = self.macrossData[pair]
			except:
				macrosses = []
			
			# if macross is exists, exit
			for m in macrosses:
				if m["name"] == text:
					print "This macross name is exists"
					return
			
			# else, create new macross data
			macrossData = {
		        "name" : text,
		        "connections" : [connection]
		    }				
			
			# add new macross data to macrosses of the pair
			macrosses.append(macrossData)
			
			# save macrosses data 
			self.macrossData[pair] = macrosses
			self.saveMacrossData()

	def addToMacross(self, macrossName, data):
		logger.debug("Start " + inspect.stack()[0][3])	
		
		m = self.getMacross(macrossName)
		
		# take connection to connecetion list of the macross
		connection = data.split('|')[1] + "|" + data.split('|')[3]
		if connection not in m["connections"]:
			m["connections"].append(connection)
			self.saveMacrossData()
		else:
			print "this connection allready is in macross"
		
	def macrossExec(self, macrossName):
		logger.debug("Start macrossExec")
		
		m = self.getMacross(macrossName)
		
		connections = m["connections"]
		for c in connections:
			sourceAttr, targetAttr = c.split("|")
			self.customConnect(sourceAttr, targetAttr)
		
	def getMacross(self, macrossName):
		logger.debug("Start GetCurMacrosses")
		
		# get nodes pair from data
		pair = self.sourceType + "|" + self.targetType
		
		# get all macrosses of the pair
		macrosses = self.macrossData[pair]
				
		# for every macross
		for m in macrosses:
			# get needed macross
			if m['name'] == macrossName:
				return m
		
		print "not find macross"
		return None

	def removeMacross(self, macrossName):
		logger.debug("Start " + inspect.stack()[0][3])
		
		m = self.getMacross(macrossName)
		pair = self.sourceType + "|" + self.targetType

		self.macrossData[pair].remove(m)
		self.saveMacrossData()
		self.updateMacrossButtons()
				
	def renameMacross(self, macrossName):
		logger.debug("Start " + inspect.stack()[0][3])
		
		text, ok = QtWidgets.QInputDialog.getText(self, "Rename Macross", "Please enter new macross name")
		
		if ok:
			m = self.getMacross(macrossName)
			pair = self.sourceType + "|" + self.targetType
	
			m['name'] = text
			self.saveMacrossData()
			self.updateMacrossButtons()
				


	# Context Data
	
	def readData(self):
		logger.debug("Start " + inspect.stack()[0][3])	
		
		self.data = json.load( open(data_file, 'r') )
		self.contextData = self.data['connections']
		self.macrossData = self.data['macrosses']

	def saveContextData(self):
		logger.debug("Start " + inspect.stack()[0][3])

		if self.sourceType == "None" or self.targetType == "None":
			cmds.warning("Select source and target attribute")
			return

		sourceAttr = self.sourceAttr_cbox.currentText()
		targetAttr = self.targetAttr_cbox.currentText()

		self.contextData.append(self.sourceType + "|" + sourceAttr + "|" + self.targetType + "|" + targetAttr)
		self.data['connections'] = self.contextData
		
		json.dump(self.data, open(data_file, 'w'), indent=4)	

		self.updateContextButtons()
		
	def saveMacrossData(self):
		logger.debug("Start saveMacrossData")

		self.data['macrosses'] = self.macrossData
		
		json.dump(self.data, open(data_file, 'w'), indent=4)	

		self.updateContextButtons()
		self.updateMacrossButtons()