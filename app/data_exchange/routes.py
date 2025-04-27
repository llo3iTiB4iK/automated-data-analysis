from io import BytesIO

from flask import request, url_for, Response, send_file, jsonify

from app.controllers import load_data
from app.data_exchange import bp
from app.errors import ParameterMissing
from app.extensions import storage


@bp.route("/upload", methods=["POST"])
def upload_file() -> Response:
    file = request.files['file']
    if not file:
        raise ParameterMissing("file")

    params = request.form.to_dict()
    data = load_data(file, params)
    dataset_id, access_key = storage.save_dataset(data)

    response = {
        "message": "Dataset uploaded successfully",
        "dataset_id": dataset_id,
        "access_key": access_key,
        "next_step": url_for("preprocessing.preprocess_dataset", dataset_id=dataset_id),
        "metadata": {
            "num_rows": len(data),
            "num_columns": len(data.columns),
            "columns": data.dtypes.astype(str).to_dict()
        }
    }

    return jsonify(response)


@bp.route("/dataset_info/<dataset_id>")
def get_info(dataset_id: str) -> Response:
    data = storage.get_dataset(dataset_id)

    response = {
        "message": "Dataset found successfully",
        "dataset_id": dataset_id,
        "next_step": url_for("preprocessing.preprocess_dataset", dataset_id=dataset_id),
        "metadata": {
            "num_rows": len(data),
            "num_columns": len(data.columns),
            "columns": data.dtypes.astype(str).to_dict()
        }
    }

    return jsonify(response)


@bp.route("/download/<dataset_id>")
def download_dataset(dataset_id: str) -> Response:
    data = storage.get_dataset(dataset_id)
    dataset_buffer = BytesIO()
    data.to_csv(dataset_buffer, index=False)
    dataset_buffer.seek(0)
    return send_file(dataset_buffer, mimetype='text/csv', as_attachment=False, download_name=f'{dataset_id}.csv')
