import MMtoKey


mmtokey = MMtoKey.MMtoKey()


def press_selected(menu, **kwargs):
    try:
        mmtokey.press_selected(menu, **kwargs)
    except RuntimeError:
        pass


def release_selected(*args):
    try:
        mmtokey.release_selected(*args)
    except RuntimeError:
        pass


def press_preset(**kwargs):
    try:
        mmtokey.press_preset(**kwargs)
    except RuntimeError:
        pass


def release_preset():
    try:
        mmtokey.release_preset()
    except RuntimeError:
        pass


def ui():
    import Tools
    Tools.MainWindow(mmtokey)
