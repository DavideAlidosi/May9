import __main__
import contextConnector


def initializePlugin(*args):
    __main__.contextConnector = contextConnector


def uninitializePlugin(*args):
    try:
        __main__.__delattr__("contextConnector")
    except AttributeError:
        pass