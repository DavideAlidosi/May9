import maya.cmds as cmds


contexts = {
    "RotateSuperContext": (cmds.manipRotateContext, "Rotate"),
    "moveSuperContext": (cmds.manipMoveContext, "Move"),
    "scaleSuperContext": (cmds.manipScaleContext, "Scale")
    }
values = {
    "RotateSuperContext": (5, 10, 30, 45, 90),
    "moveSuperContext": (.1, .5, 1, 3, 5),
    "scaleSuperContext": (.1, 1, 3, 5, 10)
    }
modes = "off", "relative", "absolute"
positions = "W", "SW", "S", "SE", "E"


def wrapper(*args):
    return lambda x: setMode(*args)


def setMode(context="moveSuperContext", mode=0, value=None):
    """set mode. 0 - no snap, 1 - relative, 2 - absolute."""

    context, name = contexts[context]
    if mode == 0:
        context(name, e=True, s=False)
    elif mode == 1:
        context(name, e=True, s=True, sr=True)
    else:
        context(name, e=True, s=True, sr=False)

    if value is not None:
        context(name, e=True, sv=value)

    if not context(name, q=True, s=True):
        cmds.inViewMessage(smg="%s OFF" % name, pos="topCenter", f=True)
    else:
        cmds.inViewMessage(smg="%s %s %.1f" % (name, modes[mode], context(name, q=True, sv=True)),
                           pos="topCenter", f=True)


def getMode(context="moveSuperContext"):
    context, name = contexts[context]
    if not context(name, q=True, s=False):
        return 0
    elif context(name, q=True, s=True) and context(name, q=True, sr=True):
        return 1
    else:
        return 2


def run(parent):
    try:
        context = cmds.currentCtx()
        mode = getMode(context)
        cmds.setParent(parent, menu=True)
        cmds.radioMenuItemCollection()
        cmds.menuItem(label="snap off", rb=mode == 0, rp="NW", c=wrapper(context, 0))
        cmds.menuItem(label="snap relative", rb=mode == 1, rp="N", c=wrapper(context, 1))
        cmds.menuItem(label="snap absolute", rb=mode == 2, rp="NE", c=wrapper(context, 2))
        new_mode = 1 if mode == 0 else mode
        for value, pos in zip(values[context], positions):
            cmds.menuItem(label=str(value), rp=pos, c=wrapper(context, new_mode, value))
    except KeyError:
        pass
