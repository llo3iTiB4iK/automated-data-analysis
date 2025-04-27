from flask import request, url_for, jsonify, Response
from pydantic import TypeAdapter

from app.controllers import process_data
from app.extensions import storage
from app.preprocessing import bp


@bp.route("/preprocess/<dataset_id>", methods=["POST"])
def preprocess_dataset(dataset_id: str) -> Response:
    form_data = request.form.to_dict()
    make_copy = TypeAdapter(bool).validate_python(form_data.get('make_copy', False))

    access_key = request.headers.get("X-Dataset-Token", "")
    data = storage.get_dataset(dataset_id)
    data = process_data(data, form_data)
    new_dataset_id, new_access_key = storage.save_dataset(data, None if make_copy else dataset_id, access_key)

    response = {
        "message": "Dataset preprocessed successfully",
        "dataset_id": dataset_id,
        "next_step": url_for("reporting.get_recommendations", dataset_id=dataset_id),
        "metadata": {
            "num_rows": len(data),
            "num_columns": len(data.columns),
            "columns": data.dtypes.astype(str).to_dict()
        }
    }

    if make_copy:
        response["new_dataset_id"] = new_dataset_id
        response["new_dataset_access_key"] = new_access_key

    return jsonify(response)
