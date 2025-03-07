import os
import time
import uuid
import pandas as pd
from datetime import datetime

DATASET_STORAGE: str = "datasets"
DELETE_AGE_HOURS: int = 24


def delete_old_files() -> None:
    check_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    deleted_files: int = 0
    print(f"[{check_time}] Starting storage cleanup...")

    if not os.path.isdir(DATASET_STORAGE):
        os.mkdir(DATASET_STORAGE)
    for file_path in os.listdir(DATASET_STORAGE):
        full_path: str = os.path.join(DATASET_STORAGE, file_path)
        if os.path.isfile(full_path) and (time.time() - os.path.getctime(full_path) > DELETE_AGE_HOURS * 3600):
            os.remove(full_path)
            deleted_files += 1
    print(f"✅ Cleanup complete! {deleted_files} file(s) deleted.\n")


def get_from_storage(dataset_id: str) -> pd.DataFrame:
    full_path: str = os.path.join(DATASET_STORAGE, dataset_id)
    if not os.path.exists(full_path):
        raise ValueError(f"Dataset with given ID '{dataset_id}' not found in storage.")
    return pd.read_pickle(full_path)


def save_to_storage(data: pd.DataFrame, dataset_id: str = None) -> str:
    if not dataset_id:
        dataset_id: str = str(uuid.uuid4())
    if not os.path.isdir(DATASET_STORAGE):
        os.mkdir(DATASET_STORAGE)
    full_path: str = os.path.join(DATASET_STORAGE, dataset_id)
    data.to_pickle(full_path)
    return dataset_id
