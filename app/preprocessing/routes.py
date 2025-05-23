from flask import request, url_for, jsonify
from flask_pydantic_spec import Response

from app.controllers import DataFramePreprocessor, DataFrameAnalyzer
from app.extensions import storage, spec
from app.models import PreprocessingParams, PreprocessingResponse, DatasetTokenHeader
from app.preprocessing import bp


@bp.route("/datasets/<dataset_id>/preprocess", methods=["POST"])
@spec.validate(
    body=PreprocessingParams,
    headers=DatasetTokenHeader,
    resp=Response(HTTP_200=PreprocessingResponse),
    tags=["Preprocessing"]
)
def preprocess_dataset(dataset_id: str) -> Response:
    params: PreprocessingParams = request.context.body  # noqa
    data = storage.get_dataset(dataset_id)

    preprocessor = DataFramePreprocessor(data)
    data = preprocessor.preprocess(params)

    new_dataset_id, new_access_key = storage.save_dataset(data, None if params.make_copy else dataset_id)

    response_data = PreprocessingResponse(
        message="Dataset preprocessed successfully",
        dataset_id=dataset_id,
        next_step=url_for("reporting.get_recommendations", dataset_id=dataset_id),
        metadata=DataFrameAnalyzer.get_metadata(data),
        new_dataset_id=new_dataset_id if params.make_copy else None,
        new_dataset_access_key=new_access_key if params.make_copy else None
    )

    return jsonify(response_data.dict(exclude_none=True))
