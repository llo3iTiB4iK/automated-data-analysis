from flask import request, send_file, jsonify, Response
from flask_pydantic_spec import FileResponse, MultipartFormRequest

from app.controllers import DataFrameLoader, DataFramePreprocessor, DataFrameAnalyzer
from app.extensions import spec
from app.system import bp
from app.models import FullPipelineParams
from app.errors import ParameterMissing


@bp.route("/")
def index() -> Response:
    ui_set = spec.config._SUPPORT_UI | {spec.config.FILENAME}  # noqa
    base_url = request.host_url.rstrip("/")
    return jsonify({
        "message": "Welcome to the Automated Data Analysis Web Service",
        "documentation": {ui: f"{base_url}/{spec.config.PATH}/{ui}" for ui in ui_set}
    })


@bp.route("/datasets/full_pipeline", methods=["POST"])
@spec.validate(
    body=MultipartFormRequest(model=FullPipelineParams),
    resp=FileResponse(content_type='application/pdf'),
    tags=["Full pipeline"]
)
def analyze_data() -> FileResponse:
    file = request.files.get('file')
    if file is None or file.filename == '':
        raise ParameterMissing("file")

    params: FullPipelineParams = request.context.body  # noqa

    data = DataFrameLoader(file, params).load_data()
    data = DataFramePreprocessor(data).preprocess(params)
    report = DataFrameAnalyzer(data).generate_report(params)
    return send_file(report.to_bytes(), mimetype='application/pdf', as_attachment=False, download_name='report.pdf')
