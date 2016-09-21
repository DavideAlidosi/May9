anti_aliasing = mc.getAttr("hardwareRenderingGlobals.multiSampleEnable")
if anti_aliasing == 0:
    mc.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)
else:
    mc.setAttr("hardwareRenderingGlobals.multiSampleEnable", 0)