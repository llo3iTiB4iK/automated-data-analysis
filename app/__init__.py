from flask import Flask
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from config import config_by_env, ENV
from app.errors import BaseError
from app.errors.handlers import handle_custom_error, handle_validation_error, handle_http_exception
from app.main import bp as main_bp
from app.data_exchange import bp as data_exchange_bp
from app.preprocessing import bp as preprocessing_bp
from app.reporting import bp as reporting_bp
from app.extensions import storage


def create_app() -> Flask:
    app: Flask = Flask(__name__)
    app.config.from_object(config_by_env[ENV])

    storage.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(data_exchange_bp)
    app.register_blueprint(preprocessing_bp)
    app.register_blueprint(reporting_bp)

    app.register_error_handler(BaseError, handle_custom_error)
    app.register_error_handler(ValidationError, handle_validation_error)
    #app.register_error_handler(OSError, eh.failed_to_store)
    app.register_error_handler(HTTPException, handle_http_exception)


    if ENV == "dev":
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
        except ImportError:
            raise RuntimeError("Environment is set to 'dev', but 'apscheduler' is missing. "
                               "This may happen if production dependencies were installed instead of development ones.")

        scheduler = BackgroundScheduler()
        scheduler.add_job(storage.cleanup, "interval", hours=app.config["STORAGE_CLEANUP_INTERVAL_HOURS"])
        scheduler.start()

    return app  # todo: optimize imports in app directory, type hints in controllers, add jsonify everywhere, separate config (env) logic to main.py
