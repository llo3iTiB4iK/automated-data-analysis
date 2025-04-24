import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    MAX_FILE_SIZE_MB = 100
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE_MB * 1024 * 1024
    DELETE_AGE_HOURS = 24
    STORAGE_CLEANUP_INTERVAL_HOURS = 12
    DATASET_STORAGE = os.path.join(basedir, "datasets")
    ENV = os.getenv("ENV", "dev")
    DEBUG = ENV == "dev"
