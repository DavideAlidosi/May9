state = mc.manipMoveContext('Move', query=True, snap=True)
if state:
	mc.manipMoveContext('Move', edit=True, snap=False)
else:
	mc.manipMoveContext('Move', edit=True, snap=True)