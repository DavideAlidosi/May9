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

TAB = ''
ENABLE = True
INDEX = 4

import maya.cmds as cmds
from SoftClusterEX.core import scData
from SoftClusterEX.startup import setup
import baseTab
reload(setup)
reload(scData)
reload(baseTab)


########################################################################
class TabAbout(baseTab.BaseTab):
    """"""
    _TITLE = 'About'
    _INDEX = 4

    #----------------------------------------------------------------------
    def __init__(self):
        super(TabAbout, self).__init__()
    
    #----------------------------------------------------------------------
    def createUI(self, parent):
        """"""
        layout = cmds.frameLayout( lv=0, bv=0, cll=False, mh=6, mw=4, p=parent)
        
        self.installBanner()
        self.installCopyRightInfo()
        
        cmds.setParent( ".." )
        return layout
    
    #----------------------------------------------------------------------
    def installBanner(self):
        """"""
        cmds.frameLayout( lv=0, bv=0, cll=False)
        pic = cmds.iconTextStaticLabel( style='iconOnly', image=setup.getBanner())
        cmds.setParent( ".." )
        
    #----------------------------------------------------------------------
    def installCopyRightInfo(self):
        """"""
        cmds.frameLayout(lv=False, mh=6, mw=6, w=1)
        cmds.text(l="Soft Cluster EX", fn='boldLabelFont', align='center')
        cmds.rowColumnLayout( numberOfColumns=2,
                             rowSpacing=[1, 8],
                             columnAttach=[1, "right", 5], 
                             columnAlign=[1, "right"])

        cmds.text(l="Version: ", fn='boldLabelFont')
        cmds.text(l=setup.getVersion(), align='left')

        cmds.text(l="Author: ", fn='boldLabelFont')
        cmds.text(l="Webber Huang", align='left')
        
        cmds.text(l="Contact: ", fn='boldLabelFont')
        cmds.text(l="xracz.fx@gmail.com", align='left')
        
        cmds.text(l="Project Site: ", fn='boldLabelFont')
        cmds.iconTextButton( style='textOnly',
                             l='http://riggingtd.com/downloads/soft-cluster-ex',
                             ann="Click to open in brower.", 
                             c = lambda *args: setup.openBlog() )
        
        cmds.setParent( ".." )
        cmds.setParent( ".." )
        

#----------------------------------------------------------------------
def getTab():
    """"""
    return TabAbout()