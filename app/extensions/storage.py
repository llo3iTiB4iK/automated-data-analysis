import os
import time
import uuid
from datetime import datetime, timezone

import pandas as pd
from flask import Flask, current_app, url_for, request
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError


class Storage:

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['storage'] = self

    @property
    def storage_location(self) -> str:
        return current_app.config["DATASET_STORAGE"]

    @property
    def dataset_max_age(self) -> int:
        return current_app.config["DELETE_AGE_HOURS"]

    @property
    def access_key_header(self) -> str:
        return current_app.config["ACCESS_KEY_HEADER"]

    def cleanup(self) -> None:
        check_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        deleted_files = 0
        print(f"[{check_time}] Starting storage cleanup...")

        os.makedirs(self.storage_location, exist_ok=True)

        for file_path in os.listdir(self.storage_location):
            full_path = os.path.join(self.storage_location, file_path)
            if os.path.isfile(full_path) and (time.time() - os.path.getctime(full_path) > self.dataset_max_age * 3600):
                os.remove(full_path)
                deleted_files += 1

        print(f"✅ Cleanup complete! {deleted_files} file(s) deleted.\n")

    def get_dataset(self, dataset_id: str) -> pd.DataFrame:
        access_key = request.headers.get(self.access_key_header)
        if not access_key:
            raise BadRequest("Missing access key in headers.")

        expected_filename = f"{dataset_id}__{access_key}"
        full_path = os.path.join(self.storage_location, expected_filename)

        if not os.path.exists(full_path):
            raise NotFound("Dataset not found or invalid access key.")

        return pd.read_pickle(full_path)

    def save_dataset(self, data: pd.DataFrame, dataset_id: str = "") -> tuple[str, str]:
        dataset_id = dataset_id or str(uuid.uuid4())
        access_key = request.headers.get(self.access_key_header, str(uuid.uuid4()))

        os.makedirs(self.storage_location, exist_ok=True)

        filename = f"{dataset_id}__{access_key}"
        full_path = os.path.join(self.storage_location, filename)

        try:
            data.to_pickle(full_path)
        except OSError:
            raise InternalServerError(f"Failed to save your dataset. Try again later or consider using "
                                      f"'{url_for('system.analyze_data')}' endpoint for all-in-one request.")

        return dataset_id, access_key
