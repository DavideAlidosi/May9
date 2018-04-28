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
INDEX = 2

from time import clock
import maya.cmds as cmds
import maya.OpenMaya as om
from SoftClusterEX.core import scData
import baseTab 
reload(scData)
reload(baseTab)


########################################################################
class TabMirror(baseTab.BaseTab):
    """"""
    _TITLE = 'Mirror'
    _INDEX = 2

    #----------------------------------------------------------------------
    def __init__(self):
        super(TabMirror, self).__init__()
        self.axisCol = ''
        self.tolTxFld = ''
        self.searchTxFld = ''
    
    #----------------------------------------------------------------------
    def createUI(self, parent):
        """"""
        layout = cmds.frameLayout( lv=0, bv=0, cll=False, mh=4, mw=4, p=parent)
        
        form = cmds.formLayout()
        optLayout = cmds.frameLayout( l='Options:', cll=False, mh=5, w=200)
        
        # Install mirror axis radio button group
        self.installMirrorAxis()
        
        # Install mirror pivot text field
        self.installMirrorPivot()
        
        # Install mirror tolerance text field
        self.installTolerance()
        
        # Install mirror search and replace text field
        self.installSearchReplace()
        cmds.setParent( '..' )
        
        # Install mirror button
        bt = self.installMirrorButton()
        
        # Arrage UI elements
        cmds.formLayout(form,
                       e=1,
                       af=[(optLayout, 'left', 0),
                           (optLayout, 'right', 0),
                           (optLayout, 'top', 0),
                           (bt, 'bottom', 0), 
                           (bt, 'right', 0),
                           (bt, 'left', 0)],
                       
                       ac=[(optLayout, 'bottom', 2, bt)])
        
        cmds.setParent( '..' )
        cmds.setParent( '..' )
        return layout
    
    #----------------------------------------------------------------------
    def installMirrorAxis(self):
        """"""
        cmds.rowLayout(nc=2, cw=[1, 80], adj=2, cl2=['right', 'left'], cat=[1, 'left', 14])
        cmds.text(l='Mirror Axis:')
        form = cmds.formLayout()
        self.axisCol = cmds.radioCollection()
        rb1 = cmds.radioButton( l='X', sl=True )
        rb2 = cmds.radioButton( l='Y' )
        rb3 = cmds.radioButton( l='Z' )
        
        cmds.formLayout(form,
                       e=1,
                       af=[(rb1, 'left', 0), (rb2, 'left', 0), (rb3, 'right', 0)], 
                       ac=[(rb2, 'left', 0, rb1), (rb2, 'right', 0, rb3)],
                       ap=[(rb1, 'right', 0, 33), (rb2, 'left', 0, 33), (rb3, 'left', 0, 67)])
        cmds.setParent( '..' )
        cmds.setParent( '..' )
        cmds.separator( st='in' )
    
    #----------------------------------------------------------------------
    def installMirrorPivot(self):
        """"""
        cmds.frameLayout(lv=False, bv=False, mw=5)
        cmds.rowLayout(nc=2, cw=(1, 65), adj=2)
        cmds.button( l='Mirror Pivot:',
                    ann="Select nothing and click will clear the text field.",
                    c=lambda *args: self.setMirrorPivotCmd() )
        self.mirPivTxFld = cmds.textField( ann="Leave it blank to use world space." )

        cmds.setParent( '..' )
        cmds.setParent( '..' )
        cmds.separator( st='in' )
    
    #----------------------------------------------------------------------
    def installTolerance(self):
        """"""
        cmds.frameLayout(lv=False, bv=False)
        self.tolTxFld = cmds.textFieldGrp( l="Tolerance:",
                                          tx=0.01,
                                          cl2=( 'right', 'left' ),
                                          cw=(1, 70), 
                                          adj=2)
        cmds.separator( st='in' )
        cmds.setParent( '..' )
    
    #----------------------------------------------------------------------
    def installSearchReplace(self):
        """"""
        cmds.frameLayout(lv=False, bv=False)
        self.searchTxFld = cmds.textFieldGrp( l='Search for:',
                                             tx='L_',
                                             cl2=( 'right', 'left' ),
                                             cw=(1, 70), 
                                             adj=2 )
        self.replaceTxFld = cmds.textFieldGrp( l='Replace with:',
                                              tx='R_',
                                              cl2=( 'right', 'left' ),
                                              cw=(1, 70), 
                                              adj=2 )
        cmds.setParent( '..' )

    #----------------------------------------------------------------------
    def installMirrorButton(self):
        """"""
        return cmds.button( l='Mirror',
                            bgc=(153.0/255, 217.0/255, 234.0/255),
                            c=lambda *args: self.mirrorClusterCmd() )

    #----------------------------------------------------------------------
    def mirrorClusterCmd(self):
        """"""
        sels = cmds.ls(sl=1, ap=1)
        if not sels: cmds.error("Please select clusters or joints!")
        
        # Prepare parameters
        axisBtn = cmds.radioCollection(self.axisCol, q=1, sl=1)
        axisId = cmds.radioButton(axisBtn, q=1, l=1).lower()
        axises = scData.getAxisMap(axisId)
        mirrorPivot = cmds.textField(self.mirPivTxFld, q=1, tx=1)
        tol = float(cmds.textFieldGrp(self.tolTxFld, q=1, tx=1))
        search = cmds.textFieldGrp(self.searchTxFld, q=1, tx=1)
        replace = cmds.textFieldGrp(self.replaceTxFld, q=1, tx=1)

        # Deal with mirror pivot matrix
        if mirrorPivot: pivotMatrixList = cmds.xform(mirrorPivot, q=1, ws=1, m=1)
        else: pivotMatrixList = scData.getWorldMatrixList()
        
        start = clock()
        for sel in sels:
            if cmds.objectType( sel, isType='joint' ):
                scData.JointFn.mirrorJnt(sel, pivotMatrixList, axises, search, replace, tol)
            elif cmds.listRelatives(sel, s=1, typ='clusterHandle'):            
                scData.ClusterFn.mirrorCluster(sel, pivotMatrixList, axises, search, replace, tol)
            else: cmds.warning("%s is skipped!" % sel)
        
        finish = clock()
        om.MGlobal.displayInfo( "Mirror Time Cost: %fs" % (finish-start) )

    #----------------------------------------------------------------------
    def setMirrorPivotCmd(self):
        """"""
        sel = cmds.ls(sl=1, ap=1)
        if sel: cmds.textField(self.mirPivTxFld, e=1, tx=sel[0])
        else: cmds.textField(self.mirPivTxFld, e=1, tx='')


#----------------------------------------------------------------------
def getTab():
    """"""
    return TabMirror()
