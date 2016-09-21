state = mc.selectPref(query=True, useDepth=True)
if state:
	mc.selectPref(useDepth=False)
	mc.selectPref(paintSelectWithDepth=False)
else:
	mc.selectPref(useDepth=True)
	mc.selectPref(paintSelectWithDepth=True)