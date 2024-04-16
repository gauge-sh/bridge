from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel
from yaml import CDumper as Dumper
from yaml import CLoader as Loader
from yaml import dump, load

from bridge.console import log_warning


class BridgeConfig(BaseModel):
    enable_postgres: bool = True
    enable_worker: bool = True

    def to_yaml(self) -> str:
        return dump(self.model_dump(), Dumper=Dumper)

    @classmethod
    def from_yaml(cls, data: str) -> "BridgeConfig":
        return cls.model_validate(load(data, Loader=Loader))


CONFIG_PATH = Path("bridge.yaml")


def ensure_config_file():
    if not CONFIG_PATH.exists():
        with CONFIG_PATH.open(mode="w") as f:
            f.write(BridgeConfig().to_yaml())


__CONFIG: Optional[BridgeConfig] = None


def get_config() -> BridgeConfig:
    # NOTE: not thread-safe
    global __CONFIG
    if __CONFIG is not None:
        return __CONFIG

    ensure_config_file()
    try:
        with CONFIG_PATH.open(mode="r") as f:
            __CONFIG = BridgeConfig.from_yaml(f.read())
    except yaml.YAMLError:
        log_warning("Failed to read configuration file. Using default configuration.")
        __CONFIG = BridgeConfig()

    return __CONFIG
