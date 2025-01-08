import pandas as pd
from flask import Flask, request, render_template, send_file, Response
from werkzeug.datastructures import FileStorage
from io import BytesIO
import error_handlers as eh
from services.data_processing import process_data
from services.data_analysis import analyze_data
from services.report_generation import generate_report

app: Flask = Flask(__name__)
app.register_error_handler(KeyError, eh.missing_parameter)
app.register_error_handler(ValueError, eh.incorrect_parameter)


@app.route("/")
def home() -> str:
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def upload_file() -> Response:
    file: FileStorage = request.files['file']
    params: dict = request.form.to_dict()
    processed_data: pd.DataFrame = process_data(file, params)
    analysis_results: dict = analyze_data(processed_data)
    pdf_buffer: BytesIO = generate_report(analysis_results)
    # TODO: analyze and optimize performance
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=False, download_name='report.pdf')


if __name__ == "__main__":
    app.run(debug=True)
