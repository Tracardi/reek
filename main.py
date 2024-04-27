from collections import defaultdict
from typing import List

from iterator import find_reeks
from utils.converter import file_path_to_module
from utils.yaml_reader import read_yaml


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


# Example usage:
file_path = 'config.yaml'
config = read_yaml(file_path)
print(config)

report = defaultdict(list)
if 'folders' in config:
    for folder in config['folders']:
        # Iterate folders
        for file, imports in find_reeks(folder):
            constrains = config['constrains']
            for namespace, namespace_config in constrains.items():
                not_allowed = get_not_allowed(file, namespace, imports)
                if not_allowed:
                    report[namespace].extend(not_allowed)

for namespace, validations in report.items():
    if validations:
        print(f"Set constrain for {namespace} validated in the following files:")
        for file in validations:
            print(f" - {file}")
