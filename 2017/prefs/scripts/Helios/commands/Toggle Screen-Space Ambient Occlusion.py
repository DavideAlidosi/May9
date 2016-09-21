anti_aliasing = mc.getAttr("hardwareRenderingGlobals.ssaoEnable")
if anti_aliasing == 0:
    mc.setAttr("hardwareRenderingGlobals.ssaoEnable", 1)
else:
    mc.setAttr("hardwareRenderingGlobals.ssaoEnable", 0)