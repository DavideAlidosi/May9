obj = mc.polyPyramid()

mc.scale(5, 5, 5)
mc.move(0, -1.75, 0, obj[0] + ".scalePivot", obj[0] + ".rotatePivot", r=True)
mc.move(0, 1.75, 0)