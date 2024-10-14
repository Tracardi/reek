from collections import defaultdict
from typing import List

from iterator import find_reeks
from utils.converter import file_path_to_module
from utils.yaml_reader import read_yaml

from rich.progress import Progress
from rich.console import Console


def _get_allowed(namespace_config: dict):
    return [c for c in namespace_config.get('allowed', [])]


def _get_disallowed(namespace_config: dict):
    return [c for c in namespace_config.get('disallowed', [])]


def is_in_list(namespace: str, items: List[str]) -> bool:
    for allowed_namespace in items:
        if namespace.startswith(allowed_namespace):
            return True
    return False

def _get_next_char(_import, namespace):
    try:
        return _import[len(namespace)] in [" ", "."]
    except IndexError:
        return True

def check_allowed(file: str, current_file_module_name: str, namespace, imports, allowed) -> List[str]:
    not_allowed = []
    for _import in imports:
        if _import.startswith(namespace) and _get_next_char(_import,namespace):
            if not is_in_list(current_file_module_name, items=allowed):
                not_allowed.append(file)
    return not_allowed


def check_disallowed(file: str, current_file_module_name: str, namespace, imports, disallowed) -> List[str]:
    not_allowed = []

    for _disallowed in disallowed:
        if not current_file_module_name.startswith(_disallowed):
            continue

        for _import in imports:
            if _import.startswith(namespace):
                not_allowed.append(file)

    return not_allowed


def print_bullet_list(items, root_directory, bullet="•"):
    """
    Prints a list of items with bullet points.

    Args:
        items (list): A list of items to print.
        bullet (str): The character to use as the bullet point. Default is a bullet (•).
    """
    print(root_directory)
    for item in items:
        console.print(f"{bullet} {item}")


# Example usage:
file_path = 'config.yaml'
config = read_yaml(file_path)
# print(config)

console = Console()
console.print("Python module constrain validator (REEK)", style="bold")
report = defaultdict(list)
if 'folders' in config:
    with Progress() as folder_progress:
        total_folders = len(config['folders'])
        task = folder_progress.add_task("[gray]Scanning folders...", total=total_folders)
        for folder in config['folders']:
            # Iterate folders
            for file, imports, root in find_reeks(folder):
                constrains = config['constrains']
                for namespace, namespace_config in constrains.items():

                    file_module_name = file_path_to_module(file)
                    name = namespace_config.get('name', None)
                    if 'allowed' in namespace_config:
                        allowed = _get_allowed(namespace_config)
                        not_allowed = check_allowed(file, file_module_name, namespace, imports, allowed)
                        if not_allowed:
                            report[(namespace, name, root)].extend(not_allowed)

                    if 'disallowed' in namespace_config:
                        disallowed = _get_disallowed(namespace_config)
                        not_allowed = check_disallowed(file, file_module_name, namespace, imports, disallowed)
                        if not_allowed:
                            report[(namespace, name, root)].extend(not_allowed)

            folder_progress.update(task, advance=1)

console.print("Report", style="bold")
total_errors = 0
failed_namespaces = []
for (namespace, name, root_directory), validations in report.items():
    if validations:
        validations = list(set(validations))
        no_of = len(validations)
        total_errors += no_of
        failed_namespaces.append(f"{namespace} ({no_of}) in {root_directory}")
        console.rule(f"FAILED CONSTRAIN", style="red")
        console.rule(f"Constrain failed for namespace \"{namespace}\" ({no_of})", style="red")
        console.print(name if name is not None else "Missing description", style="red")
        console.rule(f"List of files that break the constraints", style="red")
        print_bullet_list(sorted(validations), root_directory)

console.rule(f"Summary", style="white")
console.print(f"Total numer of errors {total_errors}", style="blue")
console.print(f"Failed namespaces {len(report)}", style="blue")
print_bullet_list(sorted(failed_namespaces), "")
console.rule(style="white")
