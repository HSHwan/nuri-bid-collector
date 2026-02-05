import os
import yaml
import logging
from typing import Dict

logger = logging.getLogger("ConfigLoader")

def _load_yaml(path: str) -> Dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_app_config(config_dir: str) -> Dict:
    logger.info(f"Loading configuration from: {config_dir}")
    try:
        return {
            "search": _load_yaml(os.path.join(config_dir, "search.yaml")),
            "system": _load_yaml(os.path.join(config_dir, "system.yaml"))
        }
    except Exception as e:
        logger.error(f"Failed to load config files: {e}")
        raise e