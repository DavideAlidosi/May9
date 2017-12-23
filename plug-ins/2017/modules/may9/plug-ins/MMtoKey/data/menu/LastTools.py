import maya.cmds as cmds


POSITIONS = "N", "NE", "E", "SE", "S", "SW", "W", "NW"


def run():
    """press enter point"""
    for item, pos in zip(last_tools_list, POSITIONS):
        cmds.menuItem(stp="python", c="cmds.setToolTo('%s')" % item, rp=pos, l=item)


def tool():
    """trigger for changed tool"""
    current_tool = cmds.currentCtx()
    if current_tool not in last_tools_set:
        last_tools_set.add(current_tool)
        last_tools_list.append(current_tool)
    while len(last_tools_list) > 8:
        last_tools_set.discard(last_tools_list.pop(0))


last_tools_set = set()
last_tools_list = []
cmds.scriptJob(e=["ToolChanged", tool])
