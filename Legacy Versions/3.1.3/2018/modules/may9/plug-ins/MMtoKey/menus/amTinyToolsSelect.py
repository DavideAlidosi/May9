import maya.cmds as cmds


def run(parent):
    """requires amTinyTools"""
    try:
        import amTinyTools
        amTinyTools.Menu.menuSelect(parent)
    except ImportError:
        cmds.confirmDialog(m="this module requires amTinyTools")
