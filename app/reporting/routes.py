from flask import send_file, Response, request

from app.controllers import get_data_report
from app.extensions import storage
from app.reporting import bp


@bp.route("/recommendations/<dataset_id>")
def get_recommendations(dataset_id: str) -> Response:
    data = storage.get_dataset(dataset_id)
    params = request.args.to_dict()
    pdf_buffer = get_data_report(data, params)
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=False, download_name='report.pdf')
