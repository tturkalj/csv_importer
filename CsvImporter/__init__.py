import os
__version__ = 0.1


def get_root_folder():
    return os.path.dirname(os.path.abspath(__file__))
