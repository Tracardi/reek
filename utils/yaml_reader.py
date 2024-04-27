import yaml


def read_yaml(file_path):
    """Read and return the content of a YAML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            return yaml.load(file, Loader=yaml.FullLoader)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
