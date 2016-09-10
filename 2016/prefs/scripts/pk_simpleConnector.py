"""
Copyright (c) 2016 Pavel Korolyov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

__author__ = 'Pavel Korolyov (pavel.crow@gmail.com)'
__version__ = '1.0.0'
__date__ = '2016/05/07'


Description:
Small tool for simple and fast conncecting most used attributes.

Features:
1. Fast connect by one button - translate, rotate, scale and shape attributes. Most frequently used attributes in rigging process.
2. Connecting from one to multiple objects. For this, you can select muliple object and click Set Target button.

Tips:
1. If before run tool select two objects, they will be set as source and target
2. If click right mouse button on source ot target name, you can see list setted objects. From this menu you can select this object.
3. In full list of attributes you can find attribute by pressed key button.

Usage:
Make shelf button or shortcut for python commands:
import pk_simpleConnector
reload(pk_simpleConnector)

"""

# -*- coding: cp1251
import maya.cmds as cmds
from functools import partial

if cmds.window("connectorWindow", ex=True):
	cmds.deleteUI("connectorWindow", window=True)

window = cmds.window("connectorWindow", title = "Simple Connector", sizeable = True, toolbox=True)
mainLayout = cmds.columnLayout(rowSpacing = 2)

source = ''
target = ''
targets = []


def ui():
	cmds.rowLayout(numberOfColumns = 3, parent = mainLayout, adjustableColumn = 2)
	cmds.textField('source_text', text = "", width = 140, editable = False)
	
	cmds.popupMenu("source_menu")
	
	cmds.text(label = ">")
	cmds.textField('target_text', text = "", width = 140, editable = False)
	
	cmds.popupMenu("target_menu")
	
	
	cmds.rowLayout(numberOfColumns = 3, adjustableColumn = 2, parent = mainLayout)
	cmds.button(label = 'Set Source', width = 140, command = SetSource)
	cmds.text(label = "_")
	cmds.button(label = 'Set Target', width = 140, command = SetTarget)

	cmds.text(label = "                                  Stright Connect: ", parent = mainLayout)

	cmds.rowLayout(numberOfColumns = 4, parent = mainLayout)
	cmds.button("translate_btn", label = 'Translate', width = 60, command = partial(connect, "t"))
	cmds.button("rotate_btn", label = 'Rotate', width = 60, command = partial(connect, "r"))
	cmds.button("scale_btn", label = 'Scale', width = 60, command = partial(connect, "s"))
	cmds.button("all_btn", label = 'All', width = 103, command = connectAll)

	cmds.button("shape_btn", label = 'Shape', parent = mainLayout, width = 290, command = connectShape)
	
	
	cmds.separator(parent = mainLayout, h=10)
	cmds.text(label = "                                Andanced Connect: ", parent = mainLayout)
	
	cmds.setParent(mainLayout)

	cmds.optionMenu("sourceAttr_menu", label=' Source Attribute', width = 290)

	cmds.optionMenu("targetAttr_menu", label=' Target Attribute', width = 290)
	cmds.button(label = 'Connect', width = 290, parent = mainLayout, command = advConnect)
	
	
	
def selectItem(target, *args):
	cmds.select(target)

	
def updateTargetsPopup(*args):
	# get selected attr
	currentTargetAttr = ""
	if cmds.optionMenu("targetAttr_menu", q=True, numberOfItems=True) > 0:
		currentTargetAttr = cmds.optionMenu("targetAttr_menu", q=True, v=True)

	# clear attr menu	
	cmds.popupMenu("target_menu", e=True, deleteAllItems=True)
	
	menuItems = cmds.optionMenu('targetAttr_menu', q=True, itemListLong=True) # itemListLong returns the children
	if menuItems:
		cmds.deleteUI(menuItems)
		
	# fill attr menu
	for t in targets:
		cmds.menuItem(t, parent="target_menu", c=partial(selectItem, t))
		
		
	listAttr = cmds.listAttr(t)
	listAttr.sort()
	
	# if old current attr in list attr, save number
	n = 0
	for i in range(len(listAttr)):
		cmds.menuItem( label=listAttr[i], parent="targetAttr_menu" )
		
		if currentTargetAttr == listAttr[i]:
			n = i + 1
			print "ok", currentTargetAttr
	
	# select attr if it exist
	try:
		cmds.optionMenu('targetAttr_menu', e=True, select=n)
	except: pass
		
def updateSourcePopup(*args):
	# get selected attr
	currentSourceAttr = ""
	if cmds.optionMenu("sourceAttr_menu", q=True, numberOfItems=True) > 0:
		currentSourceAttr = cmds.optionMenu("sourceAttr_menu", q=True, v=True)

	# clear attr menu
	cmds.popupMenu("source_menu", e=True, deleteAllItems=True)
	
	menuItems = cmds.optionMenu('sourceAttr_menu', q=True, itemListLong=True) # itemListLong returns the children
	if menuItems:
		cmds.deleteUI(menuItems)

	# fill attr menu
	if source != "":
		cmds.menuItem(source, parent="source_menu", c=partial(selectItem, source))
		
		listAttr = cmds.listAttr(source)
		listAttr.sort()
		
		# if old current attr in list attr, save number
		n = 0
		for i in range(len(listAttr)):
			cmds.menuItem( label=listAttr[i], parent="sourceAttr_menu" )
			
			if currentSourceAttr == listAttr[i]:
				n = i + 1
		
		# select attr if it exist
		try:
			cmds.optionMenu('sourceAttr_menu', e=True, select=n)
		except: pass
		
			

def SetSource(*args):
	global source
	selection = cmds.ls(sl=True)
	
	if len(selection) != 1:
		source = ""
		print( "Select one object" )
	else:
		source = selection[0]
		
	cmds.textField('source_text', e=True, text = source)
	updateSourcePopup()
	
	refreshUI()

def SetTarget(*args):
	global target, targets
	selection = cmds.ls(sl=True)
	
	if len(selection) == 0:
		print ( "Select target object(s)" )
		cmds.textField('target_text', e=True, text = "")
		cmds.popupMenu("target_menu", e=True, deleteAllItems=True)
		targets = []
	elif len(selection) == 1:
		targets = selection
		cmds.textField('target_text', e=True, text = targets[0])
		updateTargetsPopup()
	else:
		# set multiple targets
		targets = selection
		cmds.textField('target_text', e=True, text = "mult..")
		updateTargetsPopup()

		
	refreshUI()
		
def refreshUI(*args):
	return
	if source != "" and ( target != "" or targets != [] ):
		enabled = True
	else:
		enabled = False
	
	# check transform ability connections
	try:
		if enabled and cmds.attributeQuery("t", node=source, exists=True) and cmds.attributeQuery("t", node=target, exists=True):
			cmds.button("translate_btn", e=True, enable=True)
			cmds.button("rotate_btn", e=True, enable=True)
			cmds.button("scale_btn", e=True, enable=True)
			cmds.button("all_btn", e=True, enable=True)
		else:
			cmds.button("translate_btn", e=True, enable=False)
			cmds.button("rotate_btn", e=True, enable=False)
			cmds.button("scale_btn", e=True, enable=False)
			cmds.button("all_btn", e=True, enable=False)
	except: pass
		

def connect(attr, *args):
	
	for target in targets:
		# disconnect all posible attributes
		disconnectAttr(target, attr)
		disconnectAttr(target, attr+"x")
		disconnectAttr(target, attr+"y")
		disconnectAttr(target, attr+"z")
		
		# connect
		cmds.connectAttr( source + '.' + attr, target + '.' + attr, f=True)


def disconnectAttr(target, attr, *args):
	if cmds.connectionInfo(target + '.' + attr, isDestination=True) :
		sourceAttr = cmds.connectionInfo(target + '.' + attr, sourceFromDestination=True)
		cmds.disconnectAttr( sourceAttr, target + '.' + attr)		

def connectAll(*args):
	
	connect("t")
	connect("r")
	connect("s")

def connectShape(*args):
	for target in targets:
		if cmds.objExists(source + '.outMesh') and cmds.objExists(target + '.inMesh'):
			cmds.connectAttr( source + '.outMesh', target + '.inMesh', f=True)
		if cmds.objExists(source + '.worldSpace') and cmds.objExists(target + '.create'):
			cmds.connectAttr( source + '.worldSpace', target + '.create', f=True)

def advConnect(*args):
	sourceAttr = cmds.optionMenu("sourceAttr_menu", q=True, v=True)
	targetAttr = cmds.optionMenu("targetAttr_menu", q=True, v=True)
	
	for target in targets:
		disconnectAttr(target, targetAttr)
		cmds.connectAttr( source + '.' + sourceAttr, target + '.' + targetAttr, f=True)



ui()

selection = cmds.ls(sl=True)

if len(selection) > 0:
	source = str(selection[0])
	cmds.textField('source_text', e=True, text = source)
	updateSourcePopup()
	
if len(selection) == 2:
	targets = selection[1:]
	cmds.textField('target_text', e=True, text = targets[0])
	updateTargetsPopup()

if len(selection) > 2:
	targets = selection[1:]
	cmds.textField('target_text', e=True, text = "mult..")
	updateTargetsPopup()

refreshUI()

cmds.showWindow(window)

