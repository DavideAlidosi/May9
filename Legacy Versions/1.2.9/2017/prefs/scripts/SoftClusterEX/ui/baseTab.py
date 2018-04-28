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

import maya.cmds as cmds


########################################################################
class BaseTab(object):
    _TITLE = 'Untitle'

    #----------------------------------------------------------------------
    def __init__(self):
        self.parentWindow = None
    
    #----------------------------------------------------------------------
    def title(self):
        return self._TITLE
    
    #----------------------------------------------------------------------
    def createUI(self, parent):
        """"""
        layout = cmds.columnLayout( adj=1, rowSpacing=4, columnAttach=('both', 4), p=parent )
        return layout