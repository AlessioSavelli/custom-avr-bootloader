import os
import sys

def resource_path(relative_path: str) -> str:
    """
    Return the absolute path of a resource (file or folder)
    so it works with both the Python interpreter and a Nuitka-built executable.

    :param relative_path: relative path to the script/project folder
    :return: absolute path
    """
    if getattr(sys, "frozen", False):  
        # Executable case (Nuitka, PyInstaller, etc.)
        base_path = os.path.dirname(sys.executable)
    else:
        # Interpreted case
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)