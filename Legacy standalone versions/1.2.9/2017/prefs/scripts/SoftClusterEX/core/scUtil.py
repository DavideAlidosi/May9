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

import os, sys
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma

from SoftClusterEX.startup import setup

#----------------------------------------------------------------------    
def getDependNode(name):
    """
    Args:
      name (str)

    Returns:
      MOBject
    """
    selList = om.MSelectionList()
    selList.add (name)
    node = om.MObject()
    selList.getDependNode(0, node)
    return node

#----------------------------------------------------------------------    
def getDagPath(name):
    """
    Args:
      name (str)

    Returns:
      MDagPath
    """
    selList = om.MSelectionList()
    selList.add (name)
    dagPath = om.MDagPath()
    selList.getDagPath(0, dagPath)
    return dagPath

#----------------------------------------------------------------------    
def getComponent(name):
    """
    Args:
      name (str)

    Returns:
      MOBject
    """
    selList = om.MSelectionList()
    selList.add (name)
    dagPath = om.MDagPath()
    component = om.MObject()
    selList.getDagPath(0, dagPath, component)
    return component

#----------------------------------------------------------------------
def getDagPathComponents(compList):
    """
    Args:
      compList (list)

    Returns:
      MObject
    """
    currSel = cmds.ls(sl=1, l=1)
    cmds.select(compList, r=1)
    selList = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selList)
    dagPath = om.MDagPath()
    components = om.MObject()
    selList.getDagPath(0, dagPath, components)
    cmds.select(currSel, r=1)
    return dagPath, components

#----------------------------------------------------------------------    
def getFunctionSet(obj):
    """
    Args:
      obj (MObject)

    Returns:
      list
    """
    funcSet = []
    om.MGlobal.getFunctionSetList(obj, funcSet)
    return funcSet

#----------------------------------------------------------------------    
def getMatrixListFromPoint(point):
    """
    Args:
      point (MPoint)

    Returns:
      list
    """
    return [1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            point.x, point.y, point.z, 1]

#----------------------------------------------------------------------
def getMMatrix(matrixList):
    """"""
    matrix = om.MMatrix()
    om.MScriptUtil.createMatrixFromList( matrixList, matrix )
    return matrix

#----------------------------------------------------------------------
def getComponentMatrixList(component):
    """
    Args:
      component (str)

    Returns:
      list
    """
    pos = cmds.pointPosition(component)
    return [1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            pos[0], pos[1], pos[2], 1]

#----------------------------------------------------------------------
def getTransformMatrix(transform):
    """
    Args:
      transform (str)

    Returns:
      MMatrix
    """
    matrixList = cmds.xform(transform, q=1, ws=1, m=1)
    matrix = getMMatrix(matrixList)
    return matrix

#----------------------------------------------------------------------
def getComponentMatrix(component):
    """
    Args:
      component (str)

    Returns:
      MMatrix
    """
    matrixList = getComponentMatrixList(component)
    matrix = getMMatrix(matrixList)
    return matrix

#----------------------------------------------------------------------
def getManipulatorPosition():
    """
    Returns:
      list
    """
    cmds.setToolTo('Move')
    currentMoveMode = cmds.manipMoveContext('Move', q=True, m=True)
    cmds.manipMoveContext('Move', e=True, m=0)
    pos = cmds.manipMoveContext('Move', q=True, p=True)
    cmds.manipMoveContext('Move', e=True, m=currentMoveMode)
    return pos

#----------------------------------------------------------------------
def getPivotMatrixList(obj):
    """"""
    pos = cmds.xform( obj, q=1, ws=1, piv=1 )
    matrixList = cmds.xform( obj, q=1, ws=1, m=1 )
    matrixList[-4], matrixList[-3], matrixList[-2] = pos[0], pos[1], pos[2]
    return matrixList

#----------------------------------------------------------------------
def findAllModules(relativeDirectory):
    """
    Args:
      relativeDirectory (str)

    Returns:
      list
    """
    allPyFiles = findAllFiles(relativeDirectory, ".py")
    return [f.split('.')[0] for f in allPyFiles if not f.startswith("__init__")]

#----------------------------------------------------------------------
def findAllFiles(relativeDirectory, fileExtension):
    """
    Args:
      relativeDirectory (str)
      fileExtension (str)

    Returns:
      list
    """
    fileDirectory = os.path.join(os.environ[setup.getEnviron()], relativeDirectory)
    return [f for f in os.listdir(fileDirectory) if f.lower().endswith(fileExtension)]


"""
#----------------------------------------------------------------------
# Codes below comes from part of glTools:
# https://github.com/bungnoid/glTools/blob/master/utils/deformer.py
# I make a slightly modification to meet my own demands.
# Thanks, Grant Laker.
#----------------------------------------------------------------------
"""
# Create exception class
class UserInputError(Exception): pass

def findRelatedSkinCluster(geometry):
    '''
    Return the skinCluster attached to the specified geometry
    @param geometry: Geometry object/transform to query
    @type geometry: str
    '''
    # Check geometry
    if not cmds.objExists(geometry): raise Exception('Object '+geometry+' does not exist!')
    # Check transform
    if cmds.objectType(geometry) == 'transform':
        try: geometry = cmds.listRelatives(geometry,s=True,ni=True,pa=True)[0]
        except: raise Exception('Object %s has no deformable geometry!' % geometry)

    # Determine skinCluster
    skin = mel.eval('findRelatedSkinCluster \"%s\"' % geometry)
    if not skin: 
        skin = cmds.ls(cmds.listHistory(geometry, pdo=1, gl=1), type='skinCluster')
        if skin: skin = skin[0]
    if not skin: skin = ''

    # Return result
    return skin

#----------------------------------------------------------------------
def isDeformer(deformer):
    # Check deformer exists
    if not cmds.objExists(deformer): return False
    # Check deformer type
    nodeType = cmds.nodeType(deformer,i=1)
    if not nodeType.count('geometryFilter'): return False
    # Return result
    return True

#----------------------------------------------------------------------
def getDeformerFn(deformer):
    # Get MFnWeightGeometryFilter
    deformerObj = getDependNode(deformer)
    deformerFn = oma.MFnWeightGeometryFilter(deformerObj)

    # Return result
    return deformerFn

#----------------------------------------------------------------------
def getDeformerSet(deformer):
    # Get deformer set
    deformerSet = cmds.listConnections(deformer, s=0, d=1, type='objectSet', et=1)
    if not deformerSet:
        raise UserInputError('Unable to determine deformer set!')

    # Return result
    return deformerSet[0]

#----------------------------------------------------------------------
def getDeformerSetFn(deformer):
    # Get deformer set
    deformerSet = getDeformerSet(deformer)

    # Get MFnWeightGeometryFilter
    deformerSetObj = getDependNode(deformerSet)
    deformerSetFn = om.MFnSet(deformerSetObj)

    # Return result
    return deformerSetFn

#----------------------------------------------------------------------
def getDeformerSetMembers(deformer, geometry=''):
    # Get MFnSet
    deformerSetFn = getDeformerSetFn(deformer)

    # Get deformer set members
    deformerSetSel = om.MSelectionList()
    deformerSetFn.getMembers(deformerSetSel,1)
    deformerSetPath = om.MDagPath()
    deformerSetComp = om.MObject()

    # Get geometry index
    if geometry:
        # Initialize setSelIndex boolean
        setSelIndexFound = False

        # Check geometry
        geo = geometry
        if cmds.objectType(geometry) == 'transform':
            try:
                geometry = cmds.listRelatives(geometry,s=1,ni=1,pa=1)[0]
            except:
                raise error('Object "'+geo+'" is not a valid geometry!')
        geomPath = getDagPath(geometry)

        # Check geometry affected by deformer
        if not (geometry in getAffectedGeometry(deformer,returnShapes=1).keys()):
            raise UserInputError('Geometry "'+geometry+'" is not a affected by deformer "'+deformer+'"!')

        # Cycle through selection set members
        for i in xrange(deformerSetSel.length()):
            # Get deformer set members
            deformerSetSel.getDagPath(i,deformerSetPath, deformerSetComp)
            if geomPath == deformerSetPath:
                setSelIndexFound = True
                break

        # Check setSelIndex found
        if not setSelIndexFound:
            raise UserInputError('No valid geometryIndex found for "'+geometry+'" in deformer set for "'+deformer+'"!')
    else:
        # Get deformer set members
        deformerSetSel.getDagPath(0,deformerSetPath, deformerSetComp)

    # Return result
    return [deformerSetPath, deformerSetComp]

#----------------------------------------------------------------------
def getAffectedGeometry(deformer,returnShapes=False,fullPathNames=False):
    # Verify input
    if not isDeformer(deformer):
        raise UserInputError('Object "'+deformer+'" is not a valid deformer!')

    # Clear return array (dict)
    affectedObjects = {}

    # Get MFnGeometryFilter
    deformerObj = getDependNode(deformer)
    geoFilterFn = oma.MFnGeometryFilter(deformerObj)

    # Get output geometry
    outputObjectArray = om.MObjectArray()
    geoFilterFn.getOutputGeometry(outputObjectArray)

    # Iterate through affected geometry
    for i in xrange(outputObjectArray.length()):
        outputIndex = geoFilterFn.indexForOutputShape(outputObjectArray[i])
        outputNode = om.MFnDagNode(outputObjectArray[i])

        # Check return shapes
        if not returnShapes: outputNode = om.MFnDagNode(outputNode.parent(0))

        # Check full path
        if fullPathNames: affectedObjects[outputNode.fullPathName()] = outputIndex
        else: affectedObjects[outputNode.partialPathName()] = outputIndex

    # Return result
    return affectedObjects

#----------------------------------------------------------------------
def setWeights(deformer, weights, geometry=''):
    # Get geoShape
    geoShape = geometry
    geoObj = getDependNode(geometry)
    if geometry and geoObj.hasFn(om.MFn.kTransform):
        geoShape = cmds.listRelatives(geometry,s=True,ni=True, pa=1)[0]

    # Get deformer function set and members
    deformerFn = getDeformerFn(deformer)
    deformerSetMem = getDeformerSetMembers(deformer,geoShape)

    # Build weight array
    weightList = om.MFloatArray()
    [weightList.append(i) for i in weights]

    # Set weights
    deformerFn.setWeight(deformerSetMem[0],deformerSetMem[1],weightList)

"""
#----------------------------------------------------------------------
# Codes above comes from part of glTools:
# https://github.com/bungnoid/glTools/blob/master/utils/deformer.py
# I make a slightly modification to meet my own demands.
# Thanks, Grant Laker.
#----------------------------------------------------------------------
"""

"""
#----------------------------------------------------------------------
# Codes below comes from part of Red9 StudioTools:
# https://github.com/markj3d/Red9_StudioPack/blob/master/core/Red9_General.py
# I make a slightly modification to meet my own demands.
# Thanks, Mark Jackson.
#----------------------------------------------------------------------
"""
def os_OpenFile(filePath):
    '''
    open the given file in the default program for this OS
    '''
    import subprocess
    #log.debug('filePath : %s' % filePath)
    #filePath=os.path.abspath(filePath)
    #log.debug('abspath : %s' % filePath)
    if sys.platform == 'win32':
        os.startfile(filePath)
    elif sys.platform == 'darwin':  # macOS
        subprocess.Popen(['open', filePath])
    else:  # linux
        try:
            subprocess.Popen(['xdg-open', filePath])
        except OSError:
            raise OSError('unsupported xdg-open call??')

"""
#----------------------------------------------------------------------
# Codes below comes from part of Red9 StudioTools:
# https://github.com/markj3d/Red9_StudioPack/blob/master/core/Red9_General.py
# I make a slightly modification to meet my own demands.
# Thanks, Mark Jackson.
#----------------------------------------------------------------------
"""