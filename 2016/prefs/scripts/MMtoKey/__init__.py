import MMtoKey


mmtokey = MMtoKey.MMtoKey()


def press_1(ctrl, alt,  shift, menu, *args, **kwargs):
    try:
        mmtokey.press_1(menu, ctl=ctrl, alt=alt, sh=shift)
    except RuntimeError:
        pass

def release_1(command, language, *args, **kwargs):
    try:
        mmtokey.release_1(command, language)
    except RuntimeError:
        pass


def press_0(ctrl, alt, shift, *args, **kwargs):
    try:
        mmtokey.press_0(ctl=ctrl, alt=alt, sh=shift)
    except RuntimeError:
        pass


def release_0(*args, **kwargs):
    try:
        mmtokey.release_0()
    except RuntimeError:
        pass


def ui():
    import Tools
    Tools.MainWindow(mmtokey)
