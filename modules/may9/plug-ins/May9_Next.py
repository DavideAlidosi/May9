import __main__
import May9_Next


def initializePlugin(*args):
    __main__.May9_Next = May9_Next


def uninitializePlugin(*args):
    try:
        __main__.__delattr__("May9_Next")
    except AttributeError:
        pass