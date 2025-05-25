from flask import send_file, request
from flask_pydantic_spec import FileResponse

from app.controllers import DataFrameAnalyzer
from app.extensions import storage
from app.reporting import bp
from app.extensions import spec
from app.models import AnalysisParams, DatasetTokenHeader


@bp.route("/datasets/<dataset_id>/report")
@spec.validate(
    query=AnalysisParams,
    headers=DatasetTokenHeader,
    resp=FileResponse(content_type='application/pdf'),
    tags=["Recommendations report"]
)
def get_recommendations(dataset_id: str) -> FileResponse:
    params: AnalysisParams = request.context.query  # noqa
    data = storage.get_dataset(dataset_id)

    report = DataFrameAnalyzer(data).generate_report(params)
    return send_file(report.to_bytes(), mimetype='application/pdf', as_attachment=False, download_name='report.pdf')
