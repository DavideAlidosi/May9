import __main__
import MMtoKey


def initializePlugin(*args):
    __main__.MMtoKey = MMtoKey


def uninitializePlugin(*args):
    try:
        __main__.__delattr__("MMtoKey")
    except AttributeError:
        pass