from flask import Flask
from flask_cors import CORS
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from app.data_exchange import bp as data_exchange_bp
from app.extensions import storage, spec
from app.handlers import handle_validation_error, handle_http_exception, handle_unexpected_error, handle_spec_422
from app.main import bp as main_bp
from app.preprocessing import bp as preprocessing_bp
from app.reporting import bp as reporting_bp
from config import Config


def create_app(config_class: object = Config) -> Flask:
    app: Flask = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app, resources={r"/*": {
        "origins": "*",
        "allow_headers": ["Content-Type", "X-Dataset-Token"],
        "methods": ["GET", "POST"]
    }})
    storage.init_app(app)
    spec.register(app)
    spec.before = handle_spec_422

    @app.cli.command("cleanup")
    def cleanup_command():
        storage.cleanup()

    app.register_blueprint(main_bp)
    app.register_blueprint(data_exchange_bp)
    app.register_blueprint(preprocessing_bp)
    app.register_blueprint(reporting_bp)

    app.register_error_handler(HTTPException, handle_http_exception)
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(Exception, handle_unexpected_error)

    return app


__all__ = ['create_app']
