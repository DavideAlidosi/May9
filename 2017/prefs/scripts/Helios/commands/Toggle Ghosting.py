import maya.mel as mel
import maya.cmds as mc
obj = mc.ls(sl=1)
shape = mc.listRelatives(obj[0])
isGhosted = mc.getAttr(shape[0] + '.ghosting')
if isGhosted:
	mc.UnghostObject()
else:
	mc.GhostObject()