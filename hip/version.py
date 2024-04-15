def get_version():
    with open("../VERSION", "r") as version_file:
        __version__ = version_file.read().strip()
    return __version__