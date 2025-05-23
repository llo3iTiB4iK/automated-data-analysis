from flask import request, send_file
from flask_pydantic_spec import Response

from app.controllers import DataFrameLoader, DataFramePreprocessor, DataFrameAnalyzer
from app.extensions import spec
from app.main import bp
from app.models import FullPipelineParams
from app.errors import ParameterMissing


@bp.route("/datasets/full_pipeline", methods=["POST"])
@spec.validate(
    body=FullPipelineParams,
    resp=Response('HTTP_200'),
    tags=["Full pipeline"]
)
def analyze_data() -> Response:
    file = request.files.get('file')
    if file is None or file.filename == '':
        raise ParameterMissing("file")
    params: FullPipelineParams = request.context.body  # noqa

    data = DataFrameLoader(file, params).load_data()
    data = DataFramePreprocessor(data).preprocess(params)
    report = DataFrameAnalyzer(data).fill_report(params)
    return send_file(report.to_bytes(), mimetype='application/pdf', as_attachment=False, download_name='report.pdf')
