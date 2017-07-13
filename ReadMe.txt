May9 Pro 2.0.0 - A new user experience for Autodesk Maya 2017 and 2018

Release Note:
- Tested and develop on Maya 2018 and Maya 2017 Update 4 plus MtoA 2.0
- May9 Workspaces do not autosave, so needed manually save the workspace changes

A very special tanks to Andrey Menshikov for the hard work on amazing MMtoKey


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
	- Paint Skin tool
	- Paint Attribute
	- Legacy Artisan Sulpt tool
	- Create Particle tool
	- Paint FX tool
	- Grease Pencil tool
	- Multi Cut tool
	- Quad Draw tool
	- Poly Crease tool
	- Scultp tools
	- XGen Groom Paint tools
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

CTRL + ALT + R = Start IPR or Arnold Render View
CTRL + ALT + 2 = Edit and Graph Shader Based on Selection
CTRL + ALT + 8 = Paint Effects Panel
CTRL + ALT + X = Reverse to save

CTRL + SHIFT + ALT + C = Copy selection to clipboard
CTRL + SHIFT + ALT + V = Paste selection to clipboard
CTRL + SHIFT + ALT + S = Save selection in to a Set
CTRL + SHIFT + ALT + D = Delete Static Channels
CTRL + SHIFT + ALT + M = Toggle Shelf
CTRL + SHIFT + ALT + R = Toggle Resolution Gate
CTRL + SHIFT + ALT + Z = MMtoKey Manager

CTRL + ` = Show the last operation in AE
CTRL + F = Ignore the child and frame only the selected object
CTRL + P = Parent and position
CTRL + J = Context Connector
CTRL + K = Massive Attribute Editor
CTRL + L = List of Input Operation is mapped

ALT + 1 = Set Layout Single Perspective/Four View
ALT + 2 = Set Layout Node Editor
ALT + 3 = Set Layout UV Texture Editor
ALT + 4 = Set Layout Graph Editor
ALT + 5 = Set Layout Shape Editor
ALT + 6 = Set Layout Pose Editor
ALT + 7 = Set Layout Component Editor
ALT + 8 = Set Layout Relationship Editor
ALT + 9 = Set Layout Dynamic Relationship Editor
ALT + 0 = Set Layout Reference Editor

ALT + C = Open Channel Box or toggle it if docked
ALT + A = Open Attribute Editor or toggle it if docked
ALT + M = Open Modeling Toolkit or toggle it if docked
ALT + U = Open UV Toolkit or toggle it if docked (CMD + U on OS X)
ALT + O = Open Outliner or toggle it if docked
ALT + T = Open Tools Preference Settings or toggle it if docked
ALT + \ = Reset Workspace

ALT + L = Color Picker
ALT + G = Toggle grid
ALT + K = Toggle Color Management
ALT + Enter = Toggle perspective to orthographic camera

SHIFT + UP = Side View
SHIFT + RIGHT = Front View
SHIFT + DOWN = Top View
SHIFT + LEFT = Persp View
SHIFT + T = Assing shader if an object is selected or open create node window if not

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
ALT + P = Color Picker
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
- Panel tool bar is hidden
- Status line is fully expanded
- Enable Highlight connection on selected (Only Maya 2018)

For more information:

fb.com/May9Prefs
youtube.com/c/May9