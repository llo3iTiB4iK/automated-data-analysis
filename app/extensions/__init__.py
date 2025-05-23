from flask_pydantic_spec import FlaskPydanticSpec

from .storage import Storage

__all__ = ["storage", "spec"]

storage = Storage()
spec = FlaskPydanticSpec('flask', title='Automated Data Analysis API')
