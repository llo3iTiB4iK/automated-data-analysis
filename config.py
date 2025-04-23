import os
from typing import Literal

ENV: Literal["dev", "prod"] = "dev"

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    MAX_FILE_SIZE_MB = 100
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE_MB * 1024 * 1024
    DELETE_AGE_HOURS = 24
    STORAGE_CLEANUP_INTERVAL_HOURS = 12
    DATASET_STORAGE = os.path.join(basedir, "datasets")


class DevConfig(BaseConfig):
    DEBUG = True


class ProdConfig(BaseConfig):
    DEBUG = False


config_by_env = {
    "dev": DevConfig,
    "prod": ProdConfig,
}
