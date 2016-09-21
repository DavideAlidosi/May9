import maya.cmds as mc
import maya.mel as mel
oEdges = mc.ls(sl=True)
oObj = oEdges[0].split('.')[0]
oFace = ''
for i in oEdges:
	if '.f[' in i:
		oFace = i
mc.DetachComponent()
mc.select(cl=True)
mc.select(oFace)
mc.ConvertSelectionToShell()
oFacesFinal = mc.ls(sl=True)
mc.select(oObj)
mc.polyMergeVertex(d=0.0001)
mc.select(oFacesFinal)
mc.selectType(smp=0, sme=0, smf=1, smu=0, pv=0, pe=0, pf=1, puv=0)
mc.hilite(oObj, r=True)
mel.eval('doDelete;')
mc.select(oObj, r=True)
mc.polyCloseBorder()