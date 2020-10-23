import os
import sys
import maya.cmds as cmds
import maya.mel as mel
from . import Engine

mel.eval('source "May9_menu.mel"')
mel.eval('source "May9_core.mel"')

def ui(*args):
    """open marking menu editor"""
    import Editor
    Editor.MainWindow(engine)

def menu(parent):
    """load via amTinyTools"""
    cmds.setParent(parent, menu=True)
    cmds.menuItem(label="May9_Next", sm=True, to=True)
    cmds.menuItem(label="May9_Next", c=ui)
    cmds.setParent(u=True, menu=True)


sys.path.append(os.path.dirname(__file__))
engine = Engine.Engine()
pressSelected = engine.pressSelected    # sh, alt, ctl
releaseSelected = engine.releaseSelected
pressCustom = engine.pressCustom        # sh, alt, ctl, menu_name, menu_type
releaseCustom = engine.releaseCustom    # command, language, command_always
pressPreset = engine.pressPreset        # sh, alt, ctl
releasePreset = engine.releasePreset
