from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes  # noqa: E402

__all__ = ['bp']
