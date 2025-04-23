from flask import request, url_for
from pydantic import TypeAdapter
from typing import Any

from app.extensions import storage
from app.preprocessing import bp
from app.controllers import process_data


@bp.route("/preprocess/<dataset_id>", methods=["POST"])
def preprocess_dataset(dataset_id: str) -> dict[str, Any]:
    form_data = request.form.to_dict()
    make_copy = TypeAdapter(bool).validate_python(form_data.pop('make_copy'))

    data = storage.get_dataset(dataset_id)
    data = process_data(data, form_data)
    dataset_id = storage.save_dataset(data, None if make_copy else dataset_id)

    return {
        "message": "Dataset preprocessed successfully",
        "dataset_id": dataset_id,
        "next_step": url_for("get_recommendations", dataset_id=dataset_id),
        "metadata": {
            "num_rows": len(data),
            "num_columns": len(data.columns),
            "columns": data.dtypes.astype(str).to_dict()
        }
    }
