_running = True


def set_running(is_run: bool):
    global _running
    _running = is_run


def get_running():
    return _running
