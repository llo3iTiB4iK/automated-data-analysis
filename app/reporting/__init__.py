from flask import Blueprint

bp = Blueprint('reporting', __name__)

from app.reporting import routes  # noqa: E402

__all__ = ['bp']
