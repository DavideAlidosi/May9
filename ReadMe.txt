May9 Next 10 - A new user experience for Autodesk Maya 2017, 2018 and 2019


General info
May9 Next is a plug-in aim to offer an alternative user experience for Autodesk Maya designed to improve the speed of daily workflow and maximize new tools learning.
May9 Next streamline the most common commands into a single keyboard button (Z), by predicting them from the context.


Installation
1) If is open close Autodesk Maya
2) Copy modules folder present in this archive in:
	Windows: \Users\<username>\Documents\maya\modules
	Mac OS: /Users/<username>/Library/Preferences/Autodesk/maya/modules
	Linux: ~<username>/maya/modules
3) Open Autodesk Maya and run source May9.mel as MEL command


Release Note
- Unified installation process, is highly recommended a new installation instead update it
- Compatibility to any Workspace, anyway the use of Maya Classic is high suggested
- May9 Next Hotkey Set are added over standards ones and do not substitute the user hotkeys
- Tested and develop on Autodesk Maya 2019, Autodesk Maya 2018.5 and Autodesk Maya 2017.5


Exclusive script
- da_intPlay: this script add the interactive play button directly to Time Slider
- da_curveToPoly: this script make possible the conversion of curves in polygons
- da_interactiveBooleans: this script make the Polygonal Boolean process more interactive
- da_BooleanFullIntersect: this script make a full intersect, so this execute a mesh subtraction but maintain subtracted part as separate object
- da_PlaneCutter: this script cut a mesh by using a flat mesh, this can be useful for simulate surface cracks
- da_AutoBevel: this script analyse the angle between faces and try to add a Bevel node only on needed edges
- da_ClothAsDeformer: this script set up the current mesh to be deformed by nCloth solver, this can be useful for simulate character selfcollision skin or muscle dynamics
- da_nParticleConverter: this script add the ability to convert particle to a specific type after their creation
- da_perspToggle: this script convert the current persp view to the closest ortho, and vice versa
- da_shell: this script emulates Shell deformer of Autodesk 3D Studio Max, by adding a thickness to flat polygons
- da_ConvertToMetaballs: this script convert particles to polygonal Metaballs
- da_MashVoxelizer: this script use MASH to voxelize an arbitrary mesh inside of another mesh
- da_RivetMash: this script constraint the pivot of a polygon to a component of another polygon
- da_CurveDistributionMash: this script scatter and constrain a polygonal object along a curve
- da_EdgeToLoopToCurve: this script convert edge selection to loop and then make a batch conversion to curves, this is useful for converting polygonal hair to curve hair
- da_SurfaceScatterMash: this script scatter and constrain a polygonal object on a mesh
- da_CurveLength: this script returns the length of a curve in Maya unit
- da_MouseTrack: this script tracks the mouse movement and create an animation
- da_FacesFollicles: this script creates a follicle in the centre of selected faces
- da_Compass: this script converts Euler angle into a XYZ vector, for drive wind direction in Nucleus and Air Filed
- da_CombineCurves: this script combines curves in a single transform
- da_SepareCurves: this script separate combined curves
- da_MapFacesUV: this script maps any single faces of a mesh as separate planar UV shell
- da_KeyKeyedOnly: this script creates animation keys only on already animated channels
- Control Constraint: this set of scripts constraint a controller to a single or multiple controlled object(s)


Version 10 highlight
- Add support to Maya 2019
- May9 Next Hotkey Sets are added over standard ones without overwrite the user ones
- Incorporate MMtoKey into May9 Next Plug-in, so is possible use an indipendent MMtoKey aside
- Imporved usability of objects and components contextual MMs
- Complete the support of Modeling Toolkit
- Removed support to third party plug-ins
- Global polish and optimization


Useful links
fb.com/May9Prefs
youtube.com/c/May9


Licenses
May9 Next is licensed under MIT License (https://opensource.org/licenses/MIT)
Copyright (c) Davide Alidosi (https://www.highend3d.com/maya/script/may9-pro-a-new-user-experience-for-maya)

MMtoKey is under custom license: you can free modify source code of script, include to your preferences pack and redistribute, but you're not allowed to sell this script
Copyright (c) Andrey Menshikov (https://www.highend3d.com/maya/script/free-mmtokey-for-maya)