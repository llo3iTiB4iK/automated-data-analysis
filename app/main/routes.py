from flask import request, send_file, Response

from app.controllers import load_data, process_data, get_data_report
from app.main import bp


@bp.route("/all_stages", methods=["POST"])
def analyze_data() -> Response:
    file = request.files['file']
    params = request.form.to_dict()
    data = load_data(file, params)
    data = process_data(data, params)
    pdf_buffer = get_data_report(data, params)
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=False, download_name='report.pdf')
