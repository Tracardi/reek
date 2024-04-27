import os


def file_path_to_module(path):
    """
    Convert a file system path to a Python module path.

    Args:
    path (str): The full path to the Python file.

    Returns:
    str: The module path in dot notation.
    """
    # Strip the extension (.py) from the file
    base = os.path.splitext(path)[0]

    # Replace OS-specific path separators with dots
    module_path = base.replace(os.path.sep, '.')

    if module_path[0] == '.':
        return module_path[1:]

    return module_path
