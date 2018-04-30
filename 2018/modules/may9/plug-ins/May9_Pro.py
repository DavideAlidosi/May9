import __main__
import May9_Pro


def initializePlugin(*args):
    __main__.May9_Pro = May9_Pro


def uninitializePlugin(*args):
    try:
        __main__.__delattr__("May9_Pro")
    except AttributeError:
        pass