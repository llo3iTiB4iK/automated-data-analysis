import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    MAX_FILE_SIZE_MB = 100                                  # Maximum file size that can be sent to app endpoints in MB
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE_MB * 1024 * 1024     # Maximum file size converted to bytes
    DELETE_AGE_HOURS = 24                                   # Maximum age of dataset file in hours
    STORAGE_CLEANUP_INTERVAL_HOURS = 12                     # Dataset storage cleanup frequency in hours
    DATASET_STORAGE = os.path.join(basedir, "datasets")     # Path to dataset storage
    ENV = os.getenv("ENV", "dev")                           # Environment (suggested "dev" and "prod")
    DEBUG = ENV != "prod"                                   # Debug mode for non-production environments
