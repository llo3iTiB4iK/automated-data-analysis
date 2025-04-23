from flask import Blueprint

bp = Blueprint('data_exchange', __name__)

from app.data_exchange import routes  # noqa: E402
