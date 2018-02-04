# nurbs surfaces are not supported
# messy !

import maya.cmds as mc
import maya.OpenMaya as om

class editGroup_SOuP(object):

	__na = ""

	def main(self, sNodeAttr):

		self.__na = sNodeAttr

		if mc.window("w_EDITGROUP_SOUP", ex=True) == True: mc.deleteUI("w_EDITGROUP_SOUP")
		mc.window("w_EDITGROUP_SOUP", t="edit group")
		mc.rowColumnLayout(nc=1, cw=[(1,300)])
		mc.text("t_edit_EDITGROUP_SOUP", al="left", h=30)
		mc.rowColumnLayout(nc=4, cw=[(1,100),(2,100),(3,100)])
		mc.button(l="select", c=self.selectComponents)
		mc.button(l="replace", c=self.editComponentsUI1)
		mc.button(l="add", c=self.editComponentsUI2)
		mc.setParent("..")
		mc.setParent("..")
		mc.text("t_edit_EDITGROUP_SOUP", e=True, l=" edit: "+self.__na)
		mc.showWindow("w_EDITGROUP_SOUP")
		mc.window("w_EDITGROUP_SOUP", e=True, w=300, h=60)

	def getComponentType(self, sNode):

		sCompType = ""
		nCompType = mc.getAttr(sNode+".componentType")

		plug = om.MPlug()
		selList = om.MSelectionList()
		selList.add(sNode+".inGeometry")
		selList.getPlug(0, plug)
		sGeoType = plug.asMObject().apiTypeStr()

		if sGeoType == "kMeshData":
			if nCompType == 0:
				sCompType = "vtx"
			elif nCompType == 1:
				sCompType = "e"
			elif nCompType == 2:
				sCompType = "f"
			elif nCompType == 3:
				sCompType = "map"
			else:
				return ""
		elif sGeoType == "kNurbsCurveData":
			if nCompType == 4:
				sCompType = "cv"
			else:
				return ""
		elif sGeoType == "kVectorArrayData":
			if nCompType == 6:
				sCompType = "pt"
			else:
				return ""

		return sCompType

	def selectComponents(self, *arg):

		self.deleteGeo()

		# make sure the inGeometry attribute has input connection
		if mc.objExists(self.__na) == False: return
		sNode = self.__na.split(".")[0]
		listConn = mc.listConnections(sNode+".inGeometry", s=True, d=False, p=True) or []
		if len(listConn) == 0: return

		sCompType = self.getComponentType(sNode)

		if sCompType == "vtx":
			self.createGeo(sNode, "mesh")
			mc.hilite("editGroupGeo", r=True)
			mc.SelectVertexMask()
		elif sCompType == "e":
			self.createGeo(sNode, "mesh")
			mc.hilite("editGroupGeo", r=True)
			mc.SelectEdgeMask()
		elif sCompType == "f":
			self.createGeo(sNode, "mesh")
			mc.hilite("editGroupGeo", r=True)
			mc.SelectFacetMask()
		elif sCompType == "map":
			self.createGeo(sNode, "mesh")
			mc.hilite("editGroupGeo", r=True)
			mc.SelectUVMask()
		elif sCompType == "cv":
			self.createGeo(sNode, "nurbsCurve")
			mc.hilite("editGroupGeo", r=True)
			mc.SelectVertexMask()
		elif sCompType == "pt":
			self.createGeo(sNode, "particle")
			mc.hilite("editGroupGeo", r=True)
			mc.SelectVertexMask()
		else:
			return

		# select components
		listComps = []

		listAllComps = mc.ls("editGroupGeo."+sCompType+"[*]", fl=True) or []
		nNumComps = len(listAllComps)

		listIds = mc.getAttr(self.__na) or ""
		listIds = listIds.strip().split(" ")

		for sId in listIds:
			if sId == "":
				continue
			elif sId == "*":
				listComps.append("editGroupGeo."+sCompType+"[*]")
			elif ":" in sId:
				for i in range(int(sId.split(":")[0]), int(sId.split(":")[1])+1):
					if i > nNumComps: continue
					listComps.append(listAllComps[i])
			else:
				if int(sId) > nNumComps: continue
				listComps.append(listAllComps[int(sId)])

		if len(listComps) > 0: mc.select(listComps)
		# END select components

	def editComponentsUI1(self, *arg): self.editComponents("replace")
	def editComponentsUI2(self, *arg): self.editComponents("add")

	def editComponents(self, sOperation):

		if mc.objExists(self.__na) == False: return
		sNode = self.__na.split(".")[0]
		sCompType = self.getComponentType(sNode)

		sIds = mc.getAttr(self.__na) or ""
		sIds = sIds.strip()
		listIds = sIds.split(" ")
		if sOperation == "replace": sIds = ""

		listSel = mc.ls(sl=True, fl=True) or []
		for sSel in listSel:
			if "editGroupGeo."+sCompType not in sSel: continue
			sCompId = sSel.split(sCompType+"[")[1].split("]")[0]

			bDirty = False
			for sId in listIds:
				if sId == "*": continue
				elif ":" in sId:
					bSkip = False
					for i in range(int(sId.split(":")[0]), int(sId.split(":")[1])+1):
						if str(i) == sCompId:
							bSkip = True
							break
				else:
					if sId == sCompId: continue
				bDirty = True
				break

			if bDirty == True:
				sIds += " "+sCompId

		mc.setAttr(self.__na, sIds, typ="string")

	def createGeo(self, sNode, sGeoType):

		n = mc.createNode("transform", n="editGroupGeo", ss=True)
		mc.createNode(sGeoType, n="editGroupGeoShape", p="editGroupGeo", ss=True)

		if sGeoType != "particle":
			listConn = mc.listConnections(sNode+".inGeometry", s=True, d=False, p=True) or []
			if len(listConn) > 0: mc.connectAttr(listConn[0], n+".inMesh")
			mc.sets(n, e=True, fe="initialShadingGroup")
			mc.setAttr(n+".overrideEnabled", True)
			mc.setAttr(n+".overrideShading", False)
			mc.select(n)
		else:
			listPosPP = mc.getAttr(sNode+".inGeometry") or []
			nPntCount = len(listPosPP)/3
			mc.setAttr(n+".position", nPntCount, listPosPP, typ="vectorArray")

	def deleteGeo(self):

		listNodes = mc.ls("editGroupGeo") or []
		if len(listNodes) > 0: mc.delete(listNodes)
