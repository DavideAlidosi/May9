import maya.cmds as cmds


last_tool = None
current_tool = None


def run():
    """no-click enter point"""
    if last_tool:
        cmds.setToolTo(last_tool)


def tool():
    """trigger for changed tool"""
    global current_tool, last_tool
    last_tool = current_tool
    current_tool = cmds.currentCtx()


cmds.scriptJob(e=["ToolChanged", tool])
