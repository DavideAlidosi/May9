May9 Pro 1.2.8 - A new user experience for Autodesk Maya 2017

Release Note:
- Tested and develop on Maya 2017 Update 3 and MtoA 2.0.0
- May9 Workspaces do non autosave, this fix some minor bug on Maya 2017 UI but need manually save the workspace changes


Installation Instruction:

Windows
1) Close Maya
2) Go to folder: \Users\<username>\Documents\maya\ 
3) Rename folder 2017 in to 2017_Bak
4) Copy folder 2017 of this archive in: \Users\<username>\Documents\maya\

OS X
1) Close Maya
2) Go to folder: /Users/<username>/Library/Preferences/Autodesk/maya/
3) Rename folder 2017 in to 2017_Bak
4) Copy folder 2017 of this archive in: /Users/<username>/Library/Preferences/Autodesk/maya/

Linux
1) Close Maya
2) Go to folder: ~<username>/maya/
3) Rename folder 2017 in to 2017_Bak
4) Copy folder 2017 of this archive in: ~<username>/maya/


Quick start:

Press and release Z = Enable the contextual Hotkey based on selection, combination of selection or panels (For access to undo command is possible to use CTRL + Z)
Press and hold Z + Left mouse button = Enable the contextual Marking Menus based on selection, combination of selection or panels
Press and hold Z + Middle mouse button = Enable the Universal Marking MenuEnable or one of this tool contextual Marking Menu:
	- 3D Paint tool
	- Shooth Skin tool
	- Paint Attribute
	- Legacy Artisan Sulpt tool
	- Create Particle tool
	- Paint FX tool
	- Grase Pencil tool
	- Multi Cut tool
	- Quad Draw tool
	- Poly Crease tool
	- Scultp tools
	- XGen Groom Paint tools
	- Crease tool
	- Create Particle tool
	- UV Brushes


May9 Pro new hotkeys:

CTRL + Enter = Delete History and Freeze Transform
SHIFT + ALT + F = Freeze Transformation
SHIFT + ALT + R = Reset Transformations
SHIFT + ALT + C = Center Pivot
SHIFT + ALT + Z = Zero Transformations (move objects to world center)
SHIFT + ALT + M = Match Transform
SHIFT + ALT + W = Toggle Wireframe on Shaded
SHIFT + ALT + Space = Playback toggle

CTRL + SHIFT + ALT + C = Copy selection to clipboard
CTRL + SHIFT + ALT + V = Paste selection to clipboard
CTRL + SHIFT + ALT + S = Save selection in to a Set
CTRL + SHIFT + ALT + R = Start IPR or Arnold Render View

CTRL + SHIFT + ALT + D = Delete Static Channels
CTRL + SHIFT + ALT + M = Toggle Shelf
CTRL + SHIFT + ALT + Z = MMtoKey Manager
CTRL + SHIFT + ALT + Q = MMtoKey Resetter
CTRL + ALT + X = Reverse to save
CTRL + ` = Show the last operation in AE
CTRL + F = Ignore the child and frame only the selected object
CTRL + P = Parent and position
CTRL + J = Context Connector
CTRL + K = Massive Attribute Editor
CTRL + L = List of Input Operation is mapped
CTRL + ALT + 8 = Paint Effects Panel

ALT + 1 = Open Hypershade or toggle it if docked
ALT + 2 = Open Node Editor or toggle it if docked
ALT + 3 = Open UV Editor or toggle it if docked
ALT + 4 = Open Shape Editor or toggle it if docked
ALT + 5 = Open Pose Editor or toggle it if docked
ALT + 6 = Open Component Editor or toggle it if docked
ALT + 7 = Open Relationship Editor or toggle it if docked
ALT + 8 = Open Dynamic Relationship Editor or toggle it if docked
ALT + 9 = Open Reference Editor or toggle it if docked
ALT + 0 = Open Graph Editor or toggle it if docked

ALT + C = Open Channel Box or toggle it if docked
ALT + A = Open Attribute Editor or toggle it if docked
ALT + M = Open Modeling Toolkit or toggle it if docked
ALT + U = Open UV Toolkit or toggle it if docked (CMD + U on OS X)
ALT + O = Open Outliner or toggle it if docked
ALT + T = Open Tools Preference Settings or toggle it if docked

ALT + L = Color Picker
ALT + G = Toggle grid
ALT + K = Toggle Color Management
ALT + Enter = Toggle perspective to orthographic camera

SHIFT + UP = Side View
SHIFT + RIGHT = Front View
SHIFT + DOWN = Top View
SHIFT + LEFT = Persp View

A + LMB = SOuP Smart Connector
~ = Orient Manipulators Toggle
? = Find Maya Menu
K + Drag = Smooth playback mode
CMD + Space = Toggle Full Screen (Mac OS only)


Changed hotkeys:

CTRL + ALT + D = Toggle Displacement
CTRL + ALT + ~ = SmoothingDisplayShowBoth
CTRL + ALT + ` = SmoothingDisplayToggle
ALT + - = ToggleColorFeedback
ALT + I = Toggle Wireframe in Artisan
SHIFT + N = Full Hotbox Display


Main preferences change:

- Two side lighting is enable (as in Maya 2014)
- Animate Camera Transition is enable (as in Maya 2014)
- Interactive Creation is enable (as in Maya 2015)
- Anti-aliasing and the Floating Point Render are enable by default in VP 2.0
- Playback Speed is set to Play Every Frame, Max Real-time
- X-Ray Active Component is enable
- Hidden attribute in connections exposed
- Membrane Deformer exposed
- Legacy Subdivision Surface exposed
- Legacy Mirror Cut tool exposed
- Hotbox have no transparency
- Incremental save is enable and limited to 5 increments
- Brush optimization
- Paint Skin Tool now use custom colors
- Script Editor have enable the Command Completition
- Disable Mouse Wheel Zoom
- HDR and EXR file is set to Raw colorspace for prevent Arnold double expose
- Fix PaintFX Preset Blending bug
- Two Bone IK and Spring IK are preload
- PreSelect Highlight is on by default in Graph Editor
- Wireframe visibility on Sculpting Tool is on by default
- Bake Deformer Tool exposed


For more information:

fb.com/May9Prefs
youtube.com/c/May9
github.com/DavideAlidosi/May9


A special tanks to:

Andrey Menshikov for the hard work on our amazing MMtoKey
Pavel Korolyov for Context Connector
Jefri Haryono for Rain Curves From Edges
David Johnson for djRivet
Carlos Rico Adega for Offset Keyframes
Peter Shipkov for SOuP
Ingo Clements for Smooth Skin Cluster Weight and Weight Driver 
Webber Huang for Soft Cluster EX
Mariano Merchante for Instance Along Curve
Anders Langlands for alShaders
Morten Dalgaard Andersen for amCombineCurves
Mehdi Louala for Massive Attribute Editor
Basenji Games for Poly Separate