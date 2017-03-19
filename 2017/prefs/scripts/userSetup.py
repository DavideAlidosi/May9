#Preload Crease Set Editor
from maya.app.general import creaseSetEditor

#Preload Boss Editor
import boss.BossEditor as be

#Preload MMtoKey
import MMtoKey

#Preload Soft Cluster EX
import SoftClusterEX

#Preload Combine Curves
import amCombineCurves as amcc

#Preload SOuP Menu
import maya.cmds as cmds

def soup_menu():
    maya.mel.eval("LoadSOUP")

    if cmds.menu("soup_menu", ex=True):
        cmds.deleteUI("soup_menu")

    cmds.setParent("MayaWindow")
    cmds.menu("soup_menu", l="SOuP")

    # first
    cmds.menuItem(l="tools", sm=True, to=True)
    cmds.menuItem(l="overburn", c='mm.eval("overburn_SOuP()")')
    cmds.menuItem(l="nParticle cache manager", c=npcm_SOuP().main)
    cmds.menuItem(l="particles to curves", c=particlesToCurves_SOuP().main)
    cmds.menuItem(l="uninstancer", c=uninstancer_SOuP().main)
    cmds.menuItem(l="nucleus I/O", c=nucleusIO_SOuP().gui)
    cmds.menuItem(l="instance manager", c="instanceManager_SOuP().gui()")
    cmds.menuItem(l="directional diffusion", c="directionalDiffusion_SOuP().gui()")
    cmds.menuItem(l="point cloud builder", sm=True, to=True)
    cmds.menuItem(l="create", c=pointCloudBuilder_SOuP().create)
    cmds.menuItem(l="attach", c=pointCloudBuilder_SOuP().attach)
    cmds.menuItem(d=True)
    cmds.menuItem(l="add/remove points", c=pointCloudBuilder_SOuP().begin)
    cmds.menuItem(l="set density", c=pointCloudBuilder_SOuP()._setDensity)
    cmds.menuItem(d=True)
    cmds.menuItem(l="paint points", c=pointCloudBuilder_SOuP().begin2)
    cmds.menuItem(l="set step", c=pointCloudBuilder_SOuP()._setStep)
    cmds.menuItem(d=True)
    cmds.menuItem(l="print info", c=pointCloudBuilder_SOuP().printInfo)
    cmds.setParent("..", menu=True)
    cmds.menuItem(d=True)
    cmds.menuItem(l="fracture generator", c='mm.eval("RS_voroTexFrac_GUI()")')
    cmds.menuItem(l="rbd proxy generator", c=generateRbdProxies_SOuP().gui)
    cmds.menuItem(l="intersections", c=intersections_SOuP().gui)
    cmds.menuItem(l="split mesh by object group", c=splitMeshByObjectGroup_SOuP().main)
    cmds.menuItem(l="minimum bounding box", c=minbbox_SOuP().main)
    cmds.menuItem(l="close packed spheres", c=closePackedSpheres_SOuP().gui)
    cmds.menuItem(l="kdTree (print info)", c=kdTree_SOuP().info)
    cmds.menuItem(d=True)
    cmds.menuItem(l="shotmodel", c=soup().shotmodel)
    cmds.menuItem(l="contour deformer", c=contourDeformer_SOuP().main)
    cmds.menuItem(l="softmod", c='mm.eval("softmod_SOuP()")')
    cmds.menuItem(l="flatten", c='mm.eval("flatten_SOuP()")')
    cmds.menuItem(l="jiggle", c='mm.eval("jiggle_SOuP()")')
    cmds.menuItem(l="mirror mesh", c=mirrorMesh_SOuP().gui)
    cmds.menuItem(l="skin chop", c=skinChop_SOuP().gui)
    cmds.menuItem(l="vehicle animation system", c=vehicle_SOuP().gui)
    cmds.menuItem(l="bake arbitrary deformations", c=bakeArbDefs_SOuP().gui)
    cmds.menuItem(l="bake deformations to fk skeleton", c=bakeDefsToFkSkel_SOuP().gui)
    cmds.menuItem(l="bake animation", c="bakeAnimation_SOuP().main()")
    cmds.menuItem(l="optimize DAG hierarchies", c=optimizeDagHierarchies_SOuP().gui)
    cmds.menuItem(l="sliders manager", c=soup().loadSlidersManagerGui)
    cmds.menuItem(d=True)
    cmds.menuItem(l="array attributes manager", c=arrayAttrManager_SOuP().main)
    cmds.menuItem(l="transfer multi to multi", c=attributes_SOuP().multiAttributeTransfer)
    cmds.menuItem(l="copy array to multi", c=attributes_SOuP().arrayToMulti)
    cmds.menuItem(l="copy multi to array", c=attributes_SOuP().multiToArray)
    cmds.menuItem(l="copy multi to multi", c=attributes_SOuP().multiToMulti)
    cmds.menuItem(l="copy array to array", c=attributes_SOuP().arrayToArray)
    cmds.menuItem(l="vertex colors to texture", c=vertexColorsToTexture_SOuP().main)
    cmds.menuItem(l="soft selection to weight map (print info)", c=softSelectionToWeightMap_SOuP().info)
    cmds.menuItem(l="paint normals", sm=True, to=True)
    cmds.menuItem(l="comb", c='mm.eval("paint_PAINTNORMALS(0)")')
    cmds.menuItem(l="erase", c='mm.eval("paint_PAINTNORMALS(1)")')
    cmds.setParent("..", menu=True)
    cmds.menuItem(d=True)
    cmds.menuItem(l="deltas (print info)", c=soup().deltasInfo)
    cmds.menuItem(l="select non-overlapping points", c=attributes_SOuP().selectNonOverlappingPoints)
    cmds.menuItem(l="select points with non-zero weight", c=attributes_SOuP().selectPointsWithNonZeroWeight)
    cmds.menuItem(l="edit components list", c="attributes_SOuP().editComponentsList()")
    cmds.menuItem(l="shells (print info)", c=shells_SOuP().info)
    cmds.menuItem(d=True)
    cmds.menuItem(l="icons designer", c=soup().loadIconsDesignerGui)
    cmds.menuItem(d=True)
    cmds.menuItem(l="scripts manager", c=soup().loadScriptsManagerGui)
    cmds.menuItem(d=True)
    cmds.menuItem(l="compass", c="compass_SOuP().create(bSkipSel=False)")
    cmds.setParent("..", menu=True)

    # node types
    cmds.menuItem(l="nodes", sm=True, to=True)
    cmds.menuItem(l="trajectory", sm=True, to=True)
    cmds.menuItem(l="create", c="trajectory_SOuP().create()")
    cmds.menuItem(l="delete", c=trajectory_SOuP().delete)
    cmds.menuItem(l="set reference node", c=trajectory_SOuP().setReferenceNode)
    cmds.menuItem(l="unset reference node", c=trajectory_SOuP().unsetReferenceNode)
    cmds.menuItem(l="set manipulator scale", c=trajectory_SOuP().setManipulatorScaleUI)
    cmds.menuItem(l="toggle display time", c=trajectory_SOuP().toggleDisplayTime)
    cmds.menuItem(l="toggle performance report", c=trajectory_SOuP().togglePerformanceReport)
    cmds.setParent("..", menu=True)
    cmds.menuItem(l="displayAttributes", sm=True, to=True)
    cmds.menuItem(l="create", c=displayAttributes_SOuP().create)
    cmds.menuItem(l="delete", c=displayAttributes_SOuP().delete)
    cmds.menuItem(l="pin nodes", c=displayAttributes_SOuP().pinNodes)
    cmds.menuItem(l="unpin nodes", c=displayAttributes_SOuP().unpinNodes)
    cmds.menuItem(l="pin attributes (selected in the channelBox)", c=displayAttributes_SOuP().pinAttributes)
    cmds.menuItem(l="unpin attributes (selected in the channelBox)", c=displayAttributes_SOuP().unpinAttributes)
    cmds.menuItem(l="toggle display pinned nodes only", c=displayAttributes_SOuP().toggleDisplayPinnedOnly)
    cmds.setParent("..", menu=True)
    cmds.menuItem(l="interactiveCachingSystem-GPU", c=igpucs_SOuP().gui)
    cmds.menuItem(l="interactiveCachingSystem", c=ics_SOuP().gui)
    cmds.menuItem(l="morph", c="Morph().gui()")
    cmds.menuItem(l="blendShapesManager", c="blendShapesManager.Gui()")
    cmds.menuItem(l="stickyCurves", c="stickyCurves_SOuP().gui()")
    cmds.menuItem(l="displayDriver", c='mm.eval("displayDriverManager()")')
    cmds.menuItem(l="attributeCachingSystem", c=acs_SOuP().gui)
    cmds.menuItem(l="speedometer", c='mm.eval("speedometer()")')
    cmds.menuItem(l="cape", sm=True, to=True)
    cmds.menuItem(l="create", c=cape_SOuP().create)
    cmds.menuItem(l="add", c=cape_SOuP().add)
    cmds.menuItem(l="remove", c=cape_SOuP().remove)
    cmds.menuItem(l="print info", c=cape_SOuP().info)
    cmds.setParent("..", menu=True)
    cmds.menuItem(l="cocoon", sm=True, to=True)
    cmds.menuItem(l="create from object points", c=cocoon_SOuP().createFromObjectPoints)
    cmds.menuItem(l="create from scattered points", c=cocoon_SOuP().createFromScatteredPoints)
    cmds.setParent("..", menu=True)
    cmds.setParent("..", menu=True)

