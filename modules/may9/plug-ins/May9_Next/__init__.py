import maya.mel as mel
import maya.cmds as cmds

cmds.loadPlugin("MMtoKey")

mel.eval('source "May9_menu.mel"')
mel.eval('source "May9_core.mel"')