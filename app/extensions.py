import os
import time
import uuid
from datetime import datetime, timezone

import pandas as pd
from flask import Flask


class Storage:
    # todo: add access_key
    def __init__(self, app: Flask = None) -> None:
        self.storage_location = None
        self.dataset_max_age = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        self.storage_location = app.config["DATASET_STORAGE"]
        self.dataset_max_age = app.config["DELETE_AGE_HOURS"]

    def cleanup(self) -> None:
        check_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        deleted_files = 0
        print(f"[{check_time}] Starting storage cleanup...")

        if not os.path.isdir(self.storage_location):
            os.mkdir(self.storage_location)
        for file_path in os.listdir(self.storage_location):
            full_path = os.path.join(self.storage_location, file_path)
            if os.path.isfile(full_path) and (time.time() - os.path.getctime(full_path) > self.dataset_max_age * 3600):
                os.remove(full_path)
                deleted_files += 1
        print(f"✅ Cleanup complete! {deleted_files} file(s) deleted.\n")

    def get_dataset(self, dataset_id: str) -> pd.DataFrame:
        full_path = os.path.join(self.storage_location, dataset_id)
        if not os.path.exists(full_path):
            raise ValueError(f"Dataset with given ID '{dataset_id}' not found in storage.")
        return pd.read_pickle(full_path)

    def save_dataset(self, data: pd.DataFrame, dataset_id: str = "") -> str:
        if not dataset_id:
            dataset_id: str = str(uuid.uuid4())
        if not os.path.isdir(self.storage_location):
            os.mkdir(self.storage_location)
        full_path = os.path.join(self.storage_location, dataset_id)
        data.to_pickle(full_path)
        return dataset_id


storage = Storage()
