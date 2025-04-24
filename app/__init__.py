from flask import Flask
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from app.data_exchange import bp as data_exchange_bp
from app.errors import BaseError
from app.errors.handlers import handle_custom_error, handle_validation_error, handle_http_exception
from app.extensions import storage
from app.main import bp as main_bp
from app.preprocessing import bp as preprocessing_bp
from app.reporting import bp as reporting_bp
from config import Config


def create_app(config_class: object = Config) -> Flask:
    app: Flask = Flask(__name__)
    app.config.from_object(config_class)

    storage.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(data_exchange_bp)
    app.register_blueprint(preprocessing_bp)
    app.register_blueprint(reporting_bp)

    app.register_error_handler(BaseError, handle_custom_error)
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(HTTPException, handle_http_exception)


    if app.config["ENV"] == "dev":
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
        except ImportError:
            raise RuntimeError("Environment is set to 'dev', but 'apscheduler' is missing. "
                               "This may happen if production dependencies were installed instead of development ones.")

        scheduler = BackgroundScheduler()
        scheduler.add_job(storage.cleanup, "interval", hours=app.config["STORAGE_CLEANUP_INTERVAL_HOURS"])
        scheduler.start()

    return app
