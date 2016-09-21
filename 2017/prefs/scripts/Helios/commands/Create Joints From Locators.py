oPos = []
oPosFinal = []
oSel = mc.ls(sl=True)
for i in range(0,len(oSel)):
	oPos = []
	oPos.append(mc.getAttr(oSel[i] + '.translateX'))
	oPos.append(mc.getAttr(oSel[i] + '.translateY'))
	oPos.append(mc.getAttr(oSel[i] + '.translateZ'))
	oPosFinal.append(oPos)
mc.select(cl=True)
for i in range(0,len(oPosFinal)):
	mc.joint(p=(oPosFinal[i]), radius=1)