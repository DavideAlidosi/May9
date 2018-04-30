import __main__
import mass_attr


def initializePlugin(*args):
    __main__.mass_attr = mass_attr


def uninitializePlugin(*args):
    try:
        __main__.__delattr__("mass_attr")
    except AttributeError:
        pass