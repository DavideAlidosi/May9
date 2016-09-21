state = mc.softSelect(query=True, softSelectEnabled=True)
if state:
	mc.softSelect(softSelectEnabled=False)
else:
	mc.softSelect(softSelectEnabled=True)