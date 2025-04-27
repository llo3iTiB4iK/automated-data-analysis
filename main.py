import os
import threading
import time

from app import create_app
from app.extensions import storage

app = create_app()


def interval_cleanup():
    while True:
        with app.app_context():
            storage.cleanup()
        time.sleep(app.config["STORAGE_CLEANUP_INTERVAL_HOURS"] * 3600)


if __name__ == "__main__":
    if app.config["ENV"] == "dev":
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            threading.Thread(target=interval_cleanup, daemon=True).start()

    app.run()
