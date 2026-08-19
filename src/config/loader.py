from pathlib import Path
import yaml


def load_config():
    project_root = Path(__file__).resolve().parents[2]
    config_path = project_root / "configs" / "base.yaml"

    with open(config_path, "r") as file:
        return yaml.safe_load(file)