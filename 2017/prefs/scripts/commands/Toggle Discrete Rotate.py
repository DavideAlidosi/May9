state = mc.manipRotateContext('Rotate', query=True, snap=True)
if state:
	mc.manipRotateContext('Rotate', edit=True, snap=False)
else:
	mc.manipRotateContext('Rotate', edit=True, snap=True)