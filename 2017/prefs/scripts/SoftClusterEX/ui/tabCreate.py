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
INDEX = 1

from time import clock
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
from SoftClusterEX.core import scData
from SoftClusterEX.startup import setup
import baseTab
reload(scData)
reload(baseTab)
reload(setup)


########################################################################
class TabCreate(baseTab.BaseTab):
    """"""
    _TITLE = 'Create'
    _INDEX = 1

    #----------------------------------------------------------------------
    def __init__(self):
        super(TabCreate, self).__init__()
        self.mainFormLayout = ''
        self.supportTypeCB = []
        self.checkAllCB = ''
        self.excludeScrollList = ''
        self.falloffModeOption = ''
        self.gradient = ''
        self.interpOption = ''
        self.excludeItems = ''
        self._supportTypes = setup.getSupportTypes()
        self.keepCheck = ''
        self.jointCheck = ''
        self.createBtn = ''

    #----------------------------------------------------------------------
    def createUI(self, parent):
        """"""
        layout = cmds.frameLayout( lv=0, bv=0, cll=False, mh=4, mw=4, p=parent)
        
        self.mainFormLayout = cmds.formLayout()
        optLayout = self.installOption()

        # Install exclude object list
        excludeList = self.installExcludeObjectList()
        
        # Install falloff gradient
        gradient = self.installFalloffGradient()
        
        # Install create button
        createForm = self.installCreateButton()
        convertForm = self.installConvertButton()
        
        # Arrage UI elements
        cmds.formLayout(self.mainFormLayout,
                        e=1,
                        af=[(optLayout, 'left', 0),
                            (optLayout, 'right', 0),
                            (optLayout, 'top', 0),
                            (excludeList, 'left', 0),
                            (excludeList, 'right', 0),
                            (excludeList, 'top', 0),
                            (gradient, 'left', 0),
                            (gradient, 'right', 0),
                            (gradient, 'top', 0),
                            (createForm, 'top', 0), 
                            (createForm, 'bottom', 0), 
                            (createForm, 'right', 0),
                            (createForm, 'left', 0),
                            (convertForm, 'bottom', 0), 
                            (convertForm, 'right', 0),
                            (convertForm, 'left', 0)],
                        
                        ac=[(excludeList, 'top', 2, optLayout),
                            (gradient, 'top', 2, excludeList), 
                            (createForm, 'top', 2, gradient), 
                            (createForm, 'bottom', 2, convertForm)])
        
        cmds.setParent( '..' )
        cmds.setParent( '..' )
        return layout
    
    #----------------------------------------------------------------------
    def installOption(self):
        """"""
        layout = cmds.frameLayout( "optionLayout",
                                   l='Options:',
                                   cl=True,
                                   cll=True,
                                   ec=lambda *args: self.resizeMainWindow(),
                                   cc=lambda *args: self.resizeMainWindow())
        # Install support types check boxes
        self.installSupportTypeCheckbox()
        
        # Install convert option
        self.installConvertOption()
        
        cmds.setParent( '..' )
        return layout
        
    #----------------------------------------------------------------------
    def installConvertOption(self):
        """"""
        cmds.rowLayout(nc=2, adj=2)
        cmds.text(l=' Convert:', fn='boldLabelFont')
        self.keepCheck = cmds.iconTextCheckBox( st='textOnly', l='Keep original', v=True )
        cmds.setParent( '..' )
        cmds.separator( style='none' )
        
    #----------------------------------------------------------------------
    def installSupportTypeCheckbox(self):
        """"""
        layout = cmds.frameLayout( l='Support Types:', cl=False, cll=False)
        cmds.rowColumnLayout(numberOfRows=2)

        for typeName in self._supportTypes:
            self.supportTypeCB.append(cmds.checkBox(l='%s' % self._supportTypes[typeName]))
            cmds.checkBox(self.supportTypeCB[-1], e=1, cc=lambda *args: self.toggleAllCB())
        
        self.checkAllCB = cmds.checkBox( l='All', cc=lambda *args: self.toggleAllSupportTypesCB())
        cmds.setParent( '..' )
        cmds.setParent( '..' )
        self.setDefaultSupportTypes()
        return layout

    #----------------------------------------------------------------------
    def installExcludeObjectList(self):
        """"""
        layout = cmds.frameLayout( "exclusiveLayout",
                                   l='Exclude Objects:',
                                   cl=True,
                                   cll=True,
                                   ec=lambda *args: self.resizeMainWindow(),
                                   cc=lambda *args: self.resizeMainWindow())
        self.excludeScrollList = cmds.textScrollList(allowMultiSelection=True)
        cmds.popupMenu()
        cmds.menuItem(l='Add', c=lambda *args: self.addExcludeObjectsCmd())
        cmds.menuItem(l='Delete', c=lambda *args: self.deleteExcludeObjectsCmd())
        cmds.menuItem(l='Clear', c=lambda *args: self.clearExcludeObjectsCmd())
        cmds.setParent( '..' )
        return layout
    
    #----------------------------------------------------------------------
    def installFalloffOption(self):
        """"""
        self.falloffModeOption = cmds.optionMenuGrp( l='Falloff Mode:',
                                                     cc=lambda *args: self.changeFalloffMode(),
                                                     cl2=('left', 'left'),
                                                     cw=(1, 70),
                                                     adj=2 )
        cmds.menuItem( l='Volume' )
        cmds.menuItem( l='Surface' )
        cmds.menuItem( l='Global' )
        self.setDefaultFalloffMode()
        return self.falloffModeOption
    
    #----------------------------------------------------------------------
    def installInterpolationOption(self):
        """"""
        self.interpOption = cmds.optionMenuGrp(l='Interpolation:',
                                               cc=lambda *args: self.changeInterpolationValue(),
                                               cl2=('left', 'left'),
                                               cw=(1, 70),
                                               adj=2)
        cmds.menuItem( l='None' )
        cmds.menuItem( l='Linear' )
        cmds.menuItem( l='Smooth' )
        cmds.menuItem( l='Spline' )
        self.setDefaultInterpolation()
        return self.interpOption
    
    #----------------------------------------------------------------------
    def softSelectCurveKeyChanged(self):
        """"""
        interp = cmds.gradientControlNoAttr(self.gradient, q=1, civ=1)
        cmds.optionMenuGrp(self.interpOption, e=1, sl=interp+1)
    
    #----------------------------------------------------------------------
    def changeSoftSelectValue(self):
        curveValue = cmds.gradientControlNoAttr(self.gradient, q=1, asString=1)
        cmds.softSelect(e=1, ssc=curveValue)
    
    #----------------------------------------------------------------------
    def changeInterpolationValue(self):
        interp = cmds.optionMenuGrp(self.interpOption, q=1, sl=1)
        cmds.gradientControlNoAttr(self.gradient, e=1, civ=interp-1)
        
    #----------------------------------------------------------------------
    def installFalloffGradient(self):
        """"""
        layout = cmds.frameLayout( "falloffLayout",
                                   l='Falloff:',
                                   cl=True,
                                   cll=True,
                                   mw=5,
                                   mh=5,
                                   ec=lambda *args: self.resizeMainWindow(),
                                   cc=lambda *args: self.resizeMainWindow())
        
        # Install falloff mode scroll List
        cmds.rowLayout(nc=2, adj=1)
        falloffMode = self.installFalloffOption()
        resetBtn = cmds.button(l='Reset', c=lambda *args: self.resetFalloff(), w=40)
        cmds.setParent( '..' )
        
        # Install falloff gradient control
        self.gradient = cmds.gradientControlNoAttr( 'falloffCurve', h=90)
        self.copyFromMayaFalloffCurve()
        cmds.gradientControlNoAttr( 'falloffCurve',
                                    e=True,
                                    optionVar='falloffCurveOptionVar',
                                    changeCommand=lambda *args: self.changeSoftSelectValue(),
                                    currentKeyChanged=lambda *args: self.softSelectCurveKeyChanged() )
        
        # Install interpolation scroll List
        interpolation = self.installInterpolationOption()
        
        cmds.setParent( '..' )
        return layout
    
    #----------------------------------------------------------------------
    def installCreateButton(self):
        """"""
        layout = cmds.frameLayout("createLayout", lv=False, bv=False)
        form = cmds.formLayout()
        self.createBtn = cmds.iconTextButton(st='iconOnly',
                                             l='Create',
                                             ann="Create cluster by default, turn on \"J\" to create joint.",
                                             c=lambda *args: self.createSoftDeformerCmd() )
        
        self.jointCheck = cmds.iconTextCheckBox(st='textOnly',
                                                l='   J   ',
                                                ann="Create joint",
                                                cc=lambda *args: self.setCreateBtnIcon())
        cmds.formLayout(form,
                        e=1,
                        af=[(self.createBtn, 'left', 0),
                            (self.createBtn, 'right', 0),
                            (self.createBtn, 'top', 0),
                            (self.createBtn, 'bottom', 0),
                            (self.jointCheck, 'right', 0),
                            (self.jointCheck, 'top', 0)]
                        )
        cmds.setParent( '..' )
        cmds.setParent( '..' )
        
        self.setCreateBtnIcon()
        return layout
          
    #----------------------------------------------------------------------
    def installConvertButton(self):
        """"""
        layout = cmds.frameLayout("convertLayout", lv=False, bv=False)
        cmds.button( l='Convert',
                     ann='Cluster <-->  Joint', 
                     bgc=(153.0/255, 217.0/255, 234.0/255),
                     c=lambda *args: self.convertDeformerCmd() )
        cmds.setParent( '..' )
        return layout

    #----------------------------------------------------------------------
    def addExcludeObjectsCmd(self):
        """"""
        sel = cmds.ls(sl=1, ap=1)
        self.excludeItems = cmds.textScrollList(self.excludeScrollList, q=1, ai=1)

        for obj in sel:
            if not self.excludeItems:
                cmds.textScrollList(self.excludeScrollList, e=1, a=obj)
            elif not obj in self.excludeItems:
                cmds.textScrollList(self.excludeScrollList, e=1, a=obj)

    #----------------------------------------------------------------------
    def clearExcludeObjectsCmd(self):
        """"""
        cmds.textScrollList(self.excludeScrollList, e=1, ra=1)

    #----------------------------------------------------------------------
    def deleteExcludeObjectsCmd(self):
        """"""
        selItems = cmds.textScrollList(self.excludeScrollList, q=1, si=1)
        cmds.textScrollList(self.excludeScrollList, e=1, ri=selItems)

    #----------------------------------------------------------------------
    def createSoftDeformerCmd(self):
        """"""
        self.excludeItems = cmds.textScrollList(self.excludeScrollList, q=1, ai=1)

        supportTypes = []
        for typeCB, typeName in zip(self.supportTypeCB, self._supportTypes):
            if cmds.checkBox(typeCB, q=1, v=1):
                supportTypes.append(typeName)

        if not supportTypes:
            cmds.error('Please check at least one support type!')
        
        start = clock()
        
        if not cmds.iconTextCheckBox(self.jointCheck, q=1, v=1):
            scData.ClusterFn.createSoftCluster(self.excludeItems, supportTypes)
        else:
            scData.JointFn.createSoftJoint(self.excludeItems, supportTypes)
            
        finish = clock()
        om.MGlobal.displayInfo( "Create Time Cost: %fs" % (finish-start) )
    
    #----------------------------------------------------------------------
    def convertDeformerCmd(self):
        """"""
        sels = cmds.ls(sl=1, ap=1)
        if not sels: cmds.error("Please select clusters or joints!")
            
        start = clock()
        for sel in sels:
            if cmds.objectType( sel, isType='joint' ):
                self.jointToCluster(sel)
            elif cmds.listRelatives(sel, s=1, typ='clusterHandle'):
                self.clusterToJoint(sel)
            else: cmds.warning("%s is skipped!" % sel)
            
            if not cmds.iconTextCheckBox(self.keepCheck, q=1, v=1):
                cmds.delete(sel)
        finish = clock()
        om.MGlobal.displayInfo( "Convert Time Cost: %fs" % (finish-start) )
            
    #----------------------------------------------------------------------
    def clusterToJoint(self, clusterHandle):
        """
        Args:
          clusterNode (str)
        """
        weightData = scData.ClusterFn.getWeightData(clusterHandle)
        pos = cmds.xform(clusterHandle, q=1, ws=1, piv=1)[0:3]
        scData.JointFn.createJoint(clusterHandle, pos, weightData)
        
    #----------------------------------------------------------------------
    def jointToCluster(self, joint):
        """
        Args:
          joint (str)
        """
        weightData = scData.JointFn.getWeightData(joint)
        pos = cmds.xform(joint, q=1, ws=1, t=1)
        scData.ClusterFn.createCluster(joint, pos, weightData, True)
            
    #----------------------------------------------------------------------
    def changeFalloffMode(self):
        """"""
        selIndex = cmds.optionMenuGrp(self.falloffModeOption, q=1, sl=1) - 1
        cmds.softSelect(ssf=selIndex)

    #----------------------------------------------------------------------
    def setDefaultFalloffMode(self):
        """"""
        cmds.optionMenuGrp(self.falloffModeOption, e=1, sl=2)
        cmds.softSelect(ssf=1)
    
    #----------------------------------------------------------------------
    def setDefaultInterpolation(self):
        cmds.optionMenuGrp(self.interpOption, e=1, sl=3)
    
    #----------------------------------------------------------------------
    def copyFromMayaFalloffCurve(self):
        """"""
        # Read maya's native soft select falloff curve
        curveValue = cmds.softSelect(q=1, ssc=1).split(',')
        curveValue = zip(curveValue[0::3], curveValue[1::3], curveValue[2::3])
        curveValue = [','.join(v) for v in curveValue]
        
        if cmds.optionVar( exists='falloffCurveOptionVar' ):
            cmds.optionVar( clearArray='falloffCurveOptionVar' )

        [cmds.optionVar( stringValueAppend=['falloffCurveOptionVar', v] ) for v in curveValue]
        
        cmds.gradientControlNoAttr( self.gradient, e=True, optionVar='falloffCurveOptionVar' )
    
    #----------------------------------------------------------------------
    def setDefaultFalloffCurve(self):
        """"""
        cmds.optionVar( clearArray='falloffCurveOptionVar' )
        cmds.optionVar(stringValueAppend=[ 'falloffCurveOptionVar', '0,1,2'])
        cmds.optionVar(stringValueAppend=[ 'falloffCurveOptionVar', '1,0,2'])
        cmds.gradientControlNoAttr( self.gradient, e=True, optionVar='falloffCurveOptionVar' )
        cmds.gradientControlNoAttr( self.gradient, e=True, asString='0,1,2,1,0,2' )
        cmds.softSelect(e=1, ssc='0,1,2,1,0,2')
    
    #----------------------------------------------------------------------
    def resetFalloff(self):
        """"""
        self.setDefaultFalloffMode()
        self.setDefaultInterpolation()
        self.setDefaultFalloffCurve()
        
    #----------------------------------------------------------------------
    def setDefaultSupportTypes(self):
        """"""
        for typeCB in self.supportTypeCB:
            cmds.checkBox(typeCB, e=1, v=1)

        cmds.checkBox(self.checkAllCB, e=1, v=1)

    #----------------------------------------------------------------------
    def toggleAllSupportTypesCB(self):
        """"""
        checkAll = cmds.checkBox(self.checkAllCB, q=1, v=1)
        for typeCB in self.supportTypeCB:
            cmds.checkBox(typeCB, e=1, v=checkAll)

    #----------------------------------------------------------------------
    def toggleAllCB(self):
        """"""
        enableAll = True
        for typeCB in self.supportTypeCB:
            if not cmds.checkBox(typeCB, q=1, v=1):
                enableAll = False
                break

        cmds.checkBox(self.checkAllCB, e=1, v=enableAll)
    
    #----------------------------------------------------------------------
    def setCreateBtnIcon(self):
        """"""
        if cmds.iconTextCheckBox(self.jointCheck, q=1, v=1):
            cmds.iconTextButton(self.createBtn, e=1, i=setup.getBannerJ())
        else:
            cmds.iconTextButton(self.createBtn, e=1, i=setup.getBanner())
    
    #----------------------------------------------------------------------
    def resizeMainWindow(self):
        """"""
        totalHeight = 0
        for child in cmds.formLayout(self.mainFormLayout, q=1, ca=1):
            h = cmds.frameLayout(child, q=1, h=1)
            if cmds.frameLayout(child, q=1, collapse=1): h = 20
            totalHeight += h

        self.parentWindow.setHeight(totalHeight)


#----------------------------------------------------------------------
def getTab():
    """"""
    return TabCreate()