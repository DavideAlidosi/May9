oObj = mc.ls(sl=True)[0].split('.')[0]
oClst = mc.cluster(name='envelope')[1]
posX = mc.getAttr(str(oClst) + '.originX')
posY = mc.getAttr(str(oClst) + '.originY')
posZ = mc.getAttr(str(oClst) + '.originZ')
mc.move(posX,posY,posZ, oObj + '.scalePivot', oObj + '.rotatePivot')
mc.delete(oClst)
mc.select(oObj)