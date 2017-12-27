import maya.cmds as cmds
import cPickle, os, imp


def pyToAttr(objAttr, data):
	"""
	Write (pickle) Python data to the given Maya obj.attr.  This data can
	later be read back (unpickled) via attrToPy().

	Arguments:
	objAttr : string : a valid object.attribute name in the scene.  If the
		object exists, but the attribute doesn't, the attribute will be added.
		The if the attribute already exists, it must be of type 'string', so
		the Python data can be written to it.
	data : some Python data :  Data that will be pickled to the attribute
		in question.
	"""
	obj, attr = objAttr.split('.')
	# Add the attr if it doesn't exist:
	if not cmds.objExists(objAttr):
		cmds.addAttr(obj, longName=attr, dataType='string')
	# Make sure it is the correct type before modifing:
	if cmds.getAttr(objAttr, type=True) != 'string':
		raise Exception("Object '%s' already has an attribute called '%s', but it isn't type 'string'"%(obj,attr))

	# Pickle the data and return the coresponding string value:
	stringData = cPickle.dumps(data)
	# Make sure attr is unlocked before edit:
	cmds.setAttr(objAttr, edit=True, lock=False)
	# Set attr to string value:
	cmds.setAttr(objAttr, stringData, type='string')
	# And lock it for safety:
	cmds.setAttr(objAttr, edit=True, lock=True)

def attrToPy(objAttr):
	"""
	Take previously stored (pickled) data on a Maya attribute (put there via
	pyToAttr() ) and read it back (unpickle) to valid Python values.

	Arguments:
	objAttr : string : A valid object.attribute name in the scene.  And of course,
		it must have already had valid Python data pickled to it.

	Return : some Python data :  The reconstituted, unpickled Python data.
	"""
	# Get the string representation of the pickled data.  Maya attrs return
	# unicode vals, and cPickle wants string, so we convert:
	stringAttrData = str(cmds.getAttr(objAttr))
	# Un-pickle the string data:
	loadedData = cPickle.loads(stringAttrData)

	return loadedData

# Compile Py from Ui
def compileUI():
	from pysideuic import compileUi
	
	moduleName = __name__.split('.')[0]
	modulePath = os.path.abspath(imp.find_module(moduleName)[1])
	pyfile = open(modulePath+'\\mainWindow.py', 'w')
	compileUi(modulePath+"\\mainWindow.ui", pyfile, False, 4,False)
	pyfile.close()

	
def fixName(name):
	i = 1
	initName = name
	while cmds.objExists(name):
		name = initName + str(i)
		i += 1
	return name	

def fixShapeName(name):
	shape = cmds.listRelatives(name)[0]
	cmds.rename(shape, name+"Shape")
	return shape

def getShape(name):
	shape = cmds.listRelatives(name)[0]
	return shape

def resetAttrs(o):
	cmds.setAttr(o+".tx", 0)
	cmds.setAttr(o+".ty", 0)
	cmds.setAttr(o+".tz", 0)
	cmds.setAttr(o+".rx", 0)
	cmds.setAttr(o+".ry", 0)
	cmds.setAttr(o+".rz", 0)	
	
def setColor(o, color):
	cmds.setAttr(o+".overrideEnabled", 1)
	cmds.setAttr(o+".overrideColor", color)