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

import os, math, collections, json, operator
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import scUtil, kdtree
from SoftClusterEX.startup import setup


__WORLD_MATRIX_LIST__ = (1.0, 0.0, 0.0, 0.0,
                         0.0, 1.0, 0.0, 0.0,
                         0.0, 0.0, 1.0, 0.0,
                         0.0, 0.0, 0.0, 1.0)

__AXIS_MAP__ = {'x'  : (1, 0, 0),
                'y'  : (0, 1, 0),
                'z'  : (0, 0, 1),
                'xy' : (1, 1, 0),
                'xz' : (1, 0, 1),
                'yz' : (0, 1, 1),
                'xyz': (1, 1, 1)}

#----------------------------------------------------------------------
def getWorldMatrixList():
    """
    Returns:
      tuple
    """
    return __WORLD_MATRIX_LIST__

#----------------------------------------------------------------------
def getAxisMap(axis):
    """
    Args:
      axis (str)
    
    Returns:
      tuple
    """
    return __AXIS_MAP__[axis]

########################################################################
class SoftSelectionData(object):
    
    #----------------------------------------------------------------------
    def __init__(self, excludeObjs=None, supportTypes=None):
        """
        Args:
          excludeObjs (str, list): Defaults to None
          supportTypes (str, list): Defaults to None
        """        
        if not cmds.ls(sl=1):
            cmds.error("Nothing selected, failure to create!") 
        
        self.components = []
        self.weights = []
        self.geometries = []
        self.shapes = []
        self.__constructData(excludeObjs, supportTypes)
   
    #----------------------------------------------------------------------
    def __constructData(self, excludeObjs=None, supportTypes=None):
        """
        Args:
          excludeObjs (str, list): Defaults to None
          supportTypes (str, list): Defaults to None
        """
        self.components = cmds.softSelectionQuery(vtx=1, ap=1, exo=excludeObjs, t=supportTypes)
        self.weights = cmds.softSelectionQuery(w=1, exo=excludeObjs, t=supportTypes)
        self.geometries = cmds.softSelectionQuery(tr=1, ap=1, exo=excludeObjs, t=supportTypes)
        self.shapes = cmds.softSelectionQuery(s=1, ap=1, exo=excludeObjs, t=supportTypes)

    #----------------------------------------------------------------------
    def getComponents(self):
        """
        Returns:
          list
        """
        return self.components
    
    #----------------------------------------------------------------------
    def getWeights(self):
        """
        Returns:
          list
        """
        return self.weights
    
    #----------------------------------------------------------------------
    def getGeometries(self):
        """
        Returns:
          list
        """
        return self.geometries
    
    #----------------------------------------------------------------------
    def getShapes(self):
        """
        Returns:
          list
        """
        return self.shapes
    
    #----------------------------------------------------------------------
    def getWeightData(self):
        """
        Returns:
          WeightData
        """
        return WeightData(self.components, self.weights)


########################################################################
class BaseData(collections.Mapping):
    
    #----------------------------------------------------------------------
    def __init__(self):
        self._data = {}
        self._dumpData = [self.__class__.__name__, self._data]
    
    #----------------------------------------------------------------------
    def getDatas(self):
        return self._data
    
    #----------------------------------------------------------------------
    def isEmpty(self):
        return self._data in ('', (), [], {}, None)
    
    #----------------------------------------------------------------------
    def exportWeight(self, filePath):
        """
        Args:
          filePath (str)
        """
        f = file(filePath, 'w')
        json.dump(self._dumpData, f, indent=True)
        f.close()
    
    #----------------------------------------------------------------------
    @classmethod
    def importWeight(cls, filePath):
        """
        Args:
          filePath (str)
        """
        f = file(filePath, 'r')
        encode = json.load(f)
        
        # Verify data
        if encode[0] != cls.__name__:
            cmds.error('Error input data file!')
        
        components, weights = [], []
        for data in encode[1].values():
            components += data[0]
            weights += data[1]
        
        return cls(components, weights)    


########################################################################
class VertexData(BaseData):
    """
    data = {vertex1: position1, vertex2: position2, ...}
    """
    

    #----------------------------------------------------------------------
    def __init__(self, vertices=[], positions=[]):
        """
        Args:
          vertices (list, optional): [vertex1, vertex2, ...], Defaults to []
          positions (list, optional): [positions1, positions2, ...], Defaults to []
        """
        super(VertexData, self).__init__()
        try:
            self._data = dict(zip(vertices, positions))
            self._auxData = dict(zip(positions, vertices))
        except Exception, e:
            raise e
        

    #----------------------------------------------------------------------
    def getPositions(self):
        """
        Returns:
          list
        """
        return self._data.values()

    #----------------------------------------------------------------------
    def getPosition(self, vertex):
        """
        Args:
         vertex (str)
        
        Returns:
          tuple
        """
        return self._data[vertex]

    #----------------------------------------------------------------------
    def getVertices(self):
        """
        Returns:
          list
        """
        return self._data.keys()
    
    #----------------------------------------------------------------------
    def getVertex(self, position):
        """
        Args:
         position (tuple)
        
        Returns:
          Vertex
        """
        return self._auxData[position]

    #----------------------------------------------------------------------
    def addVertex(self, vertex, position):
        """
        Args:
          vertex (str)
          position (tuple)
        """
        self._data[vertex] = position
        self._auxData[position] = vertex

    #----------------------------------------------------------------------
    def addVertices(self, vertices, positions):
        """
        Args:
          vertices (list)
          positions (list)
        """
        if len(vertices) != len(positions):
            cmds.error("Unmatch lenght of two input list!")
        for v, p in zip(vertices, positions):
            self.addVertex(v, p)
    
    #----------------------------------------------------------------------
    def hasPosition(self, position):
        """"""
        return self._auxData.has_key(position)
    #----------------------------------------------------------------------
    def __add__(self, other):
        """
        Args:
          other (VertexData)
          
        Returns:
          VertexData
        """
        newData = VertexData(self.getVertices(), self.getPositions())
        newData.addVertices(other.getVertices(), other.getPositions())
        return newData
    
    #----------------------------------------------------------------------
    def __iter__(self):
        """
        Yields:
          str
        """
        for v in self._data.keys():
            yield v
    
    #----------------------------------------------------------------------
    def __len__(self):
        """
        Returns:
          int
        """
        return len(self._data)
    
    #----------------------------------------------------------------------
    def __getitem__(self, key):
        """
        Returns:
          tuple
        """
        return self._data[key]


########################################################################
class WeightData(BaseData):
    """
    auxData = {component1: weight1, component2: weight2, ...}
    data = {
            geometryStr1: [[component11, component12, ...], [weight11, weight12, ...]],
            geometryStr2: [[component21, component22, ...], [weight21, weight22, ...]],
            ...
           }
    """
    
    #----------------------------------------------------------------------
    def __init__(self, elements, weights):
        """
        Args:
          elements (list): [componentStr1, componentStr2, ...], Defaults to []
          weights (list): [weight1, weight2, ...], Defaults to []
        """
        super(WeightData, self).__init__()
        self.__checkInputData(elements, weights)
        
        self._elements = elements
        self._weights = weights
        self._auxData = {}
        self._auxWeightArray = {}
        self._count = 0
        self.__constructData(elements, weights)
    
    #----------------------------------------------------------------------
    def __constructData(self, elements, weights):
        """
        Args:
          elements (list): [componentStr1, componentStr2, ...], Defaults to []
          weights (list): [weight1, weight2, ...], Defaults to []
        """
        for e, w in zip(elements, weights):
            o = e.split('.')[0]
            try:
                self._data[o][0].append(e)
                self._data[o][1].append(w)
                self._auxWeightArray[o].append(w)
            except KeyError:
                self._data[o] = [[e], [w]]
                self._auxWeightArray[o] = om.MFloatArray(1, w)
            
            self._auxData[e] = w
            self._count += 1
    
    #----------------------------------------------------------------------
    def addData(self, element, weight):
        """
        Args:
          element (str)
          weight (float)
        """
        o = element.split('.')[0]
        
        if not self.hasElement(element):
            try:
                self._data[o][0].append(element)
                self._data[o][1].append(weight)
                self._auxWeightArray[o].append(weight)
            except KeyError:
                self._data[o] = [[element], [weight]]
                self._auxWeightArray[o] = om.MFloatArray(1, weight)
            
            self._elements.append(element)
            self._weights.append(weight)            
            self._count += 1
            
        else:
            idx = self._data[o][0].index(element)
            
            weight += self._data[o][1][idx]    # This's important
            
            self._data[o][1][idx] = weight
            self._auxWeightArray[o].set(weight, idx)
            elementIdx = self._elements.index(element)
            self._weights[elementIdx] = weight
        
        self._auxData[element] = weight

    #----------------------------------------------------------------------
    def addDatas(self, elements, weights):
        """
        Args:
          elements (list)
          weights (list)
        """
        for e, w in zip(elements, weights):
            self.addData(e, w)
    
    #----------------------------------------------------------------------
    def getWeights(self):
        """
        Returns:
          list
        """
        return self._weights
    
    #----------------------------------------------------------------------
    def getElements(self):
        """
        Returns:
          list
        """
        return self._elements
        
    #----------------------------------------------------------------------
    def getWeight(self, element):
        """
        Args:
          item (str)
          
        Returns:
          float
        """
        return self._auxData[element]
    
    #----------------------------------------------------------------------
    def getGeometries(self, asGeometry=False):
        """
        Args:
         asGeometry (bool, optional): Defaults to False
        
        Returns:
          list: [geometryStr1, geometryStr2, ...]
        """
        if not asGeometry:
            return self._data.keys()
        else:
            objects = self._data.keys()
            return [Geometry.createFromTransform(o) for o in objects]
    
    #----------------------------------------------------------------------
    def getGeometryElements(self, geo, asComponents=False):
        """
        Return element list in sorted order
        
        Args:
          geo (str)
          asComponents (bool, optional): Defaults to False
        
        Returns:
          list or MObject: [componentStr1, componentStr2, ...]
        """
        result = self._data[geo][0]
        
        # Return MObject if asComponents is True
        if asComponents:
            return scUtil.getDagPathComponents(result)[1]
        return result

    #----------------------------------------------------------------------
    def getGeometryWeights(self, geo, asFloatArray=False):
        """
        Return weight list in sorted order
        
        Args:
          geo (str)
          asFloatArray (bool, optional): Defaults to False
        
        Returns:
          list or MFloatArray: [weight1, weight2, ...]
        """
        if asFloatArray:
            return self._auxWeightArray[geo]
        else:
            return self._data[geo][1]
    
    #----------------------------------------------------------------------
    def hasElement(self, element):
        """
        Args:
          element (str)
          
        Returns:
          bool: Return True if data contains this element, or False
        """
        return self._auxData.has_key(element)

    #----------------------------------------------------------------------
    def getWeightFromElement(self, Element):
        """
        Args:
          Element (str)
          
        Returns:
          float
        """
        return self._auxData[Element]
    
    
    #----------------------------------------------------------------------
    def maxWeight(self):
        """
        Returns:
          float
        """
        return max(self._weights)
    
    #----------------------------------------------------------------------
    def __checkInputData(self, elements, weights):
        """"""
        if len(elements) != len(weights):
            raise scUtil.UserInputError("Unmatch lenght of two input list!")
    
    #----------------------------------------------------------------------
    def __iter__(self):
        """
        Yields:
          str
        """
        for obj in self._data.keys():
            yield obj
    
    #----------------------------------------------------------------------
    def __len__(self):
        """
        Returns:
          int
        """
        return self._count
    
    #----------------------------------------------------------------------
    def __getitem__(self, key):
        """
        Returns:
          WeightDataNode
        """
        return self._data[key]
    
    #----------------------------------------------------------------------
    def __add__(self, other):
        """"""
        if isinstance(other, self.__class__):
            self.addDatas(other.getElements(), other.getWeights())
            return self
        return NotImplemented


########################################################################
class Transformation(object):
    
    #----------------------------------------------------------------------
    def __init__(self, matrix=None):
        """
        Args:
          matrix (MMatrix, optional): Defaults to None
        """
        if not matrix: self._matrix = om.MMatrix()
        elif type(matrix) is om.MMatrix: self._matrix = matrix
        else: raise scUtil.UserInputError('Input error, unable to create <Transformation> object!')
        
        self._transformMatrix = om.MTransformationMatrix(self._matrix)
    
    #----------------------------------------------------------------------
    @classmethod
    def createFromMatrixList(cls, matrixList):
        """
        Args:
          matrixList (list)
          
        Returns:
          Transformation
        """
        matrix = scUtil.getMMatrix(matrixList)
        return cls(matrix)
    
    #----------------------------------------------------------------------
    @classmethod
    def createFromObject(cls, obj):
        """
        Args:
          obj (str)
              
        Returns:
          Transformation
        """
        comp = scUtil.getComponent(obj)
        funcSet = scUtil.getFunctionSet(comp)
        
        # Create from transform
        if not funcSet:
            return cls(scUtil.getTransformMatrix(obj))
        else:
            # Create from component
            if 'kComponent' in funcSet:
                return cls(scUtil.getComponentMatrix(obj))
            else:
                raise scUtil.UserInputError('Input error, unable to create '
                                            '<Transformation> object from %s!' % obj)
    
    #----------------------------------------------------------------------
    def setMatrix(self, matrix):
        """
        Args:
          matrix (MMatrix)
        """
        if type(matrix) is om.MMatrix: self._matrix = matrix
        else: raise scUtil.UserInputError('Input error, please input MMatrix type!')
        self._transformMatrix = om.MTransformationMatrix(self._matrix)
    
    #----------------------------------------------------------------------
    def asMatrix(self):
        """
        Returns:
          MMatrix
        """
        return self._matrix
    
    #----------------------------------------------------------------------
    def asTransformationMatrix(self):
        """
        Returns:
          MTransformationMatrix
        """
        return self._transformMatrix
    
    #----------------------------------------------------------------------
    def asMatrixList(self):
        """
        Returns:
          list
        """
        m = self._matrix
        return [m(0, 0), m(0, 1), m(0, 2), m(0, 3),
                 m(1, 0), m(1, 1), m(1, 2), m(1, 3),
                 m(2, 0), m(2, 1), m(2, 2), m(2, 3),
                 m(3, 0), m(3, 1), m(3, 2), m(3, 3)]
    
    #----------------------------------------------------------------------
    def __getMirrorMatrix(self, pivotTransform, axises):
        """
        Args:
          pivotTransform (Transformation)
          axises (list)
          
        Returns:
          MMatrix
        """
        # Check input
        if not type(pivotTransform) is Transformation:
            raise scUtil.UserInputError('The first argument should be a <Transformation> object!')
        
        # construst a reflect matrix
        pivotMatrix = pivotTransform.asMatrix()
        x, y, z = pow(-1, axises[0]), pow(-1, axises[1]), pow(-1, axises[2])
        m = pivotTransform.asMatrixList()
        reflectMatrixList = [x * m[0],  x * m[1],  x * m[2],  m[3],
                             y * m[4],  y * m[5],  y * m[6],  m[7],
                             z * m[8],  z * m[9],  z * m[10], m[11],
                             1 * m[12], 1 * m[13], 1 * m[14], m[15]]
    
        reflectMatrix = scUtil.getMMatrix(reflectMatrixList)
    
        localMatrix = self._matrix * pivotMatrix.inverse() 
        return localMatrix * reflectMatrix
    
    #----------------------------------------------------------------------
    def getMirrorTransformation(self, pivotTransform, axises):
        """
        Args:
          pivotTransform (Transformation)
          axises (list)
          
        Returns:
          Transformation
        """
        mirrorMatrix = self.__getMirrorMatrix(pivotTransform, axises)
        return Transformation(mirrorMatrix)
        
    #----------------------------------------------------------------------
    def getPoint(self, space=om.MSpace.kWorld):
        """
        Args:
          space (MSpace,optional): Defaults to om.MSpace.kWorld
          
        Returns:
          MPoint
        """
        v = self._transformMatrix.getTranslation(space)
        return om.MPoint(v.x, v.y, v.z)
    
    #----------------------------------------------------------------------
    def getEulerRotation (self):
        """
        Returns:
          MEulerRotation
        """
        return self._transformMatrix.eulerRotation()
    
    #----------------------------------------------------------------------
    def getTranslate(self, space=om.MSpace.kWorld):
        """
        extract translation
        
        Args:
          space (MSpace,optional): Defaults to om.MSpace.kWorld
          
        Returns:
          tuple
        """
        pt = self.getPoint(space)
        return (pt[0], pt[1], pt[2])
    
    #----------------------------------------------------------------------
    def getRotate(self):
        """
        extract rotation
        
        Returns:
          tuple
        """
        eulerRot = self.getEulerRotation()
        angles = [math.degrees(angle) for angle in (eulerRot.x, eulerRot.y, eulerRot.z)]
        return tuple(angles)
    
    #----------------------------------------------------------------------
    def getScale(self, space=om.MSpace.kWorld):
        """
        extract scales
        
        Args:
          space (MSpace,optional): Defaults to om.MSpace.kWorld
        
        Returns:
          tuple
        """
        util = om.MScriptUtil()
        util.createFromList([0,0,0],3)
        utilPtr = util.asDoublePtr()
        self._transformMatrix.getScale(utilPtr, space)
        scales = [om.MScriptUtil.getDoubleArrayItem(utilPtr,i) for i in xrange(3)]
        return tuple(scales)
    
    #----------------------------------------------------------------------
    def inverse(self):
        """
        Returns:
          Transformation
        """
        matrix = self.asMatrix().inverse()
        return Transformation(matrix)
        
    #----------------------------------------------------------------------
    def __eq__(self, other):
        """"""
        return self.asMatrix() == other.asMatrix()
    
    #----------------------------------------------------------------------
    def __mul__(self, other):
        """
        Args:
          other (Transformation)
          
        Returns:
          Transformation
        """
        matrix = self.asMatrix() * other.asMatrix()
        return Transformation(matrix)


########################################################################
class Geometry(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, dagPath=None):
        """
        Args:
          dagPath (MDagPath, optional): Defaults to None
        """
        # Check input
        if not dagPath: self._dagPath = om.MDagPath()
        elif type(dagPath) is om.MDagPath:
            self._dagPath = dagPath
        else:
            raise scUtil.UserInputError('Input error, the first argument '
                                        'is not a MDagPath object!')        
        
        
    #----------------------------------------------------------------------
    @classmethod
    def createFromTransform(cls, transform):
        """
        Args:
          transform (str)
          
        Returns:
          Geometry
        """
        dagPath = scUtil.getDagPath(transform)
        return cls(dagPath)
    
    #----------------------------------------------------------------------
    def setDagPath(self, dagPath):
        """
        Args:
          dagPath (MDagPath)
        """
        self._dagPath.set(dagPath)
    
    #----------------------------------------------------------------------
    def getDagPath(self):
        """
        Returns:
          MDagPath
        """
        return self._dagPath
    
    #----------------------------------------------------------------------
    def name(self):
        """
        Returns:
          str
        """
        return self._dagPath.fullPathName()
    
    #----------------------------------------------------------------------
    def iterator(self):
        """
        Returns:
          MItGeometry
        """
        return om.MItGeometry(self._dagPath)
    
    #----------------------------------------------------------------------
    def getVertexData(self):
        """
        Returns:
          VertexData
        """
        data = VertexData()
        geoIter = self.iterator()
        selList = om.MSelectionList()
        selStrs = []
        while not geoIter.isDone():
            selList.clear()
            currItem = geoIter.currentItem()
            selList.add(self._dagPath, currItem)
            
            selList.getSelectionStrings(selStrs)
            element = selStrs.pop()
            
            currPt = geoIter.position(om.MSpace.kWorld)
            data.addVertex(element, (currPt.x, currPt.y, currPt.z))
            geoIter.next()
        
        return data
    
    #----------------------------------------------------------------------
    def getVertexDataInBoundingBox(self, boundingBox, tol=0.0):
        """
        Args:
          boundingBox (BoundingBox)
          tol (float, optional): Defaults to 0.0
          
        Returns:
          VertexData
        """
        data = VertexData()
        geoIter = self.iterator()
        selList = om.MSelectionList()
        selStrs = []        
        while not geoIter.isDone():
            currPt = geoIter.position(om.MSpace.kWorld)
            ptBBox = om.MBoundingBox()
            ptBBox.expand(currPt)
            
            if boundingBox.contains(currPt) or boundingBox.intersects(ptBBox, tol):
                selList.clear()
                currItem = geoIter.currentItem()
                selList.add(self._dagPath, currItem)
                
                selList.getSelectionStrings(selStrs)
                element = selStrs.pop()
                
                data.addVertex(element, (currPt.x, currPt.y, currPt.z))
            geoIter.next()
        
        return data


########################################################################
class BoundingBoxFn(object):
    """"""
    
    #----------------------------------------------------------------------
    @classmethod    
    def createFromObjects(cls, objects):
        """
        Args:
          objects (list): [str1, str2, ...]
        
        Returns:
          MBoundingBox
        """
        if type(objects) is str:
            objects = [objects]
        
        boudingBox = om.MBoundingBox()
        for obj in objects:
            dagPath = scUtil.getDagPath(obj)
            dagFn = om.MFnDagNode(dagPath)
            boudingBox.expand(dagFn.boundingBox())
        return boudingBox
    
    #----------------------------------------------------------------------
    @classmethod    
    def createFromComponents(cls, components):
        """
        Args:
          components (list): [str1, str2, ...]
        
        Returns:
          MBoundingBox
        """
        if type(components) is str:
            components = [components]
        
        boudingBox = om.MBoundingBox()
        for comp in components:
            pos = cmds.pointPosition(comp)
            boudingBox.expand( om.MPoint(pos[0], pos[1], pos[2]) )
        return boudingBox    
    
    #----------------------------------------------------------------------
    @classmethod
    def mirrorBoundingBox(cls, boundingBox, pivotTransform, axises):
        """
        Args:
          boundingBox (MBoundingBox)
          pivotTransform (Transformation)
          axises (list)
          
        Returns:
          MBoundingBox
        """
        minMatrixList = scUtil.getMatrixListFromPoint(boundingBox.min())
        maxMatrixList = scUtil.getMatrixListFromPoint(boundingBox.max())
        
        minTrans = Transformation.createFromMatrixList(minMatrixList)
        maxTrans = Transformation.createFromMatrixList(maxMatrixList)
        
        mirrorMinTrans = minTrans.getMirrorTransformation(pivotTransform, axises)
        mirrorMaxTrans = maxTrans.getMirrorTransformation(pivotTransform, axises)
        
        return om.MBoundingBox(mirrorMinTrans.getPoint(), mirrorMaxTrans.getPoint())


########################################################################
class Deformer(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, deformer=None):
        """
        Args:
          deformer (str)
        """
        self._deformer = deformer
        if deformer:
            self._deformerFn = scUtil.getDeformerFn(deformer)
    
    def setDeformer(self, deformer):
        self._deformer = deformer
        self._deformerFn = scUtil.getDeformerFn(deformer)
        return self    
    
    #----------------------------------------------------------------------
    def getOutputGeometry(self, asTransform=True):
        """
        Args:
          asTransform (bool, optional)
          
        Returns:
          list: [Geometry1, Geometry2, ...]
        """
        objs = om.MObjectArray()
        self._deformerFn.getOutputGeometry(objs)
        
        result = []
        for i in xrange(objs.length()):
            dagFn = om.MFnDagNode(objs[i])
            if asTransform:
                parent = dagFn.parent(0)
                dagFn = om.MFnDagNode(parent)
            currName = dagFn.fullPathName()
            currGeo = Geometry.createFromTransform(currName)
            result.append(currGeo)
        return result
    
    #----------------------------------------------------------------------
    def getComponents(self, noZeroWeight=False):
        """
        Args:
          noZeroWeight (bool): Defaults to False
        
        Returns:
          list: [component1, component2, ...]
        """
        result = []
        objSet = scUtil.getDeformerSet(self._deformer)
        components = cmds.filterExpand(cmds.sets(objSet, q=1), sm=(28, 31, 36, 46))
        components = cmds.ls(components, ap=1) 
        weights = cmds.percent(self._deformer, components, q=1, v=1)
        
        if noZeroWeight:
            for comp, w in zip(components, weights):
                if w > 0:
                    result.append(comp)
            return result
        return components
    
    #----------------------------------------------------------------------
    def flushWeights(self, geometry):
        """"""
        # Get deformer function set and members
        deformerSetMem = scUtil.getDeformerSetMembers(self._deformer, geometry)

        # Build weight array
        cmpFn = om.MFnComponent(deformerSetMem[1])
        weightList = [0] * cmpFn.elementCount()

        # Set weights
        scUtil.setWeights(self._deformer, weightList, geometry)
        
    #----------------------------------------------------------------------
    def flushAllWeights(self):
        """"""
        deformerSetFn = scUtil.getDeformerSetFn(self._deformer)
        deformerSetSel = om.MSelectionList()
        deformerSetFn.getMembers(deformerSetSel, 1)

        for i in xrange(deformerSetSel.length()):
            deformerSetPath = om.MDagPath()
            deformerSetComp = om.MObject()
            deformerSetSel.getDagPath(i, deformerSetPath, deformerSetComp)
            deformerDagFn = om.MFnDagNode(deformerSetPath.transform())

            # Build weight array
            cmpFn = om.MFnComponent(deformerSetComp)
            weightList = [0] * cmpFn.elementCount()
            
            # Set weights
            scUtil.setWeights(self._deformer, weightList, deformerDagFn.fullPathName())
        
    #----------------------------------------------------------------------
    def getWeightData(self, noZeroWeight=False):
        """"
        Args:
          noZeroWeight (bool): Defaults to False
          
        Returns:
          WeightDataNode
        """
        components = self.getComponents(noZeroWeight)
        weights = cmds.percent(self._deformer, components, q=1, v=1)
        return WeightData(components, weights)
    
    #----------------------------------------------------------------------
    def setWeightData(self, weightData, setPartial=True):
        """
        Args:
          weightData (WeightData)
          setPartial (bool, optional): Defaults to True
        
        Returns:
          bool: Return True if perform weights setting correctly
        """
        for geo, data in weightData.items():
            if not cmds.objExists(geo):
                cmds.warning("%s is skipped since it doesn't exist!" % geo)
                continue            
            geoDag = scUtil.getDagPath(geo)
            selList = om.MSelectionList()
            selStrs = []

            if len(data[0]) < 7000 and setPartial:
                components = weightData.getGeometryElements(geo, True)
                weights = weightData.getGeometryWeights(geo, True)
                
                # Set weights
                self.flushWeights(geo)
                self._deformerFn.setWeight(geoDag, components, weights)
            
            else:
                geoIter = om.MItGeometry(geoDag)
                weights = []
                # construct weight list
                while not geoIter.isDone():
                    selList.clear()
                    currItem = geoIter.currentItem()
                    selList.add(geoDag, currItem)
                    
                    selList.getSelectionStrings(selStrs)
                    element = selStrs.pop()

                    if weightData.hasElement(element):
                        weights.append(weightData.getWeightFromElement(element))
                    else:
                        weights.append(0)
                    geoIter.next()
                
                # Set weights
                scUtil.setWeights(self._deformer, weights, geo)
        return True


########################################################################
class ObjectFilter(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, typeIter=None):
        """
        Args:
          typeIter (MIteratorType, optional): Defaults to None
        """
        if not typeIter:
            self._filter = om.MIteratorType()
        elif type(typeIter) is om.MIteratorType:
            self._filter = typeIter
        else: raise scUtil.UserInputError('Input error, the first argument '
                                          'should be <MIteratorType> object!')
    
    #----------------------------------------------------------------------
    @classmethod
    def createFromObjects(cls, objs):
        """
        Args:
          list
        """
        typeIter = om.MIteratorType()
        types = om.MIntArray()
        
        for o in objs:
            dag = scUtil.getDagPath(o)
            dag.extendToShapeDirectlyBelow(0)
            types.append(dag.apiType())
            
        typeIter.setFilterList(types)
        return cls(typeIter)
    
    #----------------------------------------------------------------------
    def getGeometries(self, asGeometry=True):
        """
        Args:
          asGeometry (bool, optional): Defaults to True
          
        Returns:
          list: [MDagPath1, MDagPath2, ...]
        """
        result = []
        dagIt = om.MItDag(self._filter, om.MItDag.kDepthFirst)
        while not dagIt.isDone():
            dagPath = om.MDagPath()
            dagIt.getPath(dagPath)
            
            if self.__isSkip(dagPath):
                dagIt.next()
                continue
            
            name = dagPath.fullPathName()
            if asGeometry:
                result.append(Geometry.createFromTransform(name))
            else:
                result.append(name)
            dagIt.next()
    
        return result
    
    #----------------------------------------------------------------------
    def getIntersectObjects(self, boundingBox, tol=0.0, asGeometry=True):
        """
        Args:
          boundingBox (MBoundingBox)
          tol (float, optional): Defaults to 0.0
          asGeometry (bool, optional): Defaults to True
         
        Returns:
          list: [str1, str2,...]
        """
        result = []
        dagIt = om.MItDag(self._filter, om.MItDag.kDepthFirst)
        
        while not dagIt.isDone():
            dagPath = om.MDagPath()
            dagIt.getPath(dagPath)
            
            if self.__isSkip(dagPath):
                dagIt.next()
                continue
            
            objDagFn = om.MFnDagNode(dagPath)
            objBB = objDagFn.boundingBox()
            objBB.transformUsing(dagPath.inclusiveMatrix())    
            if objBB.intersects(boundingBox, tol):
                name = dagPath.fullPathName()
                if asGeometry:
                    result.append(Geometry.createFromTransform(name))
                else:
                    result.append(name)
            dagIt.next()
        return result
    
    #----------------------------------------------------------------------
    def __isSkip(self, dagPath):
        """"""
        dagFn = om.MFnDagNode(dagPath)
        if dagFn.isIntermediateObject():
            return True
        
        if setup.mayaVersion() > 2012:
            if not dagPath.isVisible():
                return True
        
        return False

########################################################################
class KDTree(object):
    """
    A wrapper of kdtree for my own demands
    """

    #----------------------------------------------------------------------
    def __init__(self, point_list=None, dimensions=None, axis=0, sel_axis=None):
        """
        Args:
          point_list (list, optional): [(pt1.x, pt1.y, pt1.z), (pt2.x, pt2.y, pt2.z), ...],
                                       Defaults to None
          dimensions (int, optional): Defaults to None
          axis (int, optional): Defaults to 0
          sel_axis (lambda, optional): Defaults to None
        """
        self._tree = kdtree.create(point_list, dimensions, axis, sel_axis)
        
    #----------------------------------------------------------------------
    def nearestPoint(self, point, dist=None):
        """
        Args:
          point (tuple, list)
          dist (lambda)
        
        Returns:
          list or tuple
        """
        return self._tree.search_nn(point, dist)[0].data
    
    #----------------------------------------------------------------------
    def kNearestPoint(self, point, k, dist=None):
        """
        Args:
          point (tuple, list)
          k (int)
          dist (lambda)
        
        Returns:
          list
        """
        return self._tree.search_knn(point, k, dist)


########################################################################
class BaseInfluenceFn(object):
    
    @classmethod
    def flushWeights(cls):
        pass
    
    #----------------------------------------------------------------------
    @classmethod
    def redefineWeight(cls, influence, weightData, append=False):
        """
        Args:
          influence (str)
          weightData (WeightData)
          append (bool, Optional): Defaults to False
        """
        
        if append:
            weightData += cls.getWeightData(influence)
            weightData = cls.sortWeightData(weightData)
            if weightData.maxWeight() > 1.0:
                weightData = cls.shrinkWeightData(weightData)
            
        cls.flushWeights(influence)
        cls.setWeightData(influence, weightData)        
        
    #----------------------------------------------------------------------
    @classmethod
    def exportWeight(cls, deformer, filePath):
        """
        Args:
          deformer (str)
          filePath (str)
        """
        weightData = cls.getWeightData(deformer)
        weightData.exportWeight(filePath)
    
    #----------------------------------------------------------------------
    @classmethod
    def importWeight(cls, deformer, filePath):
        pass
    
    #----------------------------------------------------------------------
    @classmethod
    def attachToGeometries(cls):
        pass
    
    #----------------------------------------------------------------------
    @classmethod
    def detachFromGeometries(cls):
        pass
    
    #----------------------------------------------------------------------
    @classmethod
    def getWeightData(cls):
        pass
    
    #----------------------------------------------------------------------
    @classmethod
    def setWeightData(cls):
        pass    

    #----------------------------------------------------------------------
    @classmethod
    def getMirrorPosition(cls, matrixList, pivotMatrixList, axises):
        """
        Args:
          matrixList (list, tuple)
          pivotMatrixList (list, tuple)
          axises (list, tuple)
        
        Returns:
          list
        """
        trans = Transformation.createFromMatrixList(matrixList)
        pivotTransform = Transformation.createFromMatrixList(pivotMatrixList)
        return trans.getMirrorTransformation(pivotTransform, axises).getTranslate()
    
    #----------------------------------------------------------------------
    @classmethod
    def constructMirrorVertexData(cls, components, geoList, pivotTransform, axises, tol):
        """
        Args:
          components (list)
          geoList (list)
          pivotTransform (Transformation)
          axises (list, tuple)
          tol (float)
        
        Returns:
          VertexData
        """
        # Calculate influenced objects' boundingBox and mirror it
        boundingBox = BoundingBoxFn.createFromComponents(components)    
        boundingBox = BoundingBoxFn.mirrorBoundingBox(boundingBox, pivotTransform, axises)
    
        # Figure out geometries that will be processed
        objFilter = ObjectFilter.createFromObjects(geoList)
        intersectObjs = objFilter.getIntersectObjects(boundingBox, tol)
        if not intersectObjs: cmds.error("Can't found any geometries at the mirror side!")
    
        # Iterate geometry vertices
        vertexData = VertexData()
        for geo in intersectObjs:
            if pivotTransform.asMatrixList() == __WORLD_MATRIX_LIST__:
                vertexData += geo.getVertexDataInBoundingBox(boundingBox, tol)
            else:
                vertexData += geo.getVertexData()
        
        if vertexData.isEmpty(): cmds.error("Can't found any vertices at the mirror side!")
        return vertexData
        
    #----------------------------------------------------------------------
    @classmethod
    def constructMirrorWeightData(cls, vertexData, weightData, pivotTransform, axises):
        """
        Args:
          vertexData (VertexData)
          weightData (WeightData)
          pivotTransform (Transformation)
          axises (list, tuple)
          
        Returns:
         WeightData
        """
        # Build k-d tree
        tree = KDTree(vertexData.getPositions())
    
        # Search mirror vertices and construct new weight data
        elements, weights = [], []
        for geo, data in weightData.items():
            for vtx, w in zip(data[0], data[1]):
                # Mirror query position
                matrix = scUtil.getComponentMatrixList(vtx)
                trans = Transformation.createFromMatrixList(matrix)
                mirrorTrans = trans.getMirrorTransformation(pivotTransform, axises)
                mirrorPos = mirrorTrans.getTranslate()
                
                # Find the nearest vertex
                v = vertexData.getVertex(tree.nearestPoint(mirrorPos))
                elements.append(v)
                weights.append(w)
        
        return WeightData(elements, weights)
    
    #----------------------------------------------------------------------
    @classmethod
    def getMirrorWeightData(cls, deformer, pivotMatrixList, axises, tol=0.01):
        """
        Args:
          deformer (str): deformer name, cluster or joint
          pivotMatrixList (list, tuple)
          axises (list, tuple)
          tol (float, optional): Defaults to 0.01
        
        Returns:
          WeightData
        """
        # Fetch deformer's weight data
        weightData = cls.getWeightData(deformer)
        pivotTransform = Transformation.createFromMatrixList(pivotMatrixList)
    
        # Construct mirror VertexData
        components = weightData.getElements()
        geometries = weightData.getGeometries()
        vertexData = cls.constructMirrorVertexData(components, geometries, pivotTransform, axises, tol)
        
        # Construct mirror WeightData and return
        return cls.constructMirrorWeightData(vertexData, weightData, pivotTransform, axises)
        
    #----------------------------------------------------------------------
    @classmethod
    def sortWeightData(cls, weightData):
        """
        Args:
          weightData (WeightData)
        
        Returns:
          WeightData
        """
        geoObjs = weightData.getGeometries(asGeometry=True)
        elements, weights, selStrs = [], [], []
        selList = om.MSelectionList()
        
        for geo in geoObjs:
            geoDag = geo.getDagPath()
            geoIter = geo.iterator()
            while not geoIter.isDone():
                selList.clear()
                currItem = geoIter.currentItem()
                selList.add(geoDag, currItem)
                
                selList.getSelectionStrings(selStrs)
                element = selStrs.pop()
                elements.append(element)
                
                if weightData.hasElement(element):
                    weights.append(weightData.getWeightFromElement(element))
                else:
                    weights.append(0)
                geoIter.next()
        
        nonZeroIdx = [i for i, w in enumerate(weights) if w > 0]
        elements = [elements[i] for i in nonZeroIdx]
        weights = [weights[i] for i in nonZeroIdx]
        
        return WeightData(elements, weights)
    
    #----------------------------------------------------------------------
    @classmethod
    def shrinkWeightData(cls, weightData):
        """
        Args:
          weightData (WeightData)
        
        Returns:
          WeightData
        """
        newWeights = [w if w <1 else 1 for w in weightData.getWeights()]
        return WeightData(weightData.getElements(), newWeights)
    

########################################################################
class ClusterFn(BaseInfluenceFn):
    """"""
    
    @classmethod
    def flushWeights(cls, clusterHandle):
        """
        Args:
          clusterHandle (str)
        """
        clusterNode = cmds.listConnections('%s.wm' % clusterHandle ,d=1, s=0, t='cluster', et=1)[0]
        deformer = Deformer(clusterNode)
        deformer.flushAllWeights()
                
    #----------------------------------------------------------------------
    @classmethod
    def getWeightData(cls, clusterHandle):
        """
        Args:
          clusterHandle (str)
          
        Returns:
          WeightData
        """
        clusterNode = cmds.listConnections('%s.wm' % clusterHandle ,d=1, s=0, t='cluster', et=1)[0]
        clusterObj = Deformer(clusterNode)
        return clusterObj.getWeightData(True)
    
    #----------------------------------------------------------------------
    @classmethod
    def importWeight(cls, clusterHandle, filePath):
        """
        Args:
          cluster (str)
          filePath (str)
        """
        weightData = WeightData.importWeight(filePath)
        cluster = cmds.listConnections('%s.wm' % clusterHandle ,d=1, s=0, t='cluster', et=1)[0]
        deformer = Deformer(cluster)
        
        # Make sure geometries in weightData has been weighted before set weights
        cls.attachToGeometries(cluster, weightData.getGeometries())
        deformer.setWeightData(weightData)
        
    #----------------------------------------------------------------------
    @classmethod
    def setWeightData(cls, clusterHandle, weightData, setPartial=True):
        """
        Args:
          clusterHandle (str)
          weightData (WeightData)
          setPartial (bool, optional): Defaults to True
        """
        clusterNode = cmds.listConnections('%s.wm' % clusterHandle ,d=1, s=0, t='cluster', et=1)[0]
        cls.attachToGeometries(clusterHandle, weightData.getGeometries())
        cluster = Deformer(clusterNode)
        cluster.setWeightData(weightData, setPartial)
        
    #----------------------------------------------------------------------
    @classmethod
    def repositionCluster(cls, clusterHandle, pos):
        """
        Args:
          clusterHandle (str)
          pos (list, tuple)
        """
        cmds.xform(clusterHandle, a=True, ws=True, piv=(pos[0], pos[1], pos[2]))
        clusterShape = cmds.listRelatives(clusterHandle, c=True, s=True)
        cmds.setAttr(clusterShape[0] + '.origin', pos[0], pos[1], pos[2])
    
    #----------------------------------------------------------------------
    @classmethod
    def createCluster(cls, name='', pos=(0, 0, 0), weightData=None, setPartial=True):
        """
        Args:
          name (str, optional): Defaults to ''
          pos (list, tuple, optional): Defaults to (0, 0, 0)
          weightData (WeightData, optional): Defaults to None
          setPartial (bool, optional): Defaults to True
        """
        objects = weightData.getGeometries()
        clusterNode, clusterHandle = cmds.cluster(objects, n=name.split('|')[-1])
        
        # Set cluster weights
        if weightData != None:
            cls.setWeightData(clusterHandle, weightData, setPartial)
                
        
        # Re-Position cluster
        cls.repositionCluster(clusterHandle, pos)
        return clusterHandle
    
    #----------------------------------------------------------------------
    @classmethod
    def createSoftCluster(cls, excludeObjs=None, supportTypes=None):
        """
        Args:
          excludeObjs (list, optional): Defaults to None
          supportTypes (list, optional): Defaults to None
        """    
        # determind select objects
        try:
            initSel = cmds.ls(sl=1, ap=1, st=1)
            firstSelObj, firstSelType = initSel[0], initSel[1]
        except:
            cmds.error("Please select geometry component!")
    
        if firstSelType == 'transform':
            name = firstSelObj
        elif firstSelType in ['float3', 'double3']:
            name = cmds.listRelatives(cmds.listRelatives(p=True, f=1), p=True, f=1)[0]
        else:
            cmds.error('Selected objects Unsupported!')
    
        # query manipulator's position
        pos = scUtil.getManipulatorPosition()
    
        # query influenced elements and correspond weights
        softSelectData = SoftSelectionData(excludeObjs, supportTypes)
        weightData = softSelectData.getWeightData()
    
        # create cluster with elements and set weights
        clusterHandle = cls.createCluster(name, pos, weightData, True)
        return cmds.rename(clusterHandle, '%s_softCluster' % clusterHandle)
    
    #----------------------------------------------------------------------
    @classmethod
    def mirrorCluster(cls, cluster, pivotMatrixList, axises, search='', replace='', tol=0.01):
        """
        Args:
          cluster (str): cluster node
          pivotMatrixList (list, tuple)
          axises (list, tuple)
          search (str, optional): Defaults to ''
          replace (str, optional): Defaults to ''
          tol (float, optional): Defaults to 0.01
        
        Returns:
          str
        """
        # Construct mirror WeightData
        weightData = cls.getMirrorWeightData(cluster, pivotMatrixList, axises, tol)
    
        # Create cluster
        matrixList = scUtil.getPivotMatrixList(cluster)
        pos = cls.getMirrorPosition(matrixList, pivotMatrixList, axises)
        clusterHandle = cls.createCluster(cluster, pos, weightData, False)
        
        # Rename cluster and return
        newName = cluster.replace(search, replace).split('|')[-1]
        return cmds.rename(clusterHandle, newName)
    
    #----------------------------------------------------------------------
    @classmethod
    def attachToGeometries(cls, cluster, geometries):
        """
        Args:
          cluster (str)
          geometries (list, tuple)
        """
        infGeos = cmds.cluster(cluster, q=1, g=1)
        for geo in geometries:
            if cmds.objExists(geo) and (not infGeos or not geo in infGeos):
                cmds.cluster(cluster, e=1, g=geo)
    
    #----------------------------------------------------------------------
    @classmethod
    def detachFromGeometries(cls, cluster, geometries):
        """
        Args:
          cluster (str)
          geometries (list, tuple)
        """
        for geo in geometries:
            cmds.cluster(cluster, e=1, g=geo, rm=1, rg=1)



########################################################################
class SkinWeightData(BaseData):
    """
    data = {
              component1: {influence1: weight11, influence2: weight12, ...},
              component2: {influence1: weight21, influence2: weight22, ...},
              ...
            }
    """
    _MAX_WEIGHT = 1.0

    #----------------------------------------------------------------------
    def __init__(self, elements, influences, weights):
        """
        Args:
          elements (list)
          influences (list)
          weights (list)
        """
        super(SkinWeightData, self).__init__()
        self._data = {}
        self._auxData = elements
        self._count = 0
        
        self.__constructData(elements, influences, weights)
    
    #----------------------------------------------------------------------
    def __constructData(self, elements, influences, weights):
        """
        Args:
          elements (list)
          influences (list)
          weights (list)
        """        
        infNum = len(influences)

        for i in xrange(len(weights)):
            infId = i % infNum
            elementId = i / infNum
            inf = influences[infId]
            element = elements[elementId]
            if infId == 0:
                geo = element.split('.')[0]
                self._data[element] = {}
                self._count += 1
            self._data[element][inf] = weights[i]
        
    #----------------------------------------------------------------------
    def getData(self):
        """
        Returns:
          dict
        """
        return self._data
    
    #----------------------------------------------------------------------
    def addInfluence(self, element, influence, weight):
        """
        Args:
          element (str)
          influence (str)
          weight (float)
        """
        if self._data.has_key(element):
            for e, d in self._data.iteritems():
                if e == element:
                    self.__normalizeDict(d, self._MAX_WEIGHT-weight)
                    d[influence] = weight
                elif not d.has_key(influence):
                    d[influence] = 0.0
        else:
            cmds.error("Don't contain %s in current data!" % element)
    
    #----------------------------------------------------------------------
    def getComponents(self):
        """
        Returns:
          list
        """
        return self._auxData
    
    #----------------------------------------------------------------------
    def getInfluences(self):
        """
        Returns:
          list
        """
        return self._data[self._auxData[0]].keys()
    
    #----------------------------------------------------------------------
    def getWeights(self):
        """
        Returns:
          list
        """
        result = []        
        for comp in self._auxData:
            result += self._data[comp].values()
        return result
    
    #----------------------------------------------------------------------
    def __normalizeDict(self, d, normal=1.0):
        """
        Args:
        d (dict)
        normal (float, Optional): Defaults to 1.0
        """
        try:
            factor = normal/math.fsum(d.itervalues())
        except ZeroDivisionError:
            factor = 0.0
        
        for k in d:
            d[k] = d[k]*factor
        
        key_for_max = max(d.iteritems(), key=operator.itemgetter(1))[0]
        diff = normal - math.fsum(d.itervalues())
        d[key_for_max] += diff
    
    #----------------------------------------------------------------------
    def __iter__(self):
        """
        Yields:
          str
        """
        for comp in self._auxData:
            yield comp
    
    #----------------------------------------------------------------------
    def __len__(self):
        """
        Returns:
          int
        """
        return self._count
    
    #----------------------------------------------------------------------
    def __getitem__(self, key):
        """
        Returns:
          dict
        """
        return self._data[key]    


########################################################################
class SkinClusterFn(object):
    
    def __init__(self, skinCluster=None):
        """
        Args:
          skinCluster (str, Optional): Defaults to None
        """
        self.skinCluster = skinCluster
        if skinCluster:
            self.fn = oma.MFnSkinCluster(scUtil.getDependNode(skinCluster))
        
    def setSkinCluster(self, skinCluster):
        """
        Args:
          skinCluster (str, Optional): Defaults to None
        
        Returns:
          SkinClusterFn
        """        
        self.skinCluster = skinCluster
        self.fn = oma.MFnSkinCluster(scUtil.getDependNode(skinCluster))
        return self
        
    def getLogicalInfluenceIndex(self,influence):
        """
        Args:
          influence (str)
        
        Returns:
          int
        """        
        try:
            dagPath = scUtil.getDagPath(influence)
        except:
            raise scUtil.UserInputError("Could not find influence '%s' in %s" %
                                        (influence, self.skinCluster))
            
        return self.fn.indexForInfluenceObject(dagPath)
    
    #----------------------------------------------------------------------
    def getPhysicalInfluenceIndex(self, influence):
        """
        Args:
          influence (str)
        
        Returns:
          int
        """ 
        matrices = cmds.listConnections("%s.matrix" % self.skinCluster, s=1, d=0)
        return matrices.index(influence)
    
    #----------------------------------------------------------------------
    def getInfluenceData(self, influence):
        """
        Args:
          influence (str)
        
        Returns:
          WeightData
        """
        try:
            dagPath = scUtil.getDagPath(influence)
        except:
            raise scUtil.UserInputError("Could not find influence '%s' in %s" %
                                        (influence, self.skinCluster))        
        selList = om.MSelectionList()
        weights = om.MDoubleArray()
        
        self.fn.getPointsAffectedByInfluence(dagPath, selList, weights)
    
        componentStr = []
        selList.getSelectionStrings(componentStr)
        componentStr = cmds.ls(componentStr, ap=1, fl=1)
        weights = [w for w in weights]

        return WeightData(componentStr, weights)
        
    #----------------------------------------------------------------------
    def listInfluences(self):
        """
        Returns:
          list
        """         
        dagPaths = om.MDagPathArray()
        
        self.fn.influenceObjects(dagPaths)
        result = []
        for i in range(dagPaths.length()):
            result.append(dagPaths[i].partialPathName())
        
        return result

    #----------------------------------------------------------------------
    def getWeightData(self, elements):
        """
        Args:
          elements (list)
        
        Returns:
          SkinWeightData
        """
        dagPath, components = scUtil.getDagPathComponents(elements)
        
        # Get all influences
        infs = self.listInfluences()
        influenceIndices = om.MIntArray()
        [influenceIndices.append(self.getPhysicalInfluenceIndex(inf)) for inf in infs]
        
        # Get all weights
        weights = om.MDoubleArray()
        self.fn.getWeights(dagPath, components, influenceIndices, weights)
        weights = [w for w in weights]
        
        return SkinWeightData(elements, infs, weights)
    
    #----------------------------------------------------------------------
    def setWeightData(self, data, normalize=True):
        """
        Args:
          data (SkinWeightData)
          normalize (bool, Optional): Defaults to True
        """
        # Construct dagPath and components
        compList = data.getComponents()
        dagPath, components = scUtil.getDagPathComponents(compList)
        
        # Construct influence indices
        influenceIndices = om.MIntArray()
        [influenceIndices.append(self.getPhysicalInfluenceIndex(inf)) for inf in data.getInfluences()]
        
        # Construct weights
        weights = om.MDoubleArray()
        [weights.append(w) for w in data.getWeights()]
        oldValues = om.MDoubleArray()
        self.fn.getWeights(dagPath, components, influenceIndices, oldValues)
        
        self.fn.setWeights(dagPath, components, influenceIndices, weights, normalize, oldValues)
    
    #----------------------------------------------------------------------
    def flushWeights(self, influence):
        """
        Args:
          influence (str)
        """        
        weightData = self.getInfluenceData(influence)
        skinData = SkinWeightData(weightData.getElements(), [influence], weightData.getWeights())
        [skinData.addInfluence(comp, influence, 0.0) for comp in skinData.getComponents()]
        self.setWeightData(skinData)


########################################################################
class JointFn(BaseInfluenceFn):
    """"""
    
    #----------------------------------------------------------------------
    @classmethod
    def importWeight(cls, joint, filePath):
        """
        Args:
          cluster (str)
          filePath (str)
        """
        cls.flushWeights(joint)
        weightData = WeightData.importWeight(filePath)
        cls.setWeightData(joint, weightData)

    @classmethod
    def flushWeights(cls, joint):
        """
        Args:
          joint (str)
        """
        skinFn = SkinClusterFn()
        skins = cmds.listConnections('%s.wm' % joint ,d=1, s=0, t='skinCluster', et=1)
        try:
            for skin in skins:
                skinFn.setSkinCluster(skin)
                [cmds.setAttr('%s.liw' % inf, 0) for inf in skinFn.listInfluences()]
                skinFn.flushWeights(joint)
        except TypeError:
            return
            
    #----------------------------------------------------------------------
    @classmethod
    def setWeightData(cls, joint, weightData):
        """
        Args:
          joint (str)
          weightData (WightData)
        """
        skins = cls.attachToGeometries(joint, weightData.getGeometries())
        skinFn = SkinClusterFn()
        for geo, skin in zip(weightData.getGeometries(), skins):
            if not skin: continue
            
            skinFn.setSkinCluster(skin)
            skinData = skinFn.getWeightData(weightData.getGeometryElements(geo))
            
            for v, w in zip(weightData.getGeometryElements(geo), weightData.getGeometryWeights(geo)):
                skinData.addInfluence(v, joint, w)
            
            skinFn.setWeightData(skinData, True)
            [cmds.setAttr('%s.liw' % inf, 0) for inf in skinFn.listInfluences()]
    
    #----------------------------------------------------------------------
    @classmethod
    def getWeightData(cls, joint):
        """
        Args:
          joint (str)
          
        Returns:
          WeightData
        """
        skins = cmds.listConnections('%s.wm' % joint ,d=1, s=0, t='skinCluster', et=1)
        skinFn = SkinClusterFn()
        weightData = WeightData([], [])
        
        if skins:
            for skin in skins:
                skinFn.setSkinCluster(skin)
                weightData += skinFn.getInfluenceData(joint)
        
        return weightData
    
    #----------------------------------------------------------------------
    @classmethod
    def createJoint(cls, name, pos, weightData):
        """
        Args:
          name (str)
          pos (list)
          weightData (WeightData)
                
        Returns:
          str
        """
        cmds.select(cl=1)
        joint = cmds.joint(n="%s" % name.split('|')[-1], p=pos, rad=0.2)
        cls.setWeightData(joint, weightData)
        
        return joint
        
    #----------------------------------------------------------------------
    @classmethod
    def createSoftJoint(cls, excludeObjs=None, supportTypes=None):
        """
        Args:
          excludeObjs (list)
          supportTypes (list)
        
        Returns:
          str
        """
        # determind select objects
        try:
            initSel = cmds.ls(sl=1, ap=1, st=1)
            firstSelObj, firstSelType = initSel[0], initSel[1]
        except:
            cmds.error("Please select geometry component!")        
    
        if firstSelType == 'transform':
            name = firstSelObj
        elif firstSelType in ['float3', 'double3']:
            name = cmds.listRelatives(cmds.listRelatives(p=True, f=1), p=True, f=1)[0]
        else:
            cmds.error('Selected objects Unsupported!')
    
        # query manipulator's position
        pos = scUtil.getManipulatorPosition()
    
        # query influenced elements and correspond weights
        softSelectData = SoftSelectionData(excludeObjs, supportTypes)
        weightData = softSelectData.getWeightData()
        
        return cls.createJoint("%s_jnt" % name, pos, weightData)
        
    #----------------------------------------------------------------------
    @classmethod
    def mirrorJnt(cls, joint, pivotMatrixList, axises, search='', replace='', tol=0.01):
        """
        Args:
          joint (str): joint name
          pivotMatrixList (list, tuple)
          axises (list, tuple)
          search (str, optional): Defaults to ''
          replace (str, optional): Defaults to ''
          tol (float, optional): Defaults to 0.01
        
        Returns:
          str
        """
        # Construct mirror WeightData
        weightData = cls.getMirrorWeightData(joint, pivotMatrixList, axises, tol)
        
        # Reconstruct weightData with all of geometry vertices to keep sorted order
        weightData = cls.sortWeightData(weightData)
        
        # Create joint
        matrixList = cmds.xform(joint, q=1, ws=1, m=1)
        pos = cls.getMirrorPosition(matrixList, pivotMatrixList, axises)
        newJoint = cls.createJoint(joint, pos, weightData)
        
        # Rename joint and return
        newName = joint.replace(search, replace).split('|')[-1]
        return cmds.rename(newJoint, newName)
    
    #----------------------------------------------------------------------
    @classmethod
    def attachToGeometries(cls, joint, geometries):
        """
        Args:
          joint (str)
          geometries (list, tuple)
        
        Returns:
          list
        """
        skins = []
        for geo in geometries:
            if not cmds.objExists(geo):
                skins.append(None)
                cmds.warning("%s is skipped since it doesn't exist!" % geo)
                continue
            skin = scUtil.findRelatedSkinCluster(geo)
            
            # Make sure current geometry has been deformed by skin cluster before further operation
            if not skin:
                cmds.select(cl=1)
                baseJnt = cmds.joint(n="%s_base_jnt" % geo.split('|')[-1], rad=0.2)
                skin = cmds.skinCluster(baseJnt, geo, tsb=True, nw=1, sm=0)[0]
            
            influences = cmds.skinCluster(skin, q=True, inf=True)
            [cmds.setAttr('%s.liw' % inf, 1) for inf in influences]   # Lock all influence before add, this's important
            if not joint in influences:
                cmds.skinCluster(skin, e=1, ai=joint, lw=True)
            
            skins.append(skin)
        return skins
    
    #----------------------------------------------------------------------
    @classmethod
    def detachFromGeometries(cls, joint, geometries):
        """
        Args:
          joint (str)
          geometries (list, tuple)
        """
        for geo in geometries:
            skin = scUtil.findRelatedSkinCluster(geo)
            try:
                cmds.skinCluster(skin, e=1, ri=joint)
            except:
                cmds.warning("%s is skipped!" % geo)

