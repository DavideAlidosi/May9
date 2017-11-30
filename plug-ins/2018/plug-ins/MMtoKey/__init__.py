import sys
import os
import Engine


def ui():
    """open marking menu editor"""
    import Editor
    Editor.MainWindow(engine)


sys.path.append(os.path.dirname(__file__))
engine = Engine.Engine()
pressSelected = engine.pressSelected    # sh, alt, ctl
releaseSelected = engine.releaseSelected
pressCustom = engine.pressCustom        # sh, alt, ctl, menu_name, menu_type
releaseCustom = engine.releaseCustom    # command, language, command_always
pressPreset = engine.pressPreset        # sh, alt, ctl
releasePreset = engine.releasePreset
