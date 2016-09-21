oObj = mc.ls(sl=True)[0].split('.')[0]
oClst = mc.cluster(name='envelope')[1]
posX = mc.getAttr(str(oClst) + '.originX')
posY = mc.getAttr(str(oClst) + '.originY')
posZ = mc.getAttr(str(oClst) + '.originZ')
locator = mc.spaceLocator()
mc.move(posX,posY,posZ)
mc.delete(oClst)
mc.select(locator)