import os
from dataclasses import dataclass


@dataclass
class UronConfig:
    default_cache_folder: str = os.environ.get(
        "DEFAULT_URON_CACHE_FOLDER", ".uron_cache"
    )
    disable: bool = os.environ.get("URON_DISABLE", "false") == "true"


@dataclass
class PackageConfig:
    name: str
    version: str
