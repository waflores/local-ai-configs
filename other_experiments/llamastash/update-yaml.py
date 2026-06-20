import yaml
from typing import Any, Mapping


def load_yaml(file_path: str) -> Mapping[str, Any]:
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def save_yaml(data: Mapping[str, Any], file_path: str) -> None:
    with open(file_path, "w") as file:
        yaml.safe_dump(data, file)


env_vars = [
    "GGML_CUDA_ENABLE_UNIFIED_MEMORY=1",
    "LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu",
]


def main():
    # Example usage
    yaml_file_path = "config.yaml"

    # Load the YAML file
    config_data = load_yaml(yaml_file_path)

    # models: key: env

    # Update a specific key-value pair
    # update_yaml(yaml_file_path, ['database', 'host'], 'localhost')
    models = config_data["models"]
    for model_name, model_properties in models.items():
        model_properties.setdefault("env", []).extend(env_vars)
        print(f"{model_name}: {model_properties.get('env')}")

    save_yaml(config_data, "config.yaml")
    # Print the updated config (for debugging)
    # pprint.pprint(config_data)


if __name__ == "__main__":
    main()
