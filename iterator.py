import os
import ast
from pathlib import Path


def find_python_files(directory):
    return [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith('.py')]


def get_package_path(file_path, root_directory):
    """Attempt to determine the package path by relative directory structure"""
    file_directory = os.path.dirname(file_path)
    package_path = file_directory[len(root_directory):].replace(os.sep, '.')
    return package_path.strip('.')


def get_imports(file_path, root_directory):
    """Parse a Python file and resolve imports to absolute where possible"""
    with open(file_path, 'r', encoding='utf-8') as file:
        relative_path = file_path.replace(root_directory, "")

        if relative_path.startswith('/venv'):
            return []

        root = ast.parse(file.read(), filename=file_path)

    imports = []
    package_base = get_package_path(file_path, root_directory)

    for node in ast.walk(root):
        if isinstance(node, ast.Import):
            imports.extend([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                if node.level == 0:
                    imports.append(node.module)
                else:
                    # Construct absolute path for relative imports
                    relative_levels = package_base.split('.')[:-node.level]
                    imports.append('.'.join(relative_levels + [node.module]))
            else:
                # Handling from . import something
                relative_levels = package_base.split('.')[:len(package_base.split('.')) - node.level]
                imports.append('.'.join(relative_levels))

    return imports

def find_reeks(root_directory: str):
    python_files = find_python_files(root_directory)

    all_imports = {}
    for file in python_files:
        imports = get_imports(file, root_directory)
        if imports:
            all_imports[file] = imports

    for file, imports in all_imports.items():
        yield file.replace(root_directory, ""), imports


