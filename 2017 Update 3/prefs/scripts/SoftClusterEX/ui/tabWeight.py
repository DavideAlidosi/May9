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
INDEX = 3

import maya.cmds as cmds
import maya.OpenMaya as om
from SoftClusterEX.core import scData
from SoftClusterEX.startup import setup
import baseTab
reload(scData)
reload(baseTab)


########################################################################
class TabWeight(baseTab.BaseTab):
    """"""
    _TITLE = 'Weight'
    _INDEX = 3

    #----------------------------------------------------------------------
    def __init__(self):
        super(TabWeight, self).__init__()
        self.editBtn = ''
        self.doneBtn = ''
        self.appendCheck = ''
        self.detachBtn = ''
        self.influence = ''
        self._type = ''
        self.toggle = True
    
    #----------------------------------------------------------------------
    def createUI(self, parent):
        """"""
        layout = cmds.frameLayout( lv=0, bv=0, cll=False, mh=6, mw=4, p=parent)
        
        self.installRedefineSection()
        self.installExportImport()
        
        cmds.setParent( ".." )
        return layout
    
    #----------------------------------------------------------------------
    def installRedefineSection(self):
        """"""
        cmds.frameLayout( l='Redefine:', cll=False, mh=5, w=200)
        
        form1 = cmds.formLayout()
        self.installEdit()
        self.installDone()
        self.installAppendCheck()
        
        cmds.formLayout(form1,
                       e=1,
                       af=[(self.editBtn, 'left', 0),
                           (self.editBtn, 'top', 0),
                           (self.editBtn, 'bottom', 0),
                           (self.doneBtn, 'left', 0),
                           (self.doneBtn, 'top', 0),
                           (self.doneBtn, 'bottom', 0),
                           (self.appendCheck, 'right', 0),
                           (self.appendCheck, 'top', 0),
                           (self.appendCheck, 'bottom', 0)],
                       ac=[(self.doneBtn, 'left', 1, self.editBtn),
                           (self.doneBtn, 'right', 4, self.appendCheck)], 
                       ap=[(self.editBtn, 'right', 0, 42)])
        
        cmds.setParent( ".." )
        
        separator = cmds.separator( st='in' )
        
        form2 = cmds.formLayout()
        self.installDetach()
        cmds.formLayout(form2,
                       e=1,
                       af=[(self.detachBtn, 'left', 0),
                           (self.detachBtn, 'top', 0),
                           (self.detachBtn, 'bottom', 0),
                           (self.detachBtn, 'right', 0)])
        cmds.setParent( ".." )
        cmds.setParent( ".." )
    
    #----------------------------------------------------------------------
    def installEdit(self):
        """"""
        self.editBtn =  cmds.button(l="Edit",
                                   bgc=(239.0/255, 238.0/255, 179.0/255), 
                                   en=self.toggle,
                                   c=lambda *args: self.editCmd() )
        
    
    #----------------------------------------------------------------------
    def installDone(self):
        """"""
        self.doneBtn = cmds.button(l="Done",
                                   ann="Select nothing to cancel redefine weight.", 
                                   bgc=(153.0/255, 217.0/255, 234.0/255), 
                                   en=not self.toggle,
                                   c=lambda *args: self.doneCmd() )
    
    #----------------------------------------------------------------------
    def installAppendCheck(self):
        """"""
        self.appendCheck = cmds.checkBox(l='A', ann='Append weights')
        
    #----------------------------------------------------------------------
    def installDetach(self):
        """"""
        self.detachBtn = cmds.button( l="Detach", c=lambda *args: self.detachCmd() )

    #----------------------------------------------------------------------
    def installExportImport(self):
        """"""
        cmds.frameLayout( l='Export & Import:', cll=False, mh=5, w=200)
        cmds.button(l="Export",c=lambda *args: self.exportWeight() )
        cmds.button(l="Import",c=lambda *args: self.importWeight() )        
        cmds.setParent( ".." )
        
    #----------------------------------------------------------------------
    def editCmd(self):
        """"""
        self.influence = sel = self.__selectInfluence()
        
        if cmds.objectType( self.influence, isType='joint' ):
            self._type =  'joint'
            deformers = cmds.listConnections('%s.wm' % self.influence, d=1, s=0, t='skinCluster', et=1)
            
        elif cmds.listRelatives(self.influence, s=1, typ='clusterHandle'):
            self._type =  'cluster'
            deformers = cmds.listConnections('%s.wm' % self.influence, d=1, s=0, t='cluster', et=1)
        else: cmds.error("%s is unsupported type!" % self.influence)
        
        try:
            infObjs = cmds.listConnections('%s.og' % deformers[0])
            cmds.select(infObjs)
        except TypeError:
            cmds.error("Can't find geometry deformed by %s" % self.influence)
        
        # Get into component select mode
        cmds.selectMode( object=True )
        cmds.selectMode( component=True )
        self.toggleButton()
    
    #----------------------------------------------------------------------
    def doneCmd(self):
        """"""
        if cmds.ls(sl=1):
            softSelectData = scData.SoftSelectionData(None, setup.getSupportTypes().keys())
            weightData = softSelectData.getWeightData()
            append = cmds.checkBox(self.appendCheck, q=1, v=1)
            
            if self._type == 'joint':
                scData.JointFn.redefineWeight(self.influence, weightData, append)
            elif self._type == 'cluster':
                scData.ClusterFn.redefineWeight(self.influence, weightData, append)
        
        # Recover select mode
        cmds.selectMode( object=True )
        cmds.select( self.influence )
        self.toggleButton()
    
    #----------------------------------------------------------------------
    def detachCmd(self):
        """"""
        try:
            sel = cmds.ls(sl=1, ap=1)
            inf = sel.pop(0)
            
            if cmds.objectType( inf, isType='joint' ):
                scData.JointFn.detachFromGeometries(inf, sel)
            elif cmds.listRelatives(inf, s=1, typ='clusterHandle'):            
                scData.ClusterFn.detachFromGeometries(inf, sel)
            else: cmds.error("%s is unsupported type!" % inf)
        except IndexError:
            cmds.error("Please cluster (or joint) first, then geometries you want to detach!")
        
        cmds.select(inf)
        om.MGlobal.displayInfo('Detach %s from %s success.' % (inf, str(sel)))

    #----------------------------------------------------------------------
    def exportWeight(self):
        """"""
        sel = self.__selectInfluence()
        
        try:
            fileFilter = "Soft Cluster EX Weight Data (*.scw)"
            filePath = cmds.fileDialog2(fm=0, 
                                       ff=fileFilter,
                                       cap='Export Weight Data',
                                       ds=2,
                                       okc='Export')[0]
            
            if cmds.objectType( sel, isType='joint' ):
                scData.JointFn.exportWeight(sel, filePath)
            elif cmds.listRelatives(sel, s=1, typ='clusterHandle'):
                scData.ClusterFn.exportWeight(sel, filePath)
            else: cmds.error("%s is unsupported type!" % sel)
            
            om.MGlobal.displayInfo('Export to %s success.' % filePath)
        except:
            cmds.warning("Nothing to be exported.")
        
    #----------------------------------------------------------------------
    def importWeight(self):
        """"""
        sel = self.__selectInfluence()
        
        try:
            fileFilter = "Soft Cluster EX Weight Data (*.scw)"
            filePath = cmds.fileDialog2(fm=1, 
                                       ff=fileFilter,
                                       cap='Import Weight Data',
                                       dialogStyle=2,
                                       okc='Import')[0]
            
            if cmds.objectType( sel, isType='joint' ):
                scData.JointFn.importWeight(sel, filePath)
            elif cmds.listRelatives(sel, s=1, typ='clusterHandle'):
                scData.ClusterFn.importWeight(sel, filePath)
            else: cmds.error("%s is unsupported type!" % sel)
    
            om.MGlobal.displayInfo('Import weight from %s success.' % filePath)
        except:
            cmds.warning("Nothing to be imported.")
        
    #----------------------------------------------------------------------
    def toggleButton(self):
        """"""
        self.toggle = not self.toggle
        cmds.button(self.editBtn, e=1, en=self.toggle)
        cmds.button(self.doneBtn, e=1, en=not self.toggle)
    
    #----------------------------------------------------------------------
    def __selectInfluence(self):
        """"""
        try:
            return cmds.ls(sl=1, ap=1)[0]
        except IndexError:
            cmds.error("Please select cluster or joint!")


#----------------------------------------------------------------------
def getTab():
    """"""
    return TabWeight()