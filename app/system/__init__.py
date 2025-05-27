from flask import Blueprint

bp = Blueprint('system', __name__)

from app.system import routes  # noqa: E402

__all__ = ['bp']
