from rich.console import Console

_console = None

_network_console = None


def get_console() -> Console | None:
    return _console


def set_console(file):
    global _console
    _console = Console(file=file)


def get_network_console() -> Console | None:
    return _network_console


def set_network_console(file):
    global _network_console
    _network_console = Console(file=file)
