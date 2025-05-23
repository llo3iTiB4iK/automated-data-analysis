from io import BytesIO

from flask import request, url_for, send_file, jsonify
from flask_pydantic_spec import Response

from app.data_exchange import bp
from app.errors import ParameterMissing
from app.extensions import storage, spec
from app.controllers import DataFrameLoader, DataFrameAnalyzer
from app.models import LoadingParams, UploadResponse, DatasetTokenHeader, InfoResponse, ExportParams


@bp.route("/datasets", methods=["POST"])
@spec.validate(
    body=LoadingParams,
    resp=Response(HTTP_200=UploadResponse),
    tags=["Upload dataset"]
)
def upload_file() -> Response:
    file = request.files.get('file')
    if file is None or file.filename == '':
        raise ParameterMissing("file")

    params = request.context.body  # noqa

    data = DataFrameLoader(file, params).load_data()
    dataset_id, access_key = storage.save_dataset(data)

    response_data = UploadResponse(
        message="Dataset uploaded successfully",
        dataset_id=dataset_id,
        access_key=access_key,
        next_step=url_for("preprocessing.preprocess_dataset", dataset_id=dataset_id),
        metadata=DataFrameAnalyzer.get_metadata(data)
    )

    return jsonify(response_data.dict())


@bp.route("/datasets/<dataset_id>")
@spec.validate(
    headers=DatasetTokenHeader,
    resp=Response(HTTP_200=InfoResponse),
    tags=["Dataset info"]
)
def get_info(dataset_id: str) -> Response:
    data = storage.get_dataset(dataset_id)

    response_data = InfoResponse(
        message="Dataset found successfully",
        dataset_id=dataset_id,
        next_step=url_for("preprocessing.preprocess_dataset", dataset_id=dataset_id),
        metadata=DataFrameAnalyzer.get_metadata(data)
    )

    return jsonify(response_data.dict())


@bp.route("/datasets/<dataset_id>/download")
@spec.validate(
    query=ExportParams,
    headers=DatasetTokenHeader,
    resp=Response('HTTP_200'),
    tags=["Download dataset"]
)
def download_dataset(dataset_id: str) -> Response:
    params: ExportParams = request.context.query  # noqa
    data = storage.get_dataset(dataset_id)

    buffer = BytesIO()
    params.method(data, buffer)
    buffer.seek(0)
    return send_file(buffer, mimetype=params.mimetype, as_attachment=False, download_name=f'{dataset_id}.{params.ext}')
