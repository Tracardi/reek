from collections import defaultdict
from typing import List

from iterator import find_reeks
from utils.converter import file_path_to_module
from utils.yaml_reader import read_yaml

from rich.progress import Progress
from rich.console import Console

def _get_allowed(namespace_config: dict):
    return [c for c in namespace_config.get('allowed', [])]


def is_allowed(namespace: str, allowed: List[str]) -> bool:
    for allowed_namespace in allowed:
        if namespace.startswith(allowed_namespace):
            return True
    return False

def get_not_allowed(file: str, namespace, imports) -> List[str]:
    allowed = _get_allowed(namespace_config)
    not_allowed = []
    for _import in imports:
        # if file.startswith("tracardi/service/storage/mysql/mapping"):
        #     print("xxx", file)
        if _import.startswith(namespace):
            module_name = file_path_to_module(file)
            if not is_allowed(module_name, allowed):
                not_allowed.append(file)
    return not_allowed


def print_bullet_list(items, bullet="•"):
    """
    Prints a list of items with bullet points.

    Args:
        items (list): A list of items to print.
        bullet (str): The character to use as the bullet point. Default is a bullet (•).
    """
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
            for file, imports in find_reeks(folder):
                constrains = config['constrains']
                for namespace, namespace_config in constrains.items():
                    not_allowed = get_not_allowed(file, namespace, imports)
                    if not_allowed:
                        report[namespace].extend(not_allowed)

            folder_progress.update(task, advance=1)

console.print("Report", style="bold")
for namespace, validations in report.items():
    if validations:
        validations = list(set(validations))
        console.rule(f"Constrain failed for namespace \"{namespace}\" ({len(validations)})", style="bold red")
        console.print(f"List of files that validate the constraints", style="red")
        console.rule(style="red")
        print_bullet_list(sorted(validations))
