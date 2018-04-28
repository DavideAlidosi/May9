"""
#----------------------------------------------------------------------
#    This file is part of "Soft Cluster EX"
#    and covered by a BSD-style license, check
#    LICENSE for detail.
#
#    Author:      Webber Huang
#    Contact:     xracz.fx@gmail.com
#    Homepage:    http://riggingtd.com
#----------------------------------------------------------------------
"""

import os
import maya.cmds as cmds
import maya.OpenMaya as om
from SoftClusterEX.core import scData, scUtil
from SoftClusterEX.startup import setup
reload(scUtil)
reload(scData)


########################################################################
class MainWindow(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(MainWindow, self).__init__()
        self.title = 'Soft Cluster EX'
        self.window = 'softClusterEXWin'
        self.mainTabLayout = None
        self.tabs = []
        self.createUI()

    #----------------------------------------------------------------------
    def createUI(self):
        """"""
        if cmds.window(self.window, ex=1): cmds.deleteUI(self.window)
        cmds.window(self.window, t='%s v%s' % (self.title, setup.getVersion()), w=230, h=260, s=1, rtf=1)

        # setup layout and ui elements
        form = cmds.formLayout()
        self.mainTabLayout = cmds.tabLayout(childResizable=True)
        cmds.formLayout( form,
                         edit=True,
                         attachForm=(
                                     (self.mainTabLayout, 'top', 0),
                                     (self.mainTabLayout, 'left', 0),
                                     (self.mainTabLayout, 'bottom', 0),
                                     (self.mainTabLayout, 'right', 0)
                                    ) )
        # Setup tab ui from modules
        tabModules = []
        for m in scUtil.findAllModules('ui'):
            mod = __import__('SoftClusterEX.ui.%s' % m, '', '', [m])
            if hasattr(mod, 'TAB') and mod.ENABLE:
                reload(mod)
                tabModules.append(mod)

        tabModules.sort(key=lambda m: m.INDEX)
        [self.addTab(m.getTab()) for m in tabModules]
        
        cmds.showWindow(self.window)
    
    #----------------------------------------------------------------------
    def addTab(self, tab):
        """
        adds tab object to tab UI, creating it's ui and attaching to main window
        """
        cmds.setParent(self.mainTabLayout)
        layout = tab.createUI(self.mainTabLayout)
        cmds.tabLayout( self.mainTabLayout, edit=True, tabLabel=((layout, tab.title())) );
        tab.parentWindow = self
        self.tabs.append(tab)
        
        return tab
    
    #----------------------------------------------------------------------
    def setHeight(self, h):
        """"""
        cmds.window(self.window, e=1, h=h)