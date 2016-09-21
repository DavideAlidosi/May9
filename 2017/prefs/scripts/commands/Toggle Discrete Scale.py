state = mc.manipScaleContext('Scale', query=True, snap=True)
if state:
	mc.manipScaleContext('Scale', edit=True, snap=False)
else:
	mc.manipScaleContext('Scale', edit=True, snap=True)